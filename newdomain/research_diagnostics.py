"""Offline C1/C3B prompt diagnostics on exposed saved contexts; no quality claim."""
import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path
from newdomain import candidate, clauses
from newdomain.paths import _ensure_outside_repo


def diagnose(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    selected = [r for r in rows if r.get("arm") == "C1"]
    if not selected or len({r["qid"] for r in selected}) != len(selected):
        raise ValueError("require unique saved C1 cases")
    totals = {"C1": [], "C3B": []}
    handle_counts = {"C1": [], "C3B": []}
    times = {"C1": [], "C3B": []}
    historical_hash_matches = 0
    clause_n = split_n = new_split_n = 0
    for row in selected:
        context = row["context"]
        old = candidate.passages_for_contexts(context)
        new = clauses.passages_for_contexts(context)
        for span in clauses.atomic_passages_for_contexts(context).values():
            clause_n += 1
            split_n += any(p["id"] == span["id"] and span["start"] < p["end"] < span["end"] for p in old.values())
            new_split_n += any(p["id"] == span["id"] and span["start"] < p["end"] < span["end"] for p in new.values())
        results = row["retrieval"]["results"]
        if {r["id"]: r["text"] for r in results} != context:
            raise ValueError("saved retrieval/context disagree")
        for arm, mod, handles in (("C1", candidate, old), ("C3B", clauses, new)):
            started = time.perf_counter()
            try:
                messages = mod.build_messages(row["question"], results, mode=arm)
            except ValueError as exc:
                if "payload budget exceeded" not in str(exc):
                    raise
                totals[arm].append(None)
            else:
                raw = json.dumps(messages, ensure_ascii=False).encode()
                totals[arm].append(len(raw))
                if arm == "C1":
                    historical_hash_matches += hashlib.sha256(raw).hexdigest() == row.get("prompt_sha256")
            times[arm].append((time.perf_counter() - started) * 1000)
            handle_counts[arm].append(len(handles))
    report = {"n_exposed_cases": len(selected), "historical_c1_prompt_hash_matches": historical_hash_matches,
        "complete_clause_instances": clause_n, "c1_split_clause_instances": split_n, "c3b_split_clause_instances": new_split_n,
        "interpretation": "Representation and prompt-size diagnostic only. Identical source characters; no generated answers or semantic gain measured.",
        "api_calls": 0, "api_cost_usd": 0, "by_arm": {}}
    for arm in totals:
        sizes = [n for n in totals[arm] if n is not None]
        report["by_arm"][arm] = {"prompt_budget_rejections": totals[arm].count(None),
            "mean_prompt_bytes": statistics.mean(sizes) if sizes else None,
            "max_prompt_bytes": max(sizes) if sizes else None,
            "mean_handles": statistics.mean(handle_counts[arm]),
            "mean_prompt_build_ms": statistics.mean(times[arm]),
            "timing_scope": "Single local pass; excludes retrieval, model, validation and cold/warm control."}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, type=Path)
    args = parser.parse_args()
    path = _ensure_outside_repo(args.results, "Exposed results")
    print(json.dumps(diagnose(path), indent=2))


if __name__ == "__main__":
    main()
