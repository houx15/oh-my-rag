"""Offline answer-obligation diagnostic. Never a semantic judge or human gold."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r"\s+", "", text).lower()


def inspect_answer(text, requirements):
    """Missing patterns flag review; matching patterns never establish entailment."""
    value = normalized(text)
    return [{"id": r["id"], "criterion": r["criterion"],
             "status": "surface_present_needs_semantic_review" if all(
                 re.search(pattern, value) for pattern in r["patterns"]
             ) else "missing_or_paraphrased_needs_review"}
            for r in requirements]


def risk_checks(text, requirements):
    """Conservative review flags for two calibrated semantic risk patterns.

    These flags are not a general entailment model and never repair answers.
    """
    value = normalized(text)
    risks = []
    for req in requirements:
        if any(re.search(r"(?:不要求|无需|无须|不必|不需要).{0,10}(?:" + pattern + r")", value)
               for pattern in req["patterns"]):
            risks.append({"id":"negated_obligation:"+req["id"],"status":"contradiction_risk_needs_review"})
    refusal = re.search(r"资料(?:不足|未包含)|无法确认|不能确认|没有.{0,8}依据", value)
    if refusal:
        # Narrow positive payment assertions. Explanatory caps and negated
        # payment claims are excluded; other fabrications remain a review task.
        for match in re.finditer(r"(?:已经|已|今天|现已|实际)?(?:到账|收到|获批|支付)(?:了)?[0-9]+(?:\.[0-9]+)?(?:万|亿)?元", value):
            prefix=value[max(0,match.start()-8):match.start()]
            if not re.search(r"未|不|无法|不能|没有|并非|假设|例如",prefix):
                risks.append({"id":"unsupported_fact_after_refusal","status":"unsupported_claim_risk_needs_review"})
                break
    return risks


def validate_annotations(annotations, cases):
    if annotations["status"] != "posthoc_assistant_source_review_not_human_gold":
        raise ValueError("annotation provenance missing")
    seen = set()
    for item in annotations["cases"]:
        qid = item["qid"]
        if qid in seen or qid not in cases:
            raise ValueError("duplicate or unknown case")
        seen.add(qid)
        ids = set()
        for req in item["requirements"]:
            if req["id"] in ids or not req["patterns"]:
                raise ValueError("duplicate or empty criterion")
            ids.add(req["id"])
            for pattern in req["patterns"]:
                re.compile(pattern)
            support = req["support"]
            if support["kind"] == "source_span":
                source = cases[qid]["fixed_context"][support["page"]]
                if not support["quote"] or normalized(support["quote"]) not in normalized(source):
                    raise ValueError("criterion quote not in frozen source view")
            elif support["kind"] in ("question_premise", "derived", "corpus_absence_review"):
                if not support.get("rationale"):
                    raise ValueError("derived/absence premise needs explicit rationale")
            else:
                raise ValueError("unknown support kind")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if args.output.resolve() == repo or repo in args.output.resolve().parents:
        raise ValueError("private diagnostic output must remain outside repository")
    ann = json.loads(args.annotations.read_text())
    for name, expected in ann["input_hashes"].items():
        if digest(args.root / name) != expected:
            raise ValueError("diagnostic input changed")
    cases = {r["qid"]: r for r in json.loads((args.root / "final-judge-cases.json").read_text())}
    validate_annotations(ann, cases)
    answers = {(r["qid"], r["arm"]):r for r in map(json.loads,(args.root / "final-final-results.jsonl").read_text().splitlines())}
    judges = []
    for name in ("primary", "secondary"):
        judges.append({(r["qid"],a):s for r in map(json.loads,(args.root / f"final-final-{name}-judge.jsonl").read_text().splitlines()) for a,s in r["scores"].items()})
    results, controls, blindspots = [], [], []
    for item in ann["cases"]:
        for arm in ("C1", "C3B"):
            key = (item["qid"], arm)
            # Deliberately exclude question, references and citation quotes.
            text = "\n".join(s["text"] for s in answers[key]["answer"]["sentences"])
            checks = inspect_answer(text, item["requirements"])
            results.append({"qid":key[0], "arm":arm, "stratum":cases[key[0]]["stratum"],
                "checks":checks, "original_both_adequate":all(j[key]["adequate"] for j in judges),
                "flagged_ids":[c["id"] for c in checks if c["status"].startswith("missing")],
                "risk_flags":risk_checks(text, item["requirements"])})
        for control in item["controls"]:
            flags = [c["id"] for c in inspect_answer(control["text"], item["requirements"]) if c["status"].startswith("missing")]
            controls.append({"qid":item["qid"],"name":control["name"],"expected_flags":control["expected_flags"],"actual_flags":flags,"matches_expectation":set(flags)==set(control["expected_flags"])})
        for control in item.get("blindspot_controls", []):
            checks = inspect_answer(control["text"], item["requirements"])
            blindspots.append({"qid":item["qid"], "name":control["name"], "reason":control["reason"],
                "flagged_ids":[c["id"] for c in checks if c["status"].startswith("missing")],
                "risk_flags":risk_checks(control["text"], item["requirements"]),
                "semantic_status":"assistant_constructed_error_requires_review"})
    result = {"status":ann["status"],"annotation_sha256":digest(args.annotations),
        "tool_sha256":digest(__file__),"limitations":ann["limitations"],"results":results,"controls":controls,"known_semantic_blindspots":blindspots,
        "api_calls":0,"quality_score":None}
    with args.output.open("x", encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"cases":len(ann["cases"]),"arms_flagged":sum(bool(r["flagged_ids"]) for r in results),
        "controls":len(controls),"controls_matching":sum(r["matches_expectation"] for r in controls),"api_calls":0}))


if __name__ == "__main__":
    main()
