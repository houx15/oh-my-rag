# Cycle14: fixed-evidence generation checklist

Completed2026-10-14.20 retained originals: all10 historicalUSE cases,2scope cases,
8controls. Independent pre-run selected-evidence review:7sufficient-targeted,
4conditional,5limited,4missing-requested-information/referent. Historical labels
do not establish current evidence sufficiency. Contexts/user messages identical
within pairs; only a generic system checklist changes. Same approved Bailian
`deepseek-v4.1-flash`, generation settings, schema, citation and boundary checks.

| Measurement | Fresh baseline | Checklist |
|---|---:|---:|
| Raw judge passes |6/20|9/20 +1unscored|
| Masked assistant source-usefulness |8/20|9/20|
| Excluding explicitly borderline passes |5/20|6/20|
| Mechanical validity |18/20|20/20|
| Actual warm end-to-end p50 |4.735s|4.749s|
| Actual warm end-to-end p95 |6.387s|7.705s|
| Maximum |8.081s|8.880s|

All40 outputs received masked assistant source review: same-model with prior
context, not human gold. Only source-usefulness gain: **GM124**, removing unsupported
UI-capability claims while retaining safety-system explanation. No observed binary
source-usefulness loss, but **no demonstrated content-USE rescue**. Not promoted.
Raw gainsN022,N353,GM127,N265 are not corresponding source gains. GM124 candidate
judge is unavailable, not a loss. Strata baseline→candidate: sufficient4→5/7,
conditional1→1/4,limited0→0/5,missing3→3/4. Borderline conditional-referent/phonetic/
minor-qualifier judgments remain explicit; sensitivity counts are not human truth.

## Trace: generation versus protocol

All38 valid outputs preserve every raw factual sentence. Baseline N265/R095 fail
the declared boundary/citation form despite raw clarification intent. Candidate
outputs become valid but respectively assign牛黄 to an unresolved它 and supply
unrelated facts: neither is a source-usefulness rescue. Format is not content.
GM071/072/126 still abstain despite concrete/limited/conditional selected evidence.
N170 recovers biography then incorrectly assigns答’s indication to牛黄. N325/N466
list properties instead of using historical forms and acknowledging limits of a
modern definition. R050 sources lack explicit phrase explanation. GM064/127 omit
policy relationships/qualifiers already present. These errors originate in raw
generation; validation did not delete a correct explanation.

Guangming permits2fixed uncited sentences and no typed clarification; Niuhuang
has exact standaloneclarify. Neither contract changes. This is a real constraint
for missing-context handling, not justification for accepting arbitrary uncited text.

## Timing, costs and verification

Each request repeats warm original retrieval/prompt construction, asserts exact
frozen evidence/prompt equality, generates and validates within one monotonic
interval. Cold initialization, uncached embedding network and judging excluded;
no keyword/embedding network calls. Unlike Cycle12/13, this is contiguous timing.
10NHsimilarity arrays and allcorpusvectors are finite; independent einsum agrees
within1e-12 despite NumPy warnings. No numeric code change.

80paid dispatches:40generation,39successfuljudges,1judgeReadTimeout after a saved
answer. No headers/events/usage for failedjudge; full conservative reservation
retained, rawscoreNone, answer source-reviewed, no retry. Increment**2.5678**,
cumulative**86.06776345/200USD**,0open reservations. Conservative accounting is not
invoice/FX.486regression and13focused optimized checks pass. No push/upload/deploy.

## Decision

Generic checklist insufficient. Cycle15 separately versions a task-focused prompt:
introductions use bounded relevant content; person questions use biography without
unrelated herb claims; definitions use identity/form within historical limits;
nonessential policies are omitted when conditions cannot fit. Source/model/schema/
validators remain fixed; fresh paired originals and controls required.

Eight independently authored same-source synthetic Cycle14 checks were frozen
(hash1b11019c68600c4a8167d0c0f831a6df23016978073dc546ec0b0767aa2fc6bd)
but **not run**, because meaningful content-use gain was not established. Retained
unrun, not discarded or reported as successes. No outputs exist to tune on.

Local artifacts: `use-prompt-cycle14-20261014/` under
`/Users/monkey/Documents/Codex/2026-10-12/task/`: fixedjobs,stage-trace,40masked
reviews,source-readiness,summary,ledger,judge-timeout,numeric-check and frozenchecks.
Exact code: `newdomain/evidence_use_prompt.py`, `scripts/run_evidence_use.py`.
[Canonical technical report](technical-report.md) retains keyword negative findings.
