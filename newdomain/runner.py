"""Offline CLI for the new-domain evaluation pipeline.

Commands:
  replay    — re-validate saved generation results against the pipeline gate
  summarize — validity/latency/usage summary from saved results
  prepare   — offline retrieval + prompt preparation for a corpus/questions set
  help      — show usage and current path configuration

All commands are OFFLINE: no API calls, no credential reads, no network.
Paid generation/judging is in newdomain/generation.py (disabled during consolidation).

Usage:
  .venv/bin/python -m newdomain.runner replay --results <path> [--arm C2P]
  .venv/bin/python -m newdomain.runner summarize --results <path>
  .venv/bin/python -m newdomain.runner prepare --corpus <jsonl> --questions <json> --output <dir> --mode C2P
  .venv/bin/python -m newdomain.runner help
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np

from newdomain.paths import PATHS, MissingDataPath, _ensure_outside_repo, _ensure_parent_for_output


# ---------------------------------------------------------------------------
# Loading / validation
# ---------------------------------------------------------------------------
def load_results(results_path: Path) -> List[Dict[str, Any]]:
    """Load saved results JSONL; reject duplicate (qid, arm) pairs."""
    rows = []
    seen = set()
    with open(results_path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"results line {line_no}: invalid JSON: {e}") from e
            key = (row.get("qid"), row.get("arm"))
            if key in seen:
                raise ValueError(
                    f"results line {line_no}: duplicate (qid={key[0]}, arm={key[1]}) — "
                    "saved results must be unique per question×arm")
            seen.add(key)
            rows.append(row)
    return rows


def _resolve_canonical_response(row: Dict[str, Any]) -> Tuple[Any, Optional[Dict], str]:
    """Return (canonical_response, canonicalize_meta, mode_note).

    Starts from raw_response when present (the original runner's behavior),
    canonicalizes ONCE for C1/C2 arms, and enforces meta.ok.
    For rows that only carry a canonical response (no raw), validates the
    canonical form directly — noted as 'canonical_only' mode.
    """
    arm = row.get("arm", "")
    context = row.get("context") or {}

    raw = row.get("raw_response")
    canonical = row.get("response")

    if raw is not None:
        if arm == "C1":
            from newdomain import candidate as c1_mod
            response, meta = c1_mod.canonicalize(raw, context)
            if not meta.get("ok"):
                return response, meta, "canonicalize_rejected"
            return response, meta, "raw_replayed"
        elif arm in ("C2P", "C2R"):
            from newdomain import cycle2 as c2_mod
            response, meta = c2_mod.canonicalize(raw, context)
            if not meta.get("ok"):
                return response, meta, "canonicalize_rejected"
            return response, meta, "raw_replayed"
        elif arm == "B0":
            from newdomain import baseline as b0_mod
            return raw, None, "b0_raw"
        else:
            return raw, None, f"unknown_arm:{arm}"
    elif canonical is not None:
        return canonical, None, "canonical_only"
    else:
        return None, None, "no_response"


def validate_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Re-validate a saved row: raw → canonicalize → gate.

    Returns a report dict with ok/failure/mode. The 'mode' field preserves
    raw_replayed / canonical_only / canonicalize_rejected / b0_raw distinction.
    B0 rows are validated with the baseline module directly.
    """
    arm = row.get("arm", "")
    context = row.get("context") or {}

    response, meta, mode_note = _resolve_canonical_response(row)

    if response is None:
        return {"ok": False, "failure": "no_response", "mode": mode_note, "raw": row}

    if meta is not None and not meta.get("ok"):
        return {"ok": False,
                "failure": "candidate_protocol_rejected:" + str(meta.get("errors", [])),
                "mode": mode_note, "raw": row}

    if arm == "B0":
        from newdomain import baseline as b0_mod
        gate = b0_mod.validate(response, context)
    elif arm == "C1":
        from newdomain import candidate as c1_mod
        gate = c1_mod.validate(response, context)
    elif arm in ("C2P", "C2R"):
        from newdomain import cycle2 as c2_mod
        gate = c2_mod.validate(response, context)
    else:
        return {"ok": False, "failure": f"unknown_arm:{arm}", "mode": mode_note, "raw": row}

    # Preserve the mode note on the gate result
    gate = dict(gate)
    gate["mode"] = mode_note
    return gate


# ---------------------------------------------------------------------------
# CLI path safety
# ---------------------------------------------------------------------------
def _check_cli_input_path(path_str: str, what: str) -> Path:
    """Validate a CLI-supplied input path exists and is outside the repo."""
    p = Path(path_str)
    if not p.exists():
        print(f"ERROR: {what} not found: {p}", file=sys.stderr)
        raise SystemExit(2)
    try:
        return _ensure_outside_repo(p, what)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)


