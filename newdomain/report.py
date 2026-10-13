"""Offline reporting: paired transitions, bootstrap, judge agreement, cost/timing.

Consumes saved generation results, primary judge files and optional independent
audit verdict files. All functions are pure offline — no network, no API calls.
"""
from __future__ import annotations

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

JUDGE_AXES = ("correctness", "support", "relevance", "completeness")
JUDGE_BOOLS = ("citation_entailment", "reference_complete")


def load_jsonl(path: Path) -> List[Dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def extract_judge_scores(judge_rows: List[Dict],
                          gen_rows: List[Dict] = None) -> Dict[tuple, Dict]:
    """Extract (qid, arm) -> scores from judge journal rows.
    If gen_rows provided, only keep scores for arms with valid+complete generation."""
    gen_status = {}
    if gen_rows:
        for r in gen_rows:
            gen_status[(r.get("qid"), r.get("arm"))] = (r.get("valid"), r.get("complete"))
    scores = {}
    for e in judge_rows:
        if e.get("error"):
            continue
        mapping = e.get("mapping") or {}
        entry_scores = e.get("scores") or {}
        for label, arm in mapping.items():
            sc = entry_scores.get(arm)
            if not isinstance(sc, dict):
                continue
            key = (e["qid"], arm)
            if key in scores:
                raise ValueError(f"Duplicate judge score for {key}")
            if gen_rows:
                valid, complete = gen_status.get(key, (None, None))
                sc = dict(sc)
                sc["generation_valid"] = bool(valid)
                sc["generation_complete"] = bool(complete)
            scores[key] = sc
    return scores


def load_audit_verdicts(audit_dir: Path,
                         accepted_hashes_file: Path = None,
                         mapping_file: Path = None,
                         gen_rows: List[Dict] = None) -> Dict[tuple, Dict]:
    """Load audit verdicts via verified mapping+hashes; fail-closed on mismatches."""
    gen_status = {}
    if gen_rows:
        for r in gen_rows:
            gen_status[(r.get("qid"), r.get("arm"))] = (r.get("valid"), r.get("complete"))
    if accepted_hashes_file is None:
        accepted_hashes_file = audit_dir / "accepted-verdict-hashes.json"
    if mapping_file is None:
        mapping_file = audit_dir / "mapping.json"
    if not accepted_hashes_file.exists():
        raise FileNotFoundError(f"accepted-hashes missing: {accepted_hashes_file}")
    if not mapping_file.exists():
        raise FileNotFoundError(f"mapping missing: {mapping_file}")
    accepted = json.loads(accepted_hashes_file.read_text(encoding="utf-8"))
    mapping = json.loads(mapping_file.read_text(encoding="utf-8"))
    import hashlib
    audit_provenance(audit_dir, mapping_file)
    scores = {}
    skipped = []
    for verdict_file, expected_sha in sorted(accepted.items()):
        if Path(verdict_file).name != verdict_file:
            raise ValueError("audit filenames must be local basenames")
        vpath = audit_dir / verdict_file
        if not vpath.exists():
            skipped.append(f"missing:{verdict_file}")
            continue
        got_sha = hashlib.sha256(vpath.read_bytes()).hexdigest()
        if got_sha != expected_sha:
            skipped.append(f"hash_mismatch:{verdict_file}")
            continue
        for entry in json.loads(vpath.read_text(encoding="utf-8")):
            case_id = entry.get("case_id")
            if case_id not in mapping:
                skipped.append(f"unmapped:{case_id}")
                continue
            qid = mapping[case_id]["qid"]
            labels = mapping[case_id].get("labels") or {}
            for label, arm in labels.items():
                sc = entry.get(label)
                if not isinstance(sc, dict):
                    skipped.append(f"not_dict:{verdict_file}:{case_id}:{label}")
                    continue
                for axis in JUDGE_AXES:
                    if type(sc.get(axis)) is not int or not 0 <= sc[axis] <= 2:
                        skipped.append(f"bad_axis:{verdict_file}:{case_id}:{label}:{axis}")
                        sc = None
                        break
                if sc is None:
                    continue
                for boolean in JUDGE_BOOLS:
                    if type(sc.get(boolean)) is not bool:
                        skipped.append(f"bad_bool:{verdict_file}:{case_id}:{label}:{boolean}")
                        sc = None
                        break
                if sc is None:
                    continue
                if gen_status:
                    valid, complete = gen_status.get((qid, arm), (None, None))
                    sc = dict(sc)
                    sc["generation_valid"] = bool(valid)
                    sc["generation_complete"] = bool(complete)
                key = (qid, arm)
                if key in scores:
                    raise ValueError(f"duplicate audit score for {key} from {verdict_file}")
                scores[key] = sc
    if skipped:
        import warnings
        warnings.warn(f"audit loading skipped {len(skipped)}: {'; '.join(skipped[:5])}")
    return scores


def both_judge_conjunction(primary_scores: Dict[tuple, Dict],
                            audit_scores: Dict[tuple, Dict]) -> Dict[tuple, bool]:
    """Per-key: primary adequate AND audit adequate (both require valid+complete)."""
    common = set(primary_scores) & set(audit_scores)
    result = {}
    for key in common:
        def _ok(sc):
            return (all(sc.get(ax) == 2 for ax in JUDGE_AXES)
                    and all(sc.get(b) for b in JUDGE_BOOLS)
                    and sc.get("generation_valid", True)
                    and sc.get("generation_complete", True))
        result[key] = _ok(primary_scores[key]) and _ok(audit_scores[key])
    return result


def extract_audit_scores(audit_rows: List[Dict]) -> Dict[tuple, Dict]:
    """Legacy interface: direct row-based audit scores (kept for compatibility)."""
    scores = {}
    for v in audit_rows:
        qid = v.get("qid")
        arm = v.get("arm") or v.get("answer_arm") or "A"
        sc = v.get("scores") or v.get("verdict") or v
        if isinstance(sc, dict) and qid:
            scores[(qid, arm)] = sc
    return scores


def judge_agreement(primary: Dict[tuple, Dict], audit: Dict[tuple, Dict]) -> Dict:
    """Per-axis agreement between primary judge and independent audit.
    Skips entries where either side lacks the axis value (None != None)."""
    common = set(primary) & set(audit)
    if not common:
        return {"error": "no common (qid,arm) keys", "primary_n": len(primary),
                "audit_n": len(audit)}
    result = {"n_common": len(common),
              "primary_only": len(primary) - len(common),
              "audit_only": len(audit) - len(common)}
    for axis in JUDGE_AXES:
        scored = [(primary[k].get(axis), audit[k].get(axis))
                  for k in common
                  if primary[k].get(axis) is not None and audit[k].get(axis) is not None]
        if scored:
            agree = sum(1 for p, a in scored if p == a)
            result[f"{axis}_agreement"] = round(agree / len(scored), 4)
            result[f"{axis}_scored_n"] = len(scored)
        else:
            result[f"{axis}_agreement"] = None
            result[f"{axis}_scored_n"] = 0
    both_complete = [k for k in common
                     if all(primary[k].get(a) is not None and audit[k].get(a) is not None
                            for a in JUDGE_AXES)]
    if both_complete:
        perfect = sum(1 for k in both_complete
                      if all(primary[k].get(a) == audit[k].get(a) for a in JUDGE_AXES))
        result["perfect_agreement"] = round(perfect / len(both_complete), 4)
        result["perfect_scored_n"] = len(both_complete)
    return result


def adequate_count(scores: Dict[tuple, Dict]) -> int:
    """Count entries meeting the judge's adequacy threshold:
    all 4 axes == 2 AND both booleans True AND generation valid+complete."""
    count = 0
    for sc in scores.values():
        if not (all(sc.get(a) == 2 for a in JUDGE_AXES)
                and all(sc.get(b) for b in JUDGE_BOOLS)):
            continue
        # If generation status was attached, require valid+complete
        if "generation_valid" in sc:
            if not sc["generation_valid"] or not sc["generation_complete"]:
                continue
        count += 1
    return count


def paired_transitions(rows_a: List[Dict], rows_b: List[Dict],
                        field: str = "valid") -> Dict:
    by_qid_a = {r["qid"]: r for r in rows_a}
    by_qid_b = {r["qid"]: r for r in rows_b}
    common = set(by_qid_a) & set(by_qid_b)
    a_win = sum(1 for q in common if by_qid_a[q].get(field) and not by_qid_b[q].get(field))
    b_win = sum(1 for q in common if by_qid_b[q].get(field) and not by_qid_a[q].get(field))
    return {"n_common": len(common), "a_only": len(by_qid_a) - len(common),
            "b_only": len(by_qid_b) - len(common),
            "a_better": a_win, "b_better": b_win, "tied": len(common) - a_win - b_win}


def bootstrap_paired(rows_a: List[Dict], rows_b: List[Dict],
                      field: str = "valid", n_boot: int = 10000,
                      seed: int = 20261012) -> Dict:
    by_qid_a = {r["qid"]: r.get(field, False) for r in rows_a}
    by_qid_b = {r["qid"]: r.get(field, False) for r in rows_b}
    common = sorted(set(by_qid_a) & set(by_qid_b))
    if not common:
        return {"error": "no common qids"}
    a_vals = np.array([1.0 if by_qid_a[q] else 0.0 for q in common])
    b_vals = np.array([1.0 if by_qid_b[q] else 0.0 for q in common])
    rng = np.random.default_rng(seed)
    n = len(common)
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        diffs.append(b_vals[idx].mean() - a_vals[idx].mean())
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"n_pairs": n, "a_rate": round(float(a_vals.mean()), 4),
            "b_rate": round(float(b_vals.mean()), 4),
            "delta": round(float(b_vals.mean() - a_vals.mean()), 4),
            "ci95_lo": round(float(lo), 4), "ci95_hi": round(float(hi), 4)}


