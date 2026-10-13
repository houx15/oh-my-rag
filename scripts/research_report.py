"""Offline private experiment report: paired quality, disagreement, cost, QA."""
import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.report import grouped_quality_bootstrap, latency_summary
from newdomain.experiment import sha, write_new
from newdomain.paths import _ensure_outside_repo

AXES = ("correctness", "support", "relevance", "completeness")
BOOLS = ("citation_entailment", "reference_complete")
ARMS = ("C1", "C3B")


def read_rows(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(r.get("error") for r in rows):
        raise ValueError(f"unresolved failure in {path.name}")
    return rows


def scores(rows):
    result = {}
    for row in rows:
        for arm, score in row["scores"].items():
            key = (row["qid"], arm)
            if key in result:
                raise ValueError("duplicate judge key")
            if any(type(score.get(a)) is not int or not 0 <= score[a] <= 2 for a in AXES):
                raise ValueError("malformed judge axis")
            if any(type(score.get(b)) is not bool for b in BOOLS):
                raise ValueError("malformed judge boolean")
            result[key] = score
    return result


def response_cost(response, model, tariffs):
    usage = response["usage"]
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens")):
        raise ValueError("missing or invalid usage")
    rates = tariffs[model]
    return (Decimal(usage["input_tokens"]) * Decimal(str(rates["input_per_1m"])) +
            Decimal(usage["output_tokens"]) * Decimal(str(rates["output_per_1m"]))) / Decimal(1000000)


def section(root, split, tariffs):
    stage = "dev" if split == "pilot" else "final"
    rows = read_rows(root / f"{stage}-{split}-results.jsonl")
    cases = json.loads((root / f"{split}-questions.json").read_text())
    expected = {(c["qid"], a) for c in cases for a in ARMS}
    actual = [(r["qid"],r["arm"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("incomplete or duplicated generation coverage")
    report = {"n_questions":len(cases), "source_groups":len({c["group"] for c in cases}), "by_arm":{}}
    costs = {a:sum((response_cost(r["raw_response"], "deepseek-flash", tariffs) for r in rows if r["arm"]==a), Decimal(0)) for a in ARMS}
    for arm in ARMS:
        rr = [r for r in rows if r["arm"]==arm]
        report["by_arm"][arm] = {"n":len(rr), "valid":sum(r["valid"] is True for r in rr),
            "latency":latency_summary(rr), "generation_cost_usd":float(costs[arm])}
    if split == "repeat":
        return report, rows, {}, {}, costs
    primary_rows = read_rows(root / f"{stage}-{split}-primary-judge.jsonl")
    secondary_rows = read_rows(root / f"{stage}-{split}-secondary-judge.jsonl")
    primary, secondary = scores(primary_rows), scores(secondary_rows)
    if set(primary) != expected or set(secondary) != expected:
        raise ValueError("judge coverage does not match generation")
    gen = {(r["qid"],r["arm"]):r for r in rows}
    conjunction = {k: all(s[k][a]==2 for s in (primary,secondary) for a in AXES)
        and all(s[k][b] for s in (primary,secondary) for b in BOOLS)
        and gen[k]["valid"] and gen[k]["complete"] for k in expected}
    judge_cases = {r["qid"]:r for r in json.loads((root / f"{split}-judge-cases.json").read_text())}
    paired_cost = sum((response_cost(r["response"], "deepseek-v4-pro", tariffs) for r in primary_rows),Decimal(0))
    for arm in ARMS:
        sec_cost = sum((response_cost(r["response"],"deepseek-v4-pro",tariffs) for r in secondary_rows if r["arm"]==arm),Decimal(0))
        costs[arm] += sec_cost + paired_cost / 2
        rr = [r for r in rows if r["arm"]==arm]
        out = report["by_arm"][arm]
        out.update(primary_adequate=sum(primary[(r["qid"],arm)]["adequate"] for r in rr),
                   secondary_adequate=sum(secondary[(r["qid"],arm)]["adequate"] for r in rr),
                   both_adequate=sum(conjunction[(r["qid"],arm)] for r in rr),
                   all_in_cost_usd=float(costs[arm]), all_in_per_question_usd=float(costs[arm]/len(cases)))
        for name, judge in (("primary",primary),("secondary",secondary)):
            out[name+"_axes_fully_satisfied"] = {a:sum(judge[(r["qid"],arm)][a]==2 for r in rr) for a in AXES}
            out[name+"_citation_entailment"] = sum(judge[(r["qid"],arm)]["citation_entailment"] for r in rr)
        refused = [r for r in rr if any(s.get("text")=="本次资料未包含回答该问题所需的依据。" for s in (r.get("answer") or {}).get("sentences",[]))]
        out["fixed_phrase_refusals"] = len(refused)
        out["refusals_on_source_answerable_cases"] = sum(judge_cases[r["qid"]].get("stratum") not in ("unanswerable","regression") for r in refused)
    report["quality_cluster_bootstrap"] = grouped_quality_bootstrap(rows,conjunction,ARMS)
    improved = [c["qid"] for c in cases if not conjunction[(c["qid"],"C1")] and conjunction[(c["qid"],"C3B")]]
    regressed = [c["qid"] for c in cases if conjunction[(c["qid"],"C1")] and not conjunction[(c["qid"],"C3B")]]
    n = len(improved)+len(regressed)
    p = min(1.0, 2*sum(math.comb(n,k) for k in range(min(len(improved),len(regressed))+1))/2**n) if n else 1.0
    report["paired_transitions"] = {"improved":improved,"regressed":regressed,"mcnemar_exact_p":p}
    report["judge_disagreements"] = [{"qid":q,"arm":a,"primary_issue":primary[(q,a)]["issue"],"secondary_issue":secondary[(q,a)]["issue"]}
        for q,a in sorted(expected) if any(primary[(q,a)][f]!=secondary[(q,a)][f] for f in AXES+BOOLS)]
    report["cost_scope"] = "Generation + secondary judge + half paired primary judge; pinned conservative tariff accounting, not provider invoice."
    return report, rows, primary, secondary, costs


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--profile",required=True,type=Path)
    args=parser.parse_args(); root=_ensure_outside_repo(args.root,"Private report")
    profile=json.loads(args.profile.read_text()); manifest_path=Path(profile["manifest_path"])
    manifest=json.loads(manifest_path.read_text()); tariffs=manifest["models"]
    for freeze in root.glob("*freeze.json"):
        for path, digest in json.loads(freeze.read_text()).get("hashes", {}).items():
            if sha(path) != digest:
                raise ValueError("frozen experiment artifact changed")
    reports={}; qa=[]; all_cost=Decimal(0); files=[]
    for split in ("pilot","final","regression","repeat"):
        rep,rows,primary,secondary,costs=section(root,split,tariffs);reports[split]=rep;all_cost+=sum(costs.values())
        if split in ("final","regression"):
            by={(r["qid"],r["arm"]):r for r in rows}
            for c in json.loads((root/f"{split}-questions.json").read_text()):
                qa += [f"## {split}: {c['qid']}","",c["question"],""]
                for arm in ARMS:
                    r=by[(c["qid"],arm)];p=primary[(c["qid"],arm)];s=secondary[(c["qid"],arm)]
                    qa += [f"### {arm}","", "\n".join(x.get("text", "[invalid sentence]") for x in (r.get("answer") or {}).get("sentences", []) if isinstance(x,dict)) or "[invalid or absent answer]","",
                        f"主评 adequate={p['adequate']}；复评 adequate={s['adequate']}。",
                        f"主评意见：{p['issue']}",f"复评意见：{s['issue']}",""]
                    for sentence in (r.get("answer") or {}).get("sentences", []):
                        for cit in sentence.get("citations",[]):
                            qa += [f"- 引文 {cit['id']}：{cit['quote']}",""]
    budget=json.loads((root/"budget-freeze.json").read_text());charged=Decimal(0);opened=0
    for stage in ("dev","final"):
        state=json.loads((manifest_path.parent/f"ledger.{stage}.json").read_text())
        charged+=Decimal(str(state["totals"]["charged_cost_usd"]));opened+=state["totals"]["open_reservations"]
    delta=charged-Decimal(budget["baseline_current_ledgers_usd"])
    if opened or abs(delta-all_cost) > Decimal("0.00000001"):
        raise ValueError("unreconciled canonical ledger or open reservation")
    if delta > Decimal(str(budget["additional_cap_usd"])) or charged+Decimal(budget["prior_spend_usd"]) > Decimal("100"):
        raise ValueError("budget cap exceeded")
    reports["accounting"]={"new_charged_usd":str(delta),"response_accounted_usd":str(all_cost),
        "unattributed_difference_usd":str(delta-all_cost),"cumulative_usd":str(charged+Decimal(budget["prior_spend_usd"])),
        "open_reservations":opened,"additional_cap_usd":budget["additional_cap_usd"]}
    a,b=reports["final"]["by_arm"]["C1"],reports["final"]["by_arm"]["C3B"]
    delta_pp=100*(b["both_adequate"]-a["both_adequate"])/reports["final"]["n_questions"]
    latency_ratio=b["latency"]["p95_ms"]/a["latency"]["p95_ms"]
    regression_losses=reports["regression"]["paired_transitions"]["regressed"]
    lower_bound=reports["final"]["quality_cluster_bootstrap"].get("ci95",[-1,1])[0]
    passed=delta_pp>=5 and lower_bound>0 and latency_ratio<=1.1 and b["valid"]>=a["valid"] and not regression_losses
    reports["decision"]={"promote":passed,"adequacy_delta_pp":delta_pp,"p95_ratio":latency_ratio,
        "regression_losses":regression_losses,"cluster_ci_lower_above_zero":lower_bound>0,"note":"Threshold crossing is not statistical proof; inspect cluster uncertainty and human-ground-truth limitations."}
    reports["artifact_sha256"]={p.name:sha(p) for p in sorted(root.glob("*.json*")) if p.name not in ("profile.json","authoring.json")}
    write_new(root/"comparison-metrics.json",reports)
    with (root/"chinese-qa-review.md").open("x",encoding="utf-8") as f:f.write("# 私有中文问答与评审对照\n\n模型评分不是人工金标准；旧回归与新问题分开。\n\n"+"\n".join(qa))
    lines=["# C1 / C3B frozen comparison", "", "Decision: "+("candidate passes the prespecified point-estimate gate; no deployment" if passed else "retain C1; C3B does not meet the prespecified promotion gate"), "",
        "| Split | Arm | Valid | Primary adequate | Secondary adequate | Both adequate | p50 ms | p95 ms | All-in USD |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for split in ("pilot","final","regression"):
        for arm in ARMS:
            r=reports[split]["by_arm"][arm];n=r["n"]
            lines.append(f"| {split} | {arm} | {r['valid']}/{n} | {r['primary_adequate']}/{n} | {r['secondary_adequate']}/{n} | {r['both_adequate']}/{n} | {r['latency']['p50_ms']} | {r['latency']['p95_ms']} | {r['all_in_cost_usd']:.6f} |")
    lines += ["", "## Prespecified latency repeat", "", "| Arm | Cases | p50 ms | p95 ms | Generation USD |", "|---|---:|---:|---:|---:|"]
    for arm in ARMS:
        rr=reports["repeat"]["by_arm"][arm]
        lines.append(f"| {arm} | {rr['n']} | {rr['latency']['p50_ms']} | {rr['latency']['p95_ms']} | {rr['generation_cost_usd']:.6f} |")
    lines += ["",f"Fresh-final both-judge difference: {delta_pp:+.1f} percentage points. C3B/C1 p95 ratio: {latency_ratio:.3f}.",
        "Cluster uncertainty: `"+json.dumps(reports["final"]["quality_cluster_bootstrap"])+"`.",
        "", "## Accounting", "",json.dumps(reports["accounting"],indent=2),
        "", "## Interpretation and limits", "",
        "The final set has 19 condition questions, 7 comparisons, 6 scope questions, 4 factual controls, 1 numerical case and 3 unanswerable cases across 9 source groups. Most questions name the source/provision and explicitly request facets: this is easier and less natural than vague open-ended user questions. The sample poorly tests numeric generalization and cross-page evidence acquisition. A ceiling score cannot establish robustness or equality of true accuracy. A [0,0] bootstrap interval at the observed ceiling is degenerate, not an equivalence proof.",
        "", "Post-hoc assistant source spot-check (source-spot-check.md) flags a missing completed-project qualifier in C3B and a prior-year project qualifier omitted by both answers and the authored reference. Both judges accepted them. Frozen scores are retained; these are non-human adjudication concerns, not hidden score corrections.",
        "40 new assistant-authored Chinese final questions; previously exposed corpus. Pilot/final source groups were separated, eight overlapping draft topics replaced before freeze. This is not a new-corpus generalization test, an exhaustive semantic contamination audit, or human gold. References were checked against screened text; original OCR/page fidelity was not independently certified. Inference used the four-field question view and never received reference answers.",
        "", "Primary and secondary passes use the same approved deepseek-v4-pro model with paired versus pointwise rubrics. They share model biases; agreement does not establish correctness. No candidate changes after freeze. Generator: deepseek-flash, thinking disabled; randomized interleaved sequential arm order. Latency includes worker startup/retrieval/validation, one trial per fresh case; the nine-case preselected repeat is separate in metrics. Provider cache/load and sampling remain confounders.",
        "", "Historical 60-question results remain exposed diagnostics only. A first clause variant failed prompt budgets (46/60); packed C3B was fixed before this dataset. Numeric utilities were not used in generation. The report must not attribute numeric performance to them.",
        "", "The exposed regression has three arm/case rubric disagreements: REG-FAQ-01 for C1 (a completeness judgment) and REG-UNSUPPORTED-01 for both arms (the pointwise judge penalized an appropriate refusal for failing to supply unavailable information). These are measurement concerns, not validated model failures. No judge disagreement occurred on the fresh final set. Fixed-phrase refusal counts are only a lexical proxy: C3B also declined the third unanswerable final case using a supported explanation without the fixed sentence. Both arms declined all three on assistant inspection; this is not independent human adjudication.",
        "", "See `comparison-metrics.json` for axis counts, citation support, refusal proxy, paired changes, judge disagreements, latency repeat and artifact hashes. See `chinese-qa-review.md` for every fresh and regression answer with exact cited text and both judge comments. These files remain private."]
    with (root/"report.md").open("x",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
    print(json.dumps({"decision":reports["decision"],"accounting":reports["accounting"]},indent=2))


if __name__=="__main__": main()
