# Continuing optimization evidence log

Goal and stopping rules: [OPTIMIZATION_GOAL.md](../OPTIMIZATION_GOAL.md).
C1 is still default; no deployment or publication retry is authorized here.
Private results are retained outside this repository; code and tests remain here.

| Experiment | Hypothesis / split | Evidence | Decision |
|---|---|---|---|
| C2P historical | More context/longer answers; exposed 60 | Both-judge adequacy 36/60 vs C1 44/60, p95 2.041 vs 1.931 s | Negative; do not use as fresh test |
| C3B-v1 | Exact clause handles without packing | 46/60 exposed prompts exceed fixed request cap | Reject mechanically |
| C3B-v2 | Packed complete clauses; frozen fresh 40 | 40/40 vs 40/40, p95 +6.6%; source audit reveals missed conditions | No promotion; ceiling not plateau |
| R1 source review | Fresh-context model sees only question/source on nine exposed cases | Finds scope concerns, but copies a schema placeholder into several obligation fields | Not usable as automatic gold; preserve raw output |
| R1 blinded answer review | 41 anonymous original/control answers | Misses explicit condition reversal and several omissions; false alarm on a complete control | Reject as promotion judge |
| R2 atomic review | Per-obligation status plus exact answer span; same development controls | In progress; separate frozen unseen semantic controls required | No paid candidate generation until diagnostic gate passes |
| C4Q proposed ablation | Targeted material-scope self-check; same C1 retrieval/schema/caps | Prepared offline on exposed development cases | Await calibrated review gate |
| C4N proposed ablation | Two adjacent pages replace low-ranked chunks; same top-8 cap | Prepared offline; no oracle source IDs | Await calibrated review gate |

Local review flags now cover narrow negated-obligation and refusal-followed-by-
positive-payment-assertion patterns. They remain review hints, not general
semantic correctness or automatic answer repairs. Constructed negatives and
legitimate uncertainty statements are tested separately.

R2 has a preregistered 20-control unseen diagnostic gate: identify all eight
explicit constructed errors, at most one false alarm among twelve complete or
paraphrased controls, and all outputs must satisfy the schema/quote contract.
Those controls are assistant-authored/source-checked, not human gold. Passing
supports further diagnostic work, not general judge validity. Failed controls
become development data; never silently retest them as unseen.

Paid work uses the existing canonical ledgers, original cumulative $100 ceiling
and nested allocation, with durable dispatch journals and no retries. The
remaining authorization deadline and budget are operational boundaries, not
scientific stopping criteria. No practical plateau has been established.
