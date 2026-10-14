# Cycle13: selection-only ablations over frozen keyword hypotheses

Completed2026-10-14. Reused all20 saved Cycle12 Qwen query outputs; **zero new
keyword calls**. Original questions, source snapshot, generator, canonicalization,
context count and original protected half were held fixed. Two new local selectors:
equal reciprocal-rank fusion (original lexical view plus each hypothesis, removing
the duplicated/double-weighted baseline vote) and greedy marginal query-token
coverage, with corpus-only document frequencies. Both arms use exactly the same
candidate views and new-record window rule; existing baseline windows are preserved.
No reference answers, expected source IDs or case-specific overrides enter inference.
No external code, new dependency, weights or prompts were adopted.

## Results and decision

| Configuration | Raw judge pass /20 | Unscored | Assistant source-usefulness /20 | Valid /20 | Component-sum p50 /p95 |
|---|---:|---:|---:|---:|---|
| Cycle12 baseline |8|0|9|19|4.568 /6.140s|
| Cycle12 vocabulary |10|1|9|19|4.561 /7.020s|
| Cycle12 small_model weighted fusion |6|0|12|20|7.912 /11.299s|
| Cycle13 equal_rrf |9|0|9|19|7.896 /9.856s|
| Cycle13 token_coverage |8|0|10|19|8.767 /10.431s|

**Neither new selector establishes improvement over the earlier small-model arm.**
Equal fusion has one source-reviewed gainGM064 and four lossesR034,GM125,R095,
GM128 versus that arm. Token coverage has zero gains and two lossesR095,GM125.
Against Cycle12 baseline, equal fusion exchangesGM064 gain forGM128 loss; token
coverage gainsR034 with no observed source-usefulness losses on these20. C1 remains
default; no selector is promoted. These are20 exposed original questions,10 per
corpus, not a fresh generalization test or human-gold accuracy. All40 new outputs
received label-masked source review by the same assistant with prior context.
Borderline phonetic/clarification decisions use the unchanged Cycle12 standard.

Cycle12 and13 are noncontemporaneous paired observations.40 new answers have36
unique prompts;7 match the earlier weighted small-model prompt exactly. Stochastic
differences on identical prompts are not algorithmic evidence. No replicate-based
uncertainty claim or causal latency improvement is made. All times sum staged
measured critical-path components including the saved keyword latency; cold startup,
uncached embedding time, offline judges and stage idle time are excluded. Maximum
new component sums10.021/12.403s; no new output exceeds20s.

## What selection did and did not repair

Both new selectors recover GM064’s D30:1:01 catalogue summary, which the weighted
selector dropped. Equal fusion generates a useful scoped research/catalogue answer.
Token coverage also recovers that source but still adds a20%/500万元 subsidy without
its new-materials applicability: **better selected evidence is not sufficient**.

Neither recovers the N417 valuation target. Existing tokenization emits很贵 as one
token, absent literally from source, so the coverage scorer drops it; generic传承/
评价 coverage selects irrelevant biographical material. The synthetic single贵 test
passes, but does not guarantee real-tokenizer semantic coverage. This negative result
is retained without post-test tuning. R065’s possible夜啼 sources remain outside
all candidate pools; selection cannot recover them. GM420 remains unresolved.

Equal fusion loses GM128 to blanket abstention. Both new arms lose R095 at delivery:
raw clarifications are useful, but one mixes text with boundary and one uses an
uncited free-form sentence. Neither meets the declared contract. These are PROTO
failures with intent/format secondary tags, not retrieval failures. Do not weaken
the validator or count undelivered text as success. GM125 equal fusion supplies
facts but drops2% reward exclusions and500万元 talent-team scope; token coverage
abstains despite relevant selected facts. R034 equal fusion misattributes unsigned
牛病 text, while token coverage preserves attributed claims.

A fresh local exact-substring check covers **293 delivered citations across100
output records** (20 questions repeated in5 arms;4 invalid outputs have no delivered
citations):0 nonexact. This does not certify entailment, scope or speaker attribution.
`quotation-check.json` contains per-citation results; it is distinct from the
unverified historical1206 tally.

## USE investigation and next step

The [canonical technical report](technical-report.md) contains the requested
prompt→raw→parsed→delivered trace for6 representative saved outputs. Five valid
answers retain every raw factual sentence; the sixth is a genuine mixed-boundary
rejection. Historical GM124 false abstention originates in generation despite
selected safety-system evidence. Historical N265 likewise ignores historical
valuation; current-price and missing-antecedent ambiguity remain secondary tags.
Cycle12 R021 lacks an actual explanation in selected evidence and must not be
“fixed” by inventing interpretation.

Next controlled experiment should isolate **generation instructions**: explicitly
separate unavailable display actions from supported explanation, preserve policy
qualifiers and distinguish historical facts from current data. Hold selected
contexts/model/schema/validator fixed; include source-use failures and clean,
missing-context/current-price controls. Freeze new checks before outcomes. A schema
change, if justified, is a separate factor with parser regression tests. A larger
40-original confirmation of keyword retrieval is deferred because selection changes
did not beat the earlier pilot; it is not silently reported as completed.

## Accounting and reproducibility

40generation +40unchanged-judge calls completed,0retries,0unknown usage,0preflight
blocks and0open reservations. Cycle13 conservative increment0.594322;
cumulative **83.49996345/200USD**. Cycle12+13 together219paid calls and1.4680472
increment. Existing numeric-CNY-as-USD reservation convention is conservative,
not FX or actual invoicing. Prior spend and all ledger-chain hashes preserved.
145 frozen scope hashes plus all frozen input provenance hashes verified unchanged.
483offline tests and10focused optimized-Python checks pass. No deployment, push,
upload, new provider, privacy-screen exemption or unrecognized code execution.

Code: `newdomain/keyword_selection.py`, `scripts/prepare_keyword_selection.py`;
runner `scripts/keyword_experiment.py`; four new meaningful tests in
`tests/test_keyword_selection.py`. Preparation requires the authorized local
Cycle10 runtime and caches, and exact Cycle12 inference artifacts. The runner’s
existing allocate helper does not automatically discover new selector files; this
cycle’s explicit allocation included all new selector/preparer/test paths and the
40-job file. Do not start future paid work without re-freezing every dependency.

Local artifacts: `/Users/monkey/Documents/Codex/2026-10-12/task/keyword-selection-cycle13-20261014/`.
`plan.md`, `input-provenance.json`, `answer-jobs.json`, `answers/`, `summary.json`,
`source-review-summary.json`, `source-review.md`, `target-selection-diagnostic.json`,
`verification.json`, `quotation-check.json` and the four-column `report.html` retain
all observations. The main presentation shows one coherent unpromoted Cycle12
small_model configuration’s20answers; the appendix contains all100outputs and
preserves the five historical tables byte-for-byte. No per-question best-arm mix.
