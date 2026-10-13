"""Generation runners preserving B0/C1/C2 inference contracts.

Recovery differs from the original external scripts: an exclusive run lock,
input/code identity header and durable dispatch journal guard every paid run.
Unknown or failed dispatches require investigation, never automatic replay.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import importlib
import json
import os
import random
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# ---------------------------------------------------------------------------
# Port of run_live_v2.py (round-1 experiment runner)
# ---------------------------------------------------------------------------
def _run_identity(corpus_path, casefile, freeze_file, arms, model):
    """Compute a run identity header from input file hashes and config."""
    def _sha(p):
        if p is None or not Path(p).exists():
            return None
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return {
        "corpus_sha256": _sha(corpus_path),
        "questions_sha256": _sha(casefile),
        "freeze_sha256": _sha(freeze_file),
        "arms": sorted(arms),
        "model": model,
        "implementation_sha256": {str(p.relative_to(_REPO)): _sha(p)
            for directory in ("newdomain", "pipeline", "index", "eval/optimization")
            for p in sorted((_REPO / directory).rglob("*.py"))},
    }


def _verify_or_write_header(header_path, current, resume):
    """The caller holds the run lock throughout validation and dispatch."""
    if resume:
        if not header_path.exists():
            raise RuntimeError("Cannot resume: no run header")
        saved = json.loads(header_path.read_text(encoding="utf-8"))
        if saved != current:
            changed = sorted(k for k in set(saved) | set(current) if saved.get(k) != current.get(k))
            raise RuntimeError(f"Run identity changed on resume: {changed}")
        return saved
    with header_path.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(current, indent=1) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return current


def _reconcile_resume(journal, out_file, expected=None, expected_model=None):
    """Validate the entire run before any worker can dispatch.

    Completed, hash-pinned results are reusable. Unknown/in-flight/failed jobs,
    missing hashes, orphan rows and changed identities require investigation.
    """
    journal._require_lock()
    if not out_file.exists():
        raise RuntimeError("Cannot resume: results file missing")
    rows = {}
    for line in out_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise RuntimeError("result must be an object")
        key = (row.get("qid"), row.get("arm"))
        if not all(isinstance(v, str) and v for v in key) or key in rows:
            raise RuntimeError("invalid or duplicate result identity")
        rows[key] = (row, line.strip())
    seen = set()
    for entry_key, entry in journal._entries.items():
        qid, arm, prompt, model = entry_key.split("|")
        key = (qid, arm)
        if expected_model is not None and model != expected_model:
            raise RuntimeError("journal model identity mismatch")
        if key in seen or (expected is not None and key not in expected):
            raise RuntimeError("unknown or duplicate journal job")
        seen.add(key)
        if entry.get("status") != "terminal" or entry.get("success") is not True:
            raise RuntimeError("unresolved or failed dispatch; manual investigation required")
        if key not in rows:
            raise RuntimeError("journal succeeded but result missing")
        row, raw = rows[key]
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if entry.get("result_sha256") != digest:
            raise RuntimeError("result hash missing or mismatch")
        if row.get("prompt_sha256") != prompt:
            raise RuntimeError("result prompt identity mismatch")
    if set(rows) != seen:
        raise RuntimeError("result has no corresponding completed dispatch")


def _validate_jobs(cases, arms):
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a nonempty list")
    if not arms or len(set(arms)) != len(arms):
        raise ValueError("arms must be nonempty and unique")
    keys = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("question"), str):
            raise ValueError("invalid question")
        qid = case.get("qid")
        if not isinstance(qid, str) or not qid or "|" in qid or qid in keys:
            raise ValueError("invalid or duplicate question identity")
        keys.add(qid)
    return {(qid, arm) for qid in keys for arm in arms}


def run_live_v2(stage, arms, revision, repeat=0, dataset=None,
                output_dir: Path = None, casefile: Path = None,
                corpus_path: Path = None, freeze_file: Path = None,
                live_context=None, resume=False, _journal=None):
    """Behavior-preserving port of run_live_v2.run().

    New parameters (output_dir, casefile, corpus_path, freeze_file) supply the
    paths that the original hardcoded from its task folder.
    """
    from newdomain import baseline as baseline_mod
    from newdomain.transport import LiveAuthorizationError, chat
    from eval.optimization.transports import TransportError

    if live_context is None:
        raise LiveAuthorizationError(
            "run_live_v2 requires explicit live_context; "
            "construct via CLI --live or pass a LiveContext for testing")
    ctx = live_context
    journal = _journal
    P = output_dir

    if stage == "final":
        f = json.loads(freeze_file.read_text())
        for path, h in f["hashes"].items():
            got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            if got != h:
                raise RuntimeError(f"Freeze hash mismatch: {path} expected {h[:16]}… got {got[:16]}…")

    cases = json.loads(casefile.read_text())
    _validate_jobs(cases, arms)
    adapters = {}
    init = {}
    for arm in arms:
        t = time.perf_counter()
        if arm == "B0":
            mod = baseline_mod
            index = mod.NewDomainBaseline(mod.build_chunks(mod.load_units(corpus_path)))
        else:
            mod = importlib.import_module("newdomain.clauses" if arm == "C3B" else "newdomain.candidate")
            index = mod.create_index(documents_path=corpus_path)
        adapters[arm] = (mod, index)
        init[arm] = {"initialization_s": time.perf_counter() - t, "chunks": len(index.chunks)}

    out = P / f"{stage}-{revision}-results.jsonl"

    from newdomain.journal import JournalError

    if not resume:
        (P / f"{stage}-{revision}-initialization.json").write_text(json.dumps(
        {"arms": arms, "repeat": repeat, "case_count": len(cases),
         "initializations": init,
         "clock": "worker_start through final validation, excludes shared init and result persistence",
         "case_sha256": hashlib.sha256(casefile.read_bytes()).hexdigest(),
         "resume": resume}, indent=2) + "\n")

    jobs = [(c, a) for c in cases for a in arms]
    random.Random(20261012 + repeat).shuffle(jobs)
    lock = threading.Lock()
    stop = threading.Event()

    def work(job):
        if stop.is_set():
            return
        c, a = job
        mod, index = adapters[a]
        start = time.perf_counter()
        r = {"qid": c["qid"], "arm": a, "repeat": repeat, "stage": stage,
             "revision": revision, "dataset": casefile.name,
             "question": c["question"], "group": c.get("group", c["qid"]),
             "origin": c.get("origin", c.get("kind", "")), "live": True, "complete": False}
        row_written = False
        skipped = False
        dispatched = False
        try:
            if c.get("fixed_context"):
                results = [{"id": i, "text": t, "title": "固定回归资料", "locator": "regression"}
                           for i, t in c["fixed_context"].items()]
                rt = {"results": results, "elapsed_ms": 0, "fixed_regression_context": True}
            else:
                rt = index.retrieval(c["question"], k=8)
                results = rt["results"]
            r["retrieval"] = rt
            r["context"] = {x["id"]: x["text"] for x in results}
            messages = mod.build_messages(c["question"], results, mode=a)
            r["prompt_sha256"] = hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()
            resume = journal.check_resume(c["qid"], a, r["prompt_sha256"], "deepseek-flash")
            if resume == "skip":
                skipped = True
                return
            if resume == "fail":
                raise JournalError(f"prior failed dispatch for ({c['qid']}, {a}); not auto-retried")
            journal.record_started(c["qid"], a, r["prompt_sha256"], "deepseek-flash")
            dispatched = True
            response = chat(ctx, messages)
            r["raw_response"] = response
            if response.get("usage") is None:
                journal.record_terminal(c["qid"], a, r["prompt_sha256"], "deepseek-flash",
                                         success=False, error="usage missing")
                raise TransportError("usage missing")
            if not (response.get("stream_done") and response.get("finish_reason") == "stop"):
                journal.record_terminal(c["qid"], a, r["prompt_sha256"], "deepseek-flash",
                                         success=False, error="incomplete response")
                raise TransportError("incomplete response")
            if a != "B0" and hasattr(mod, "canonicalize"):
                response, transform = mod.canonicalize(response, r["context"])
                r["transformations"] = transform
            r["response"] = response
            gate = mod.validate(response, r["context"])
            if a != "B0" and not r.get("transformations", {}).get("ok"):
                gate["ok"] = False
                gate["failure"] = "candidate_protocol_rejected: " + str(r.get("transformations", {}).get("errors"))
            r["gate"] = {k: v for k, v in gate.items() if k != "raw"}
            r["complete"] = True
            try:
                parsed = json.loads(response["content"])
                r["answer"] = parsed if isinstance(parsed, dict) else None
            except (TypeError, ValueError):
                r["answer"] = None
            r["valid"] = gate["ok"]
            r["abstention"] = isinstance(r.get("answer"), dict) and bool(r["answer"].get("sentences")) and all(not s.get("citations") for s in r["answer"].get("sentences", []))
            r["full_ms"] = (time.perf_counter() - start) * 1000
            row_json = json.dumps(r, ensure_ascii=False)
            row_sha = hashlib.sha256(row_json.encode("utf-8")).hexdigest()
            with lock:
                with out.open("a") as f:
                    f.write(row_json + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                row_written = True
            journal.record_terminal(c["qid"], a, r["prompt_sha256"], "deepseek-flash",
                                     success=True, result_sha256=row_sha)
        except Exception as e:
            r["error"] = type(e).__name__ + ": " + str(e)
            r["full_ms"] = (time.perf_counter() - start) * 1000
            if dispatched and not row_written:
                try:
                    journal.record_terminal(c["qid"], a, r.get("prompt_sha256", ""),
                                             "deepseek-flash", success=False,
                                             error=str(e)[:100])
                except Exception:
                    pass
            stop.set()
        finally:
            if not row_written and not skipped:
                with lock:
                    with out.open("a") as f:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        f.flush()
                        os.fsync(f.fileno())
            if not skipped:
                print(json.dumps({"qid": r["qid"], "arm": a, "valid": r.get("valid"),
                                   "error": r.get("error"), "full_ms": r.get("full_ms", 0)},
                                  ensure_ascii=False), flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, jobs))
    print(json.dumps({"terminal": True, "stopped": stop.is_set(), "totals": ctx.ledger.snapshot()["totals"]}))
    if stop.is_set():
        raise RuntimeError("generation stopped after an unresolved failure; inspect saved results")


# ---------------------------------------------------------------------------
# Port of run_cycle2.py (cycle-2 experiment runner)
# ---------------------------------------------------------------------------
def run_cycle2(stage, arms, revision, dataset=None,
               output_dir: Path = None, casefile: Path = None,
               corpus_path: Path = None, freeze_file: Path = None, live_context=None,
               resume=False, _journal=None):
    """Behavior-preserving port of run_cycle2.run()."""
    from newdomain.transport import LiveAuthorizationError, chat
    from eval.optimization.transports import TransportError

    if live_context is None:
        raise LiveAuthorizationError(
            "run_cycle2 requires explicit live_context")
    ctx = live_context
    journal = _journal
    P = output_dir
    if stage == "final":
        freeze = json.loads(freeze_file.read_text())
        for path, h in freeze["hashes"].items():
            got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            if got != h:
                raise RuntimeError(f"Freeze hash mismatch: {path} expected {h[:16]}… got {got[:16]}…")

    cases = json.loads(casefile.read_text())
    _validate_jobs(cases, arms)
    out = P / f"{stage}-{revision}-results.jsonl"
    adapters = {}
    init = {}
    for arm in arms:
        t = time.perf_counter()
        if arm == "C1":
            mod = importlib.import_module("newdomain.candidate")
            index = mod.create_index(documents_path=corpus_path)
        else:
            mod = importlib.import_module("newdomain.cycle2")
            index = mod.create_index(mode=arm, documents_path=corpus_path)
        adapters[arm] = (mod, index)
        init[arm] = {"seconds": time.perf_counter() - t, "chunks": len(index.chunks)}

    if not resume:
        (P / f"{stage}-{revision}-initialization.json").write_text(json.dumps(
        {"case_n": len(cases), "arms": arms, "initializations": init,
         "case_sha256": hashlib.sha256(casefile.read_bytes()).hexdigest(),
         "clock": "Worker start through validation; excludes queue, initialization and persistence."},
        indent=2) + "\n")

    jobs = [(c, a) for c in cases for a in arms]
    random.Random(2026101202).shuffle(jobs)
    stop = threading.Event()
    from newdomain.journal import JournalError
    lock = threading.Lock()

    def work(job):
        if stop.is_set():
            return
        c, a = job
        mod, index = adapters[a]
        start = time.perf_counter()
        r = {"qid": c["qid"], "question": c["question"], "arm": a, "stage": stage,
             "revision": revision, "dataset": casefile.name,
             "group": c.get("group", c["qid"]),
             "origin": c.get("origin", c.get("kind", "")), "live": True, "complete": False}
        row_written = False
        skipped = False
        dispatched = False
        try:
            if c.get("fixed_context"):
                rt = {"results": [{"id": i, "text": t, "title": "固定回归资料", "locator": "regression"}
                                   for i, t in c["fixed_context"].items()],
                      "elapsed_ms": 0, "fixed_regression_context": True}
            else:
                rt = index.retrieval(c["question"], k=8)
            rs = rt["results"]
            r["retrieval"] = rt
            r["context"] = {x["id"]: x["text"] for x in rs}
            messages = mod.build_messages(c["question"], rs, mode=a)
            r["prompt_sha256"] = hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()
            resume = journal.check_resume(c["qid"], a, r["prompt_sha256"], "deepseek-flash")
            if resume == "skip":
                skipped = True
                return
            if resume == "fail":
                raise JournalError(f"prior failed dispatch for ({c['qid']}, {a})")
            journal.record_started(c["qid"], a, r["prompt_sha256"], "deepseek-flash")
            dispatched = True
            response = chat(ctx, messages)
            r["raw_response"] = response
            if not (response.get("stream_done") and response.get("finish_reason") == "stop" and response.get("usage") is not None):
                journal.record_terminal(c["qid"], a, r["prompt_sha256"], "deepseek-flash",
                                         success=False, error="incomplete generation")
                raise TransportError("incomplete generation")
            response, transform_meta = mod.canonicalize(response, r["context"])
            r["transformations"] = transform_meta
            r["response"] = response
            gate = mod.validate(response, r["context"])
            if not transform_meta.get("ok"):
                gate["ok"] = False
                gate["failure"] = "candidate_protocol_rejected: " + str(transform_meta.get("errors"))
            r["gate"] = {k: v for k, v in gate.items() if k != "raw"}
            r["complete"] = True
            r["valid"] = bool(gate["ok"])
            try:
                parsed = json.loads(response["content"])
                r["answer"] = parsed if isinstance(parsed, dict) else None
            except (ValueError, TypeError):
                r["answer"] = None
            r["abstention"] = isinstance(r.get("answer"), dict) and bool(r["answer"].get("sentences")) and all(not s.get("citations") for s in r["answer"]["sentences"])
            r["full_ms"] = (time.perf_counter() - start) * 1000
            row_json = json.dumps(r, ensure_ascii=False)
            row_sha = hashlib.sha256(row_json.encode("utf-8")).hexdigest()
            with lock:
                with out.open("a") as f:
                    f.write(row_json + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                row_written = True
            journal.record_terminal(c["qid"], a, r["prompt_sha256"], "deepseek-flash",
                                     success=True, result_sha256=row_sha)
        except Exception as e:
            r["error"] = type(e).__name__ + ": " + str(e)
            if dispatched and not row_written:
                try:
                    journal.record_terminal(c["qid"], a, r.get("prompt_sha256", ""),
                                             "deepseek-flash", success=False,
                                             error=str(e)[:100])
                except Exception:
                    pass
            stop.set()
        finally:
            r["full_ms"] = (time.perf_counter() - start) * 1000
            if not row_written and not skipped:
                with lock:
                    with out.open("a") as f:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        f.flush()
                        os.fsync(f.fileno())
            if not skipped:
                print(json.dumps({"qid": c["qid"], "arm": a, "valid": r.get("valid"),
                                   "error": r.get("error")}), flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, jobs))
    print(json.dumps({"terminal": True, "stopped": stop.is_set(), "totals": ctx.ledger.snapshot()["totals"]}))
    if stop.is_set():
        raise RuntimeError("generation stopped after an unresolved failure; inspect saved results")


def _guard_run(function):
    import functools
    import inspect
    from newdomain.journal import DispatchJournal

    @functools.wraps(function)
    def guarded(*args, **kwargs):
        bound = inspect.signature(function).bind(*args, **kwargs)
        bound.apply_defaults()
        p = bound.arguments
        if p["live_context"] is None:
            from newdomain.transport import LiveAuthorizationError
            raise LiveAuthorizationError("explicit live_context required")
        if p.get("_journal") is not None:
            raise ValueError("journal is managed by the runner")
        stage, revision = p["stage"], p["revision"]
        if stage not in ("dev", "final") or not isinstance(revision, str) or not revision or any(c in revision for c in "/\\"):
            raise ValueError("invalid run name or stage")
        allowed = {"B0", "C1", "C3B"} if function.__name__ == "run_live_v2" else {"C1", "C2P", "C2R"}
        if not set(p["arms"]) <= allowed:
            raise ValueError("unsupported arm")
        cases = json.loads(Path(p["casefile"]).read_text())
        expected = _validate_jobs(cases, p["arms"])
        from newdomain.paths import _ensure_outside_repo
        for field in ("corpus_path", "casefile", "output_dir", "freeze_file"):
            if p.get(field) is not None:
                _ensure_outside_repo(Path(p[field]), field)
        root = Path(p["output_dir"])
        out = root / f"{stage}-{revision}-results.jsonl"
        header = root / f"{stage}-{revision}-header.json"
        identity = _run_identity(p["corpus_path"], p["casefile"], p["freeze_file"], p["arms"], "deepseek-flash")
        identity.update(runner=function.__name__, stage=stage, revision=revision, repeat=p.get("repeat", 0))
        with DispatchJournal(root / f"{stage}-{revision}-journal.jsonl") as journal:
            if not p["resume"] and (out.exists() or journal.path.exists()):
                raise FileExistsError("run results or journal already exist")
            _verify_or_write_header(header, identity, p["resume"])
            if p["resume"]:
                _reconcile_resume(journal, out, expected, "deepseek-flash")
            else:
                with out.open("x", encoding="utf-8") as fh:
                    fh.flush()
                    os.fsync(fh.fileno())
            p["_journal"] = journal
            return function(*bound.args, **bound.kwargs)
    return guarded


run_live_v2 = _guard_run(run_live_v2)
run_cycle2 = _guard_run(run_cycle2)