def _check_cli_output_dir(dir_str: str, filename: str) -> Path:
    """Validate an output directory is outside the repo and the target file
    does not already exist (no overwrite)."""
    out_dir = Path(dir_str)
    out_file = out_dir / filename
    try:
        resolved = _ensure_parent_for_output(out_file, "Output")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
    if resolved.exists():
        print(f"ERROR: output file already exists (refusing to overwrite): {resolved}",
              file=sys.stderr)
        raise SystemExit(2)
    return resolved


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------
def _load_judge_scores(judge_path: Path,
                        generation_rows: List[Dict]) -> Optional[Dict]:
    """Load saved judge results keyed by (qid, arm); validate coverage against
    the supplied generation rows. Returns None if no judge file.

    The judge file format has entries like:
      {"qid": "...", "mapping": {"A": "C1", "B": "C2P"}, "scores": {"C1": {...}}}
    We extract per-(qid, arm) scores and cross-reference generation rows.
    """
    if judge_path is None:
        return None
    gen_keys = {(r.get("qid"), r.get("arm")) for r in generation_rows}
    scores_by_key = {}
    orphans = []
    with open(judge_path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            entry = json.loads(line)
            qid = entry.get("qid")
            mapping = entry.get("mapping") or {}
            entry_scores = entry.get("scores") or {}
            for label, arm in mapping.items():
                key = (qid, arm)
                if key in scores_by_key:
                    raise ValueError(
                        f"judge results: duplicate (qid={qid}, arm={arm})")
                sc = entry_scores.get(arm)
                if sc is None:
                    continue
                if key not in gen_keys:
                    orphans.append({"qid": qid, "arm": arm,
                                     "reason": "no matching generation row"})
                scores_by_key[key] = sc
    return {"by_key": scores_by_key, "orphans": orphans}


def _judge_arm_summary(judge_data: Optional[Dict],
                        arm_rows: List[Dict]) -> Optional[Dict]:
    """Per-arm saved judge adequacy summary from loaded judge data."""
    if judge_data is None:
        return None
    arm = arm_rows[0].get("arm", "?") if arm_rows else "?"
    adequate_count = 0
    semantic_adequate_count = 0
    scored_count = 0
    for row in arm_rows:
        key = (row.get("qid"), row.get("arm"))
        sc = judge_data["by_key"].get(key)
        if sc is None:
            continue
        scored_count += 1
        if sc.get("adequate"):
            adequate_count += 1
        if sc.get("semantic_adequate"):
            semantic_adequate_count += 1
    return {
        "arm": arm,
        "scored": scored_count,
        "adequate": adequate_count,
        "semantic_adequate": semantic_adequate_count,
    }


def cmd_replay(args) -> int:
    """Offline replay: re-validate saved results, report counts and mismatches."""
    results_path = _check_cli_input_path(args.results, "Results file")
    rows = load_results(results_path)
    arm_filter = args.arm

    judge_data = None
    if getattr(args, "judge_results", None):
        judge_path = _check_cli_input_path(args.judge_results, "Judge results file")
        judge_data = _load_judge_scores(judge_path, rows)

    stats = {"total": 0, "valid": 0, "invalid": 0, "mode_notes": Counter(),
             "failures": Counter(), "saved_valid_mismatches": []}
    for row in rows:
        if arm_filter and row.get("arm") != arm_filter:
            continue
        stats["total"] += 1
        gate = validate_row(row)
        mode = gate.get("mode", "")
        stats["mode_notes"][mode] += 1

        recomputed_ok = bool(gate.get("ok"))
        saved_ok = bool(row.get("valid"))
        if recomputed_ok != saved_ok:
            stats["saved_valid_mismatches"].append({
                "qid": row.get("qid"), "arm": row.get("arm"),
                "saved_valid": saved_ok, "recomputed_valid": recomputed_ok,
                "failure": gate.get("failure")})

        if recomputed_ok:
            stats["valid"] += 1
        else:
            stats["invalid"] += 1
            fail = str(gate.get("failure", "unknown"))[:120]
            stats["failures"][fail] += 1

    output = {
        "command": "replay",
        "results_file": str(results_path),
        "arm_filter": arm_filter,
        "total": stats["total"],
        "recomputed_valid": stats["valid"],
        "recomputed_invalid": stats["invalid"],
        "saved_validity_mismatches": stats["saved_valid_mismatches"],
        "failure_categories": dict(stats["failures"].most_common()),
        "mode_notes": dict(stats["mode_notes"].most_common()),
    }

    if judge_data is not None:
        by_arm: Dict[str, List[Dict]] = {}
        for row in rows:
            if arm_filter and row.get("arm") != arm_filter:
                continue
            by_arm.setdefault(row.get("arm", "?"), []).append(row)
        judge_summary = {}
        for arm, arm_rows in sorted(by_arm.items()):
            s = _judge_arm_summary(judge_data, arm_rows)
            if s:
                judge_summary[arm] = s
        output["saved_judge"] = {
            "note": "saved judge scores from a separate file, NOT recomputed; "
                     "keyed by (qid, arm) matched against generation rows",
            "per_arm": judge_summary,
        }
        if judge_data["orphans"]:
            output["saved_judge"]["orphan_entries"] = judge_data["orphans"]

    print(json.dumps(output, ensure_ascii=False, indent=1))
    return 0


def cmd_summarize(args) -> int:
    """Offline summary using numpy.percentile/median (same formula as frozen reports).

    Distinguishes saved generation validity from any recomputed values.
    Does NOT re-run judge scoring — saved judge metrics come from a separate file.
    """
    results_path = _check_cli_input_path(args.results, "Results file")
    rows = load_results(results_path)

    by_arm: Dict[str, List[Dict]] = {}
    for row in rows:
        arm = row.get("arm", "?")
        by_arm.setdefault(arm, []).append(row)

    # Saved judge scores from separate file (keyed by qid×arm, per-arm adequacy)
    judge_data = None
    if getattr(args, "judge_results", None):
        judge_path = _check_cli_input_path(args.judge_results, "Judge results file")
        judge_data = _load_judge_scores(judge_path, rows)

    summary = {}
    for arm, arm_rows in sorted(by_arm.items()):
        n = len(arm_rows)
        saved_valid = sum(1 for r in arm_rows if r.get("valid"))
        saved_complete = sum(1 for r in arm_rows if r.get("complete"))
        saved_abstention = sum(1 for r in arm_rows if r.get("abstention"))
        # saved_abstention counts ALL rows with the flag, including mechanically
        # invalid outputs; report valid-only fully-uncited separately for clarity
        valid_abstention = sum(1 for r in arm_rows
                                if r.get("abstention") and r.get("valid"))

        full_ms = sorted(r.get("full_ms", 0) for r in arm_rows
                         if r.get("full_ms") is not None)
        ms = np.array(full_ms) if full_ms else np.array([0.0])
        p50 = float(np.median(ms)) if full_ms else None
        p95 = float(np.percentile(ms, 95)) if full_ms else None

        tokens_in = [((r.get("raw_response") or r.get("response") or {})
                      .get("usage") or {}).get("input_tokens", 0) for r in arm_rows]
        tokens_out = [((r.get("raw_response") or r.get("response") or {})
                       .get("usage") or {}).get("output_tokens", 0) for r in arm_rows]

        arm_summary = {
            "n": n,
            "saved_valid": saved_valid,
            "saved_complete": saved_complete,
            "saved_abstention": saved_abstention,
            "saved_abstention_note": "unfiltered: includes mechanically invalid outputs",
            "valid_abstention": valid_abstention,
            "p50_ms": round(p50, 1) if p50 is not None else None,
            "p95_ms": round(p95, 1) if p95 is not None else None,
            "total_input_tokens": sum(tokens_in),
            "total_output_tokens": sum(tokens_out),
        }

        if judge_data is not None:
            js = _judge_arm_summary(judge_data, arm_rows)
            if js:
                arm_summary["saved_judge"] = js

        summary[arm] = arm_summary

    print(json.dumps({"command": "summarize",
                       "results_file": str(results_path),
                       "by_arm": summary}, ensure_ascii=False, indent=1))
    return 0


def cmd_prepare(args) -> int:
    """Offline retrieval + prompt preparation for a corpus/questions set.

    Produces per-question retrieval results and ready-to-send prompts.
    No generation, no API calls — pure local compute.
    Output file is created exclusively ('x' mode); existing files are rejected.
    """
    corpus_path = _check_cli_input_path(args.corpus, "Corpus file")
    questions_path = _check_cli_input_path(args.questions, "Questions file")
    out_path = _check_cli_output_dir(args.output, "prepare.jsonl")

    from newdomain import baseline as b0_mod
    mode = args.mode
    units = b0_mod.load_units(corpus_path)

    if mode in ("C2P", "C2R"):
        from newdomain import cycle2 as c2_mod
        index = c2_mod.create_index(mode=mode, documents_path=corpus_path)
        build = c2_mod.build_messages
    elif mode == "C1":
        from newdomain import candidate as c1_mod
        index = c1_mod.create_index(documents_path=corpus_path)
        build = c1_mod.build_messages
    elif mode == "B0":
        index = b0_mod.NewDomainBaseline(b0_mod.build_chunks(units))
        build = b0_mod.build_messages
    else:
        print(f"ERROR: unknown mode {mode}", file=sys.stderr)
        return 2

    with open(questions_path, encoding="utf-8") as fh:
        cases = json.loads(fh.read())

    # Reject duplicate qids before writing anything
    qids = [c.get("qid") for c in cases]
    dupes = [q for q, n in Counter(qids).items() if n > 1]
    if dupes:
        print(f"ERROR: duplicate qids in questions file: {sorted(dupes)}", file=sys.stderr)
        return 2

    n_ok, n_err = 0, 0
    with open(out_path, "x", encoding="utf-8") as out:
        for case in cases:
            qid = case.get("qid")
            question = case.get("question", "")
            try:
                rt = index.retrieval(question, k=8)
                results = rt["results"]
                context = {c["id"]: c["text"] for c in results}
                msgs = build(question, results, mode=mode)
                prompt_sha = hashlib.sha256(
                    json.dumps(msgs, ensure_ascii=False).encode()).hexdigest()
                out.write(json.dumps({
                    "qid": qid, "question": question, "mode": mode,
                    "retrieval": {"ids": [c["id"] for c in results],
                                   "factors": rt.get("provenance", {}).get("factors", {})},
                    "context": context,
                    "prompt_sha256": prompt_sha,
                    "prompt_messages": msgs,
                }, ensure_ascii=False) + "\n")
                n_ok += 1
            except Exception as e:
                out.write(json.dumps({
                    "qid": qid, "error": f"{type(e).__name__}: {e}", "mode": mode,
                }, ensure_ascii=False) + "\n")
                n_err += 1

    print(json.dumps({"command": "prepare", "output": str(out_path),
                       "questions": len(cases), "prepared": n_ok, "errors": n_err,
                       "mode": mode, "corpus": str(corpus_path)}))
    return 0 if n_err == 0 else 1


def cmd_help(args) -> int:
    """Show help and current path configuration (works without data)."""
    import os
    print("newdomain.runner — offline CLI for the new-domain evaluation pipeline")
    print()
    print("Commands:")
    print("  replay    — re-validate saved generation results")
    print("  summarize — validity/latency/usage summary from saved results")
    print("  prepare   — offline retrieval + prompt preparation")
    print("  help      — this message")
    print()
    print("Path configuration (all optional; lazy on first use):")
    for var in ("NEWDOMAIN_CORPUS", "NEWDOMAIN_QUESTIONS", "NEWDOMAIN_RESULTS_DIR"):
        val = os.environ.get(var, "<not set>")
        print(f"  ${var} = {val}")
    print()
    print("All commands are offline: no API calls, no credential reads, no network.")
    print("Paid generation/judging is disabled in newdomain/generation.py during consolidation.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="newdomain.runner",
                                  description="Offline new-domain evaluation CLI")
    sub = ap.add_subparsers(dest="command")

    rp = sub.add_parser("replay", help="Re-validate saved results")
    rp.add_argument("--results", required=True, help="Path to results JSONL")
    rp.add_argument("--arm", default=None, help="Filter by arm (B0/C1/C2P/C2R)")
    rp.add_argument("--judge-results", default=None,
                    help="Optional path to saved judge results JSONL (reported separately)")

    sm = sub.add_parser("summarize", help="Summarize saved results")
    sm.add_argument("--results", required=True, help="Path to results JSONL")
    sm.add_argument("--judge-results", default=None,
                    help="Optional path to saved judge results JSONL")

    pr = sub.add_parser("prepare", help="Offline retrieval + prompt preparation")
    pr.add_argument("--corpus", required=True, help="Corpus JSONL path")
    pr.add_argument("--questions", required=True, help="Questions JSON path")
    pr.add_argument("--output", required=True, help="Output directory (file must not exist)")
    pr.add_argument("--mode", default="C2P", choices=["B0", "C1", "C2P", "C2R"])

    sub.add_parser("help", help="Show usage and path configuration")

    args = ap.parse_args()
    if args.command == "replay":
        return cmd_replay(args)
    if args.command == "summarize":
        return cmd_summarize(args)
    if args.command == "prepare":
        return cmd_prepare(args)
    return cmd_help(args)


if __name__ == "__main__":
    sys.exit(main())