def latency_summary(rows: List[Dict]) -> Dict:
    ms = sorted(r.get("full_ms", 0) for r in rows if r.get("full_ms") is not None)
    if not ms:
        return {"n": 0}
    arr = np.array(ms)
    ttfts = [((r.get("raw_response") or {}).get("timings") or {}).get("ttft_ms")
             for r in rows if ((r.get("raw_response") or {}).get("timings") or {}).get("ttft_ms")]
    result = {"n": len(ms),
              "p50_ms": round(float(np.median(arr)), 1),
              "p95_ms": round(float(np.percentile(arr, 95)), 1),
              "max_ms": round(float(arr.max()), 1)}
    if ttfts:
        t = np.array(ttfts)
        result["ttft_p50_ms"] = round(float(np.median(t)), 1)
        result["ttft_p95_ms"] = round(float(np.percentile(t, 95)), 1)
    return result


def cost_summary(rows: List[Dict]) -> Dict:
    in_toks = sum(((r.get("raw_response") or {}).get("usage") or {}).get("input_tokens", 0)
                  for r in rows)
    out_toks = sum(((r.get("raw_response") or {}).get("usage") or {}).get("output_tokens", 0)
                   for r in rows)
    return {"total_input_tokens": in_toks, "total_output_tokens": out_toks}


