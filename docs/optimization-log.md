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
| R2 atomic review | Per-obligation status plus exact answer span | First unseen controls: 7/8 errors, 0/12 false alarms; missed date inside compound criterion | Failed gate; those controls are now development data |
| R3 separate predicates | Same reviewer, independently checked source predicates | New frozen controls: 8/8 errors, 0/16 false alarms, 24/24 schema-valid | Limited diagnostic gate passed; not general validity |
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

Development generation completed 27/27 structurally valid outputs. Review then
exposed a false missing-condition judgment, incomplete evidence supplied to the
reviewer, and retyped-quote errors. The repaired source view includes all actually
retrieved passages; answer sentence IDs replace free-form copied quotes. Remaining
review disagreements and schema violations are unresolved evaluation outcomes,
not automatic candidate losses. A protocol disclaimer is not an unsupported
business fact. Candidate selection requires source adjudication, not raw counts.

A 16-question scenario holdout in four development-disjoint source families was
frozen before answers, with separate inference questions and source obligations.
The corpus and related topics were previously exposed; lexical overlap audit is
not a semantic independence guarantee. C1/C4Q/C4N are unchanged for this comparison.
Arm-masked assistant review packets preserve a private mapping; this masking is
not equivalent to a fully independent human reviewer. No plateau claimed.

## Completed continuation: 2026-10-13

The proposed C4Q/C4N experiments above are now completed. On the frozen 16-case
scenario set, raw pointer-review adequacy was C1 13/16, C4Q 14/16, C4N 14/16.
These are **diagnostic model judgments**, not defensible gold accuracy: source
review found an ambiguous question, unsupported payment substitution, and judge
false positives on exact protocol disclaimers. No default promotion follows.
Provider transport p95 was 2145/2103/2033 ms respectively; generation cost was
$0.0184434/$0.0190338/$0.0184197. These timings exclude retrieval.

An approved stronger-model ablation used identical C1 messages on those 16 cases.
It produced 12/16 schema-valid answers, p95 2973 ms, generation cost $0.07892412.
All four invalid outputs omitted the evidence key on an exact fixed protocol
sentence. A local, narrowly scoped normalizer repairs that contract discrepancy
in replay (16/16), without changing business facts, citations, or provider usage.
This adaptive replay is not a fresh model-quality gain. A report-only pricing fix
replaced an erroneous flash tariff with the manifest's actual requested-model
tariff; the original incorrect report is preserved privately.

A question-only missing-record guard was frozen before 20 new focused questions.
It routed 10/12 explicitly unavailable-record questions and 0/8 answerable policy
controls. Reusing unchanged baseline fallbacks yielded 20/20 valid hybrid outputs
versus baseline 19/20; the avoided failure was structural, not a demonstrated
factual hallucination. Two paraphrases fell through correctly. It matched none
of 330 exposed regression questions. Avoided calls are a counterfactual projection,
not measured new provider responses or a broad semantic quality improvement.

C8U explicitly distinguishes unknown premises from false premises. On an initial
12-case set and a separate 12-case confirmation, arm-masked assistant source review
found one clear C1 error corrected by C8U in each set. This is only two discordant
pairs (exploratory exact two-sided sign-test p=0.5); it does not establish broad
superiority. References in the initial set also had policy-scope and unrequested-
computation ambiguity. Confirmation raw judge totals were C1 12/12 versus C8U
10/12, while the judge missed C1's premise error and incorrectly flagged two C8U
protocol sentences. Confirmation generation cost was $0.0142605/$0.0151281;
p95 was 1978/2112 ms. C8U remains experimental.

`newdomain.guardrails` exposes opt-in record routing and exact protocol normalization.
Local responses identify their deterministic origin and contain no fabricated model
usage. The existing C1 entry point remains unchanged. The uncertainty prompt and
all source-review tooling remain experiment scripts, not production deployment.

This continuation dispatched 456 provider jobs, including unsuccessful evaluator
calibration attempts, costing $1.24491114 at pinned conservative tariffs. Cumulative
spend is $29.94520233 of $100. Output usage matches the canonical ledger delta;
all dispatch journals reconcile, zero reservations remain open, and all eleven
historical ledger hashes match. No provider retry was used.

**No practical plateau is established.** Several inexpensive changes lack reliable
broad gains; narrow contract fixes are reproducible, and premise reasoning remains
promising. Next priorities are policy/version applicability resolution, a separate
calibrated evaluation family, and a larger preregistered premise test with paired
source-family uncertainty. Training or a new provider is not implicitly approved.
Human review would improve validity but is not a prerequisite for continued
independent work. An authorization deadline or publication block is not a plateau.
