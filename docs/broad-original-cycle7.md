# Broad original-question regression — October 14, 2026

The frozen combined candidate completed all318 original questions:113 Guangming
and205 Niuhuang.55 changed Guangming prompts received separate baseline calls;
263 identical-prompt cases share one output. This produced373 answers and373
unchanged-rubric reviews,746 paid requests, with no retries or unknown usage.
The candidate remains unpromoted. These exposed originals are broad regression
evidence, not an untouched external generalization set or human-gold accuracy.

| Unchanged primary model scores | Baseline | Candidate |
|---|---:|---:|
| Changed Guangming prompts |30/55|34/55|
| All Guangming originals, including58 common outputs |60/113|64/113|
| Niuhuang originals, all common outputs |80/205|80/205|
| Assembled total, including263 common outputs |140/318|144/318|

Only the55 changed prompts are independently paired. Eight raw gains and four
raw losses are one generation/judgment per arm, with no model-noise estimate or
prespecified noninferiority margin. The assembled totals are not two independent
full-system runs. Both generation and judgment use `deepseek-v4.1-flash`, so the
judge is not independent of the generator. Raw/historical scores are unchanged.

## Source audit and negative results

Assistant source review covers all55 pairs and39 Niuhuang cases:32 selected by
deterministic case-ID hash plus7 targeted diagnostics. Selection does not use
scores, but one hash-selected case overlaps the already observed pilot. Review
is source-visible and not blinded or human gold. The39 annotations contain11
clear source-supported cases,8 genuine failures,4 false failures and16 qualified,
ambiguous or disputed cases; these categories are not an adjusted accuracy rate.

Confirmed examples include the108/381 application-field mode (28.35%), conditional
19-row laboratory count, correct-property transport evidence, and separating the
platform's over1000 online achievements from the381-row institutional catalogue.
GM050's raw gain is not confirmed: equivalent topic summaries were judged with
different clarification requirements. GM015/016/038 losses use inconsistent
reference/example requirements; GM046 is an incomplete question fragment.

GM089 is a definite baseline false pass: its answer says materials are **not**
the smallest category while listing44<166<171; the judge awards full marks.
The candidate correctly says materials are smallest. This source/arithmetic
gain is invisible to the binary model score. Unlike historical GM161, the
closed three-category comparison leaves no scope ambiguity.

Important remaining failures:

- GM048 retrieves−4F–42F but fails to decode42 above/4 below/46 total. Cycle6's
  narrow source-recovery criterion was met, not full original-question adequacy.
  Its separate nine synthetic wording checks remain6/9→8/9; H05's floor-range
  trigger miss is visible and was not tuned.
- GM067's incubator/entity relationship is awkward and ambiguous; GM170 weakens
  the platform subject into science-city wording.39/55 pairs keep the same
  evidence-ID set,16 change it: restoration, ranking and operators are not
  causally separated by this combined experiment.
- Six common-prompt delivery failures remain: one Guangming invalid handle list;
  Niuhuang malformed schema, invalid segment handle, title attribution rejection
  and two rejected free-form clarifications. No failed output was regenerated.
- Niuhuang misses book/formula/person coverage and confuses collection inventory
  with a book's internal bibliography. A current advice request can still receive
  historical procedures without the appropriate personal-use boundary.
- Navigation requests are not exercised by this text-only harness. OCR wording,
  legendary history and some corpus metadata remain independently unverified.

The main report therefore preserves the reference configuration and labels this
candidate as a measured research arm, not a newly validated production default.
No definite factual regression was established in the four raw model-loss pairs;
this does not prove overall non-regression or remove the above limitations.

## Latency and accounting

Across373 actual warm retrieval-to-validation chains: p50 **3.551s**, p95
**4.720s**, maximum **5.674s**, zero over20s. Guangming candidate p95 is4.410s;
Niuhuang common-output p95 is4.875s. Offline judging, UI/TTS and uncached embedding
network time are excluded. All205 Niuhuang cached retrievals reproduce the saved
contexts; embedding vectors/score outputs were checked finite and an independent
dot-product calculation agreed within1.34e-15 despite BLAS runtime warnings.

Main-stage initialization is3.564s from inside `main`, including subsequent
imports/index/cache work. Interpreter startup, earlier imports and later
profile/DNS preflight are outside that timer; it is not full cold user latency.
OS disk-cache state is uncontrolled. No embedding API calls were made.

Known usage:2,319,825 input and79,086 output tokens, peak-rate estimate
**CNY5.272338**, without cache discounts. Cumulative conservative ledger:
**$74.45438025/$200**, zero open reservations, zero new unknown-usage settlements.
Earlier conservative unknown settlements remain. CNY estimates are booked at the
same numeric USD ceiling; this is neither FX conversion nor a provider invoice.

## Research connections and next coordinated changes

The existing [verified research matrix](research-cycle3.md) and README credits
remain applicable: bounded evidence coverage/selection conceptually relates to
S2G-RAG and CompSelect; judge reliability/validity motivates separate source audit.
No upstream implementation, prompt, weight or asset was copied or installed.
No new paper is credited as an implemented method, and no novelty claim is made.

Proposed separate files, not implemented in this frozen run: source-addressed
floor derivation, output-contract emission, and an ablation of stable baseline
ranking with restored source hydration versus reranking. Book/person/formula
coverage should be a separate retrieval ablation. Preserve H05, require source
provenance, do not whitelist arbitrary uncited claims, and freeze follow-on tests
before evaluating revised code. The prior rubric-rewording experiment was negative.

The [DeepSeek feature table](https://help.aliyun.com/zh/model-studio/deepseek-api)
marks structured output supported, while the linked
[structured-output documentation](https://help.aliyun.com/zh/model-studio/qwen-structured-output)
lists DeepSeek Pro for JSON Object and only Qwen variants for strict JSON Schema.
Checked October14: strict schema support for this exact model is not established;
plain JSON mode does not guarantee fields/types. No capability probe or provider
change was made.

## Private reproducibility evidence

Workspace `broad-original-cycle7-20261014` contains frozen jobs/pairs, runtime and
runner, per-phase manifests/ledgers/journals, raw responses, unchanged scores,
39 source annotations,55 paired inspections, delivery failures, context changes,
summary, SQLite-backed four-column report, and next-experiment proposal.
`verification.json` confirms coverage,37 frozen inputs per phase, response/journal
hashes, unchanged raw/historical scores and closed accounting. Report packaging
and structural checks pass; browser visual QA is unavailable. All373 answers are
present; old five answer tables remain byte-identical in the main-report portal.

No inference implementation changed during the broad run. This documentation
checkpoint does not rerun the unchanged439-test suite from cycle6. All artifacts
remain local; no upload, push or deployment occurred.