def failure_summary(rows: List[Dict]) -> Dict:
    failures = Counter()
    valid = sum(1 for r in rows if r.get("valid"))
    for r in rows:
        if not r.get("valid"):
            gate = r.get("gate") or {}
            fail = str(gate.get("failure", r.get("error", "unknown")))[:120]
            failures[fail] += 1
    return {"n": len(rows), "valid": valid, "invalid": len(rows) - valid,
            "failure_categories": dict(failures.most_common())}


def structural_uncited_count(rows: List[Dict]) -> int:
    """Valid rows where all sentences lack citations (structural proxy, NOT
    confirmed true abstention — the sentence could be a template or an error)."""
    count = 0
    for r in rows:
        if not r.get("valid"):
            continue
        ans = r.get("answer")
        if isinstance(ans, dict) and ans.get("sentences"):
            if all(not s.get("citations") for s in ans["sentences"]):
                count += 1
    return count


def full_report(results_path: Path, judge_path: Path = None,
                audit_dir: Path = None) -> Dict:
    rows = load_jsonl(results_path)
    gen_keys = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("generation row must be an object")
        key = (row.get("qid"), row.get("arm"))
        if not all(isinstance(v, str) and v for v in key) or key in gen_keys:
            raise ValueError("invalid or duplicate generation identity")
        gen_keys.add(key)
    for path in (judge_path, audit_dir):
        if path is not None and not path.exists():
            raise FileNotFoundError(path)
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r.get("arm", "?")].append(r)

    judge_scores = {}
    if judge_path is not None and judge_path.exists():
        judge_scores = extract_judge_scores(load_jsonl(judge_path), gen_rows=rows)

    audit_scores = {}
    if audit_dir is not None and audit_dir.exists():
        audit_scores = load_audit_verdicts(audit_dir, gen_rows=rows)

    report = {
        "results_file": str(results_path),
        "judge_file": str(judge_path) if judge_path else None,
        "audit_dir": str(audit_dir) if audit_dir else None,
        "by_arm": {},
        "audit_provenance": audit_provenance(audit_dir) if audit_dir else None,
        "cost_scope": "Token totals only; dollar cost requires canonical ledger settlements, including failed calls and judges.",
    }
    for arm, arm_rows in sorted(by_arm.items()):
        arm_report = {
            **failure_summary(arm_rows),
            "latency": latency_summary(arm_rows),
            "cost": cost_summary(arm_rows),
            "structural_uncited_valid": structural_uncited_count(arm_rows),
        }
        arm_judge = {k: v for k, v in judge_scores.items() if k[1] == arm}
        if arm_judge:
            arm_report["judge_scored"] = len(arm_judge)
            arm_report["judge_semantic_adequate"] = sum(
                1 for sc in arm_judge.values() if sc.get("semantic_adequate"))
            arm_report["judge_adequate"] = adequate_count(arm_judge)
        arm_audit = {k: v for k, v in audit_scores.items() if k[1] == arm}
        if arm_audit:
            arm_report["audit_scored"] = len(arm_audit)
            arm_report["audit_adequate"] = adequate_count(arm_audit)
            arm_report["audit_semantic_adequate"] = sum(all(sc.get(a) == 2 for a in JUDGE_AXES) and all(sc.get(b) is True for b in JUDGE_BOOLS) for sc in arm_audit.values())
        report["by_arm"][arm] = arm_report

    if len(by_arm) == 2:
        arms = sorted(by_arm)
        report["paired"] = {
            "metric": "mechanical validity (not semantic adequacy)",
            "transitions": paired_transitions(by_arm[arms[0]], by_arm[arms[1]]),
            "bootstrap": bootstrap_paired(by_arm[arms[0]], by_arm[arms[1]])}

    if judge_scores and audit_scores:
        report["judge_agreement"] = judge_agreement(judge_scores, audit_scores)
        conjunction = both_judge_conjunction(judge_scores, audit_scores)
        if len(by_arm) == 2:
            arms = sorted(by_arm)
            report["quality_paired"] = grouped_quality_bootstrap(rows, conjunction, arms)
        for arm in sorted(by_arm):
            arm_conj = sum(1 for key, ok in conjunction.items() if ok and key[1] == arm)
            report["by_arm"][arm]["both_judge_adequate"] = arm_conj

    # Explicit coverage/missingness
    gen_keys = {(r["qid"], r["arm"]) for r in rows}
    report["coverage"] = {
        "generation_unique_keys": len(gen_keys),
        "judge_scored_keys": len(judge_scores),
        "judge_missing_keys": len(gen_keys - set(judge_scores)),
        "audit_scored_keys": len(audit_scores),
        "judge_extra_keys": len(set(judge_scores) - gen_keys),
        "audit_extra_keys": len(set(audit_scores) - gen_keys),
        "audit_missing_keys": len(gen_keys - set(audit_scores)) if audit_scores else None,
    }
    return report


