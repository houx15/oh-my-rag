"""Frozen exposed regression and preselected latency-repeat runs. Private outputs."""
import argparse
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import ExperimentContext, sha, write_new
from newdomain.profile import load_profile, verify_profile
from newdomain.transport import screen
from newdomain.paths import _ensure_outside_repo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "generate", "primary", "secondary"))
    parser.add_argument("--mode", choices=("regression", "repeat"), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--regression", type=Path)
    args = parser.parse_args()
    root, mode = _ensure_outside_repo(args.root, "Private experiment"), args.mode
    original_freeze = json.loads((root / "evaluation-freeze.json").read_text())
    for name, digest in original_freeze["hashes"].items():
        if sha(name) != digest:
            raise RuntimeError("original frozen source or candidate changed")
    paths = verify_profile(load_profile(args.profile), "final")
    if args.action == "prepare":
        if mode == "repeat":
            chosen = set(json.loads((root / "decision-plan.json").read_text())["preselected_repeat_qids"])
            cases = [r for r in json.loads((root / "final-questions.json").read_text()) if r["qid"] in chosen]
            judges = []
        else:
            cases, judges = [], []
            for r in json.loads(args.regression.read_text()):
                match = re.search(r"MD-\d+", r["qid"])
                group = match.group() if match else r.get("kind", "regression")
                case = {"qid":r["qid"], "question":r["question"], "group":group,
                        "origin":"exposed_regression"}
                if r.get("fixed_context"):
                    case["fixed_context"] = r["fixed_context"]
                cases.append(case)
                reference = r.get("expected_behavior") or "Prior unvalidated answer, not gold: " + json.dumps(r.get("prior_answer"),ensure_ascii=False)
                judges.append(dict(case, provided_reference=reference, stratum="regression"))
        for case in cases + judges:
            screen([{"role":"user", "content":json.dumps(case,ensure_ascii=False)}], paths["redaction_names_path"])
        write_new(root / f"{mode}-questions.json", cases)
        if judges:
            write_new(root / f"{mode}-judge-cases.json", judges)
        hashes = dict(json.loads((root / "inference-freeze.json").read_text())["hashes"])
        hashes.update({str(root / f"{mode}-questions.json"):sha(root / f"{mode}-questions.json"),
                       str(Path(__file__).resolve()):sha(__file__)})
        write_new(root / f"{mode}-inference-freeze.json", {"hashes":hashes})
        if judges:
            hashes = dict(hashes)
            hashes[str(root / f"{mode}-judge-cases.json")] = sha(root / f"{mode}-judge-cases.json")
            hashes[str(args.regression)] = sha(args.regression)
            write_new(root / f"{mode}-evaluation-freeze.json", {"hashes":hashes})
        return
    ctx = ExperimentContext(experiment_root=root, manifest_path=paths["manifest_path"],
        redaction_names_path=paths["redaction_names_path"], stage="final", expected_ledger_path=paths["ledger_path"])
    if args.action == "generate":
        from newdomain.generation import run_live_v2
        run_live_v2("final", ["C1", "C3B"], mode, repeat=1 if mode=="repeat" else 0, workers=1,
            output_dir=root, casefile=root / f"{mode}-questions.json", corpus_path=args.corpus,
            freeze_file=root / f"{mode}-inference-freeze.json", live_context=ctx)
    else:
        from newdomain.judge import judge_live_v2, judge_cycle2
        common = dict(stage="final", files=[str(root / f"final-{mode}-results.jsonl")],
            name=f"{mode}-{args.action}", workers=1, output_dir=root,
            casefile=root / f"{mode}-judge-cases.json", corpus_path=args.corpus,
            freeze_file=root / f"{mode}-evaluation-freeze.json", live_context=ctx)
        if args.action == "primary":
            judge_live_v2(**common)
        else:
            judge_cycle2(dataset=mode, redaction_names_path=paths["redaction_names_path"], **common)


if __name__ == "__main__":
    main()
