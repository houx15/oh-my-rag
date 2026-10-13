"""Private frozen experiment orchestration using existing canonical accounting.

No corpus, references or results belong in this module or in Git. Generation
receives only the explicitly allowlisted question view; judge references live
in separate files, never passed as generation cases or fixed context.
"""
import argparse
from contextlib import contextmanager
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import threading
from newdomain.paths import _ensure_outside_repo
from newdomain.profile import load_profile, verify_profile
from newdomain.transport import LiveContext, screen
from eval.optimization.budget import chat_conservative_estimates, _validate_state


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, payload):
    with Path(path).open("x", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def canonical_totals(manifest_path, manifest):
    total = Decimal("0")
    opened = Decimal("0")
    for stage in ("dev", "final"):
        state = json.loads((manifest_path.parent / f"ledger.{stage}.json").read_text())
        _validate_state(state, manifest, stage, simulated=False)
        total += Decimal(str(state["totals"]["charged_cost_usd"]))
        opened += Decimal(str(state["totals"]["reserved_open_cost_usd"]))
    return total, opened


class ExperimentContext(LiveContext):
    def __init__(self, *, experiment_root, **kwargs):
        super().__init__(**kwargs)
        self.experiment_root = Path(experiment_root)
        self.budget = json.loads((self.experiment_root / "budget-freeze.json").read_text())
        if self.budget["manifest_sha256"] != sha(self.manifest_path):
            raise RuntimeError("experiment manifest changed")
        self._experiment_thread_lock = threading.Lock()

    @contextmanager
    def request_scope(self, model):
        # Serialize experiment admission + dispatch + settlement. The canonical
        # ledger still independently enforces the shared global stage caps.
        with self._experiment_thread_lock:
            with (self.experiment_root / "admission.lock").open("a") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                try:
                    baseline = Decimal(self.budget["baseline_current_ledgers_usd"])
                    charged, opened = canonical_totals(self.manifest_path, self.manifest)
                    if charged < baseline:
                        raise RuntimeError("canonical spend moved backwards")
                    i, o = chat_conservative_estimates(self.manifest, model)
                    estimate = Decimal(str(self.manifest.tariff(model).cost(i, o)))
                    if charged - baseline + opened + estimate > Decimal(self.budget["additional_cap_usd"]):
                        raise RuntimeError("experiment allocation cannot cover the conservative next request")
                    yield
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def freeze(root, authoring, corpus, old_questions, profile_path):
    root = _ensure_outside_repo(root, "Private experiment")
    root.mkdir(exist_ok=True)
    cases = json.loads(Path(authoring).read_text())
    old = [json.loads(line)["question"] for line in Path(old_questions).read_text().splitlines() if line.strip()]
    seen = set()
    groups = {split: set() for split in ("pilot", "final")}
    for c in cases:
        if c["split"] not in groups or c["qid"] in seen or c["question"] in old:
            raise ValueError("duplicate/exposed question or invalid split")
        seen.add(c["qid"])
        groups[c["split"]].add(c["group"])
    if groups["pilot"] & groups["final"]:
        raise ValueError("pilot/final source families overlap")
    units = [json.loads(line) for line in Path(corpus).read_text().splitlines() if line.strip()]
    lookup = {(u["doc_id"], str(u["locator"])): u for u in units}
    profile = load_profile(profile_path)
    paths = verify_profile(profile, "dev")
    ctx = LiveContext(**{k:paths[k] for k in ("manifest_path", "redaction_names_path")}, stage="dev", expected_ledger_path=paths["ledger_path"])
    baseline, opened = canonical_totals(ctx.manifest_path, ctx.manifest)
    if opened:
        raise RuntimeError("unresolved canonical reservations")
    write_new(root / "budget-freeze.json", {"manifest_sha256": sha(ctx.manifest_path),
        "baseline_current_ledgers_usd": str(baseline), "prior_spend_usd": str(json.loads(ctx.manifest_path.read_text()).get("prior_spend_usd", 0)),
        "additional_cap_usd": "12", "baseline_cumulative_usd": str(baseline + Decimal(str(json.loads(ctx.manifest_path.read_text()).get("prior_spend_usd", 0)))),
        "all_provider_and_judge_calls_included": True})
    for split in groups:
        subset = [c for c in cases if c["split"] == split]
        inference = []
        judges = []
        for c in subset:
            inference.append({k:c[k] for k in ("qid", "question", "group", "origin")})
            evidence = {}
            for doc, page in c["sources"]:
                u = lookup[(doc, str(page))]
                evidence[f"{doc}:{page}"] = u["text"]
            judge = dict(inference[-1], provided_reference=c["reference"], fixed_context=evidence,
                         stratum=c["stratum"], reference_status="assistant-reviewed screened source text; no human gold; OCR fidelity not independently certified")
            screen([{"role":"user", "content":json.dumps(judge, ensure_ascii=False)}], paths["redaction_names_path"])
            judges.append(judge)
        write_new(root / f"{split}-questions.json", inference)
        write_new(root / f"{split}-judge-cases.json", judges)
    repo = Path(__file__).resolve().parent.parent
    code = {str(p):sha(p) for p in sorted((repo / "newdomain").glob("*.py"))}
    code.update({str(repo / "eval/optimization" / n):sha(repo / "eval/optimization" / n) for n in ("budget.py", "transports.py", "telemetry.py")})
    inference_hashes = {str(Path(corpus)):sha(corpus), str(root / "budget-freeze.json"):sha(root / "budget-freeze.json"), **code}
    inference_hashes.update({str(root / f"{s}-questions.json"):sha(root / f"{s}-questions.json") for s in groups})
    write_new(root / "inference-freeze.json", {"hashes":inference_hashes,
        "scope":"generation questions, source corpus and code only; no reference paths or answers"})
    write_new(root / "evaluation-freeze.json", {"hashes": {**inference_hashes,
        **{str(root / f"{s}-judge-cases.json"):sha(root / f"{s}-judge-cases.json") for s in groups},
        str(root / "budget-freeze.json"):sha(root / "budget-freeze.json")},
        "groups": {s:sorted(v) for s,v in groups.items()},
        "selection":"C3B fixed before authoring; pilot checks mechanics, no tuning after freeze",
        "limitation":"new assistant-authored questions on previously exposed corpus; source family split only between pilot and final, not a new-corpus generalization claim"})


def run(root, profile_path, corpus, split, action):
    root = _ensure_outside_repo(root, "Private experiment")
    freeze_path = root / ("inference-freeze.json" if action == "generate" else "evaluation-freeze.json")
    for filename, expected in json.loads(freeze_path.read_text())["hashes"].items():
        if sha(filename) != expected:
            raise RuntimeError(f"frozen input changed: {Path(filename).name}")
    stage = "dev" if split == "pilot" else "final"
    paths = verify_profile(load_profile(profile_path), stage)
    ctx = ExperimentContext(experiment_root=root, manifest_path=paths["manifest_path"],
        redaction_names_path=paths["redaction_names_path"], stage=stage, expected_ledger_path=paths["ledger_path"])
    if action == "generate":
        from newdomain.generation import run_live_v2
        cases = json.loads((root / f"{split}-questions.json").read_text())
        if any(set(c) != {"qid", "question", "group", "origin"} for c in cases):
            raise ValueError("inference view contains forbidden fields")
        run_live_v2(stage, ["C1", "C3B"], split, workers=1, output_dir=root,
            casefile=root / f"{split}-questions.json", corpus_path=corpus,
            freeze_file=freeze_path, live_context=ctx)
    else:
        from newdomain.judge import judge_live_v2, judge_cycle2
        common = dict(stage=stage, files=[str(root / f"{stage}-{split}-results.jsonl")], name=f"{split}-{action}",
            workers=1, output_dir=root, casefile=root / f"{split}-judge-cases.json",
            corpus_path=corpus, freeze_file=freeze_path, live_context=ctx)
        if action == "primary":
            judge_live_v2(**common)
        else:
            judge_cycle2(dataset=split, redaction_names_path=paths["redaction_names_path"], **common)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("freeze", "generate", "primary", "secondary"))
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--authoring", type=Path)
    p.add_argument("--old-questions", type=Path)
    p.add_argument("--split", choices=("pilot", "final"), default="pilot")
    args = p.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.authoring, args.corpus, args.old_questions, args.profile)
    else:
        run(args.root, args.profile, args.corpus, args.split, args.action)


if __name__ == "__main__":
    main()