def audit_provenance(audit_dir, mapping_file=None):
    """Verify available pack hashes; disclose absent historical mapping pinning.

    A current digest is a reproducibility receipt, not a trusted signature.
    Historical manifests without mapping hashes cannot authenticate arm labels.
    """
    import hashlib
    audit_dir = Path(audit_dir)
    mapping_file = Path(mapping_file or audit_dir / "mapping.json")
    manifest_file = audit_dir / "manifest.json"
    result = {"mapping_sha256": hashlib.sha256(mapping_file.read_bytes()).hexdigest(),
              "mapping_hash_pinned": False, "verified_pack_count": 0}
    if not manifest_file.exists():
        result["limitation"] = "No audit manifest; verdict hashes alone do not bind mapping or source packs."
        return result
    manifest = json.loads(manifest_file.read_text())
    result["manifest_sha256"] = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
    for filename, expected in manifest.get("hashes", {}).items():
        if Path(filename).name != filename:
            raise ValueError("audit manifest filenames must be basenames")
        path = mapping_file if filename == "mapping.json" else audit_dir / filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"audit manifest hash mismatch: {filename}")
        if filename == "mapping.json":
            result["mapping_hash_pinned"] = True
        elif filename.startswith("pack-"):
            result["verified_pack_count"] += 1
    if not result["mapping_hash_pinned"]:
        result["limitation"] = "Historical manifest does not pin mapping; current mapping digest recorded, not independently authenticated."
    return result


def grouped_quality_bootstrap(rows, adequacy, arms, n_boot=5000, seed=20261012):
    """Paired cluster bootstrap; source grouping is only as good as input labels."""
    grouped = {}
    by_key = {(r["qid"], r["arm"]): r for r in rows}
    qids = sorted({q for q, arm in adequacy if arm == arms[0]} &
                  {q for q, arm in adequacy if arm == arms[1]})
    if not qids:
        return {"n_pairs": 0}
    fallback = 0
    for qid in qids:
        a, b = by_key[(qid, arms[0])], by_key[(qid, arms[1])]
        if a.get("group", qid) != b.get("group", qid):
            raise ValueError("paired source-group labels disagree")
        group = a.get("group", qid)
        fallback += int("group" not in a)
        grouped.setdefault(group, []).append(int(adequacy[(qid, arms[1])]) - int(adequacy[(qid, arms[0])]))
    values = list(grouped.values())
    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(n_boot):
        sample = [v for i in rng.integers(0, len(values), size=len(values)) for v in values[i]]
        deltas.append(float(np.mean(sample)))
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {"metric": "both-judge adequacy", "arms": arms, "direction": "second minus first",
            "n_pairs": len(qids), "n_groups": len(values), "qid_fallback_count": fallback,
            "delta": float(np.mean([v for group in values for v in group])),
            "ci95": [float(lo), float(hi)],
            "limitation": "Input group labels are not independently verified source/entity families; few clusters give unstable intervals."}
