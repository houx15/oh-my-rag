# Original-question experiments completed, 2026-10-13

The strongest observed improvement is domain-specific: 牛黄 rises from90/315 to
155/315 primary Flash passes with fixed retrieval, focused answers and a strict
boundary compiler. 光明 does not support the same global change: live-question
passes fall60→58/113 and the reserved subset falls32→27/40. Keep its C1 baseline.
A separate, deterministic catalogue-count experiment improves9→14/17 original
光明 questions. These are exposed-development, model-judged results, not human-gold
accuracy, an untouched holdout, paper reproduction or an all-pass claim.

## Completed comparisons

All questions retain their original wording. Scoring rubric and source validators
are unchanged. Invalid or unscored outputs remain in the denominators.

| Ablation and comparator | 牛黄 | 光明 | Decision |
|---|---|---|---|
| Answer-focus vs original, fixed retrieval | 90→154/315;82 gains,18 losses | 21→22/30;3 gains,2 losses | Promising 牛黄 candidate;30 mechanical failures |
| Lexical pool + model selector vs answer-focus | 13→14/24;4 gains,3 losses | 9→10/12;2 gains,1 loss | Marginal; extra call; not default |
| Typed boundaries, targeted diagnostic sample vs answer-focus | 17→21/60;9 gains,5 losses | 7→7/12;1 gain,1 loss | Enriched sample, not population estimate |
| Focus + typed-v2, complete comparison vs original | 90→155/315;81 gains,16 losses | 218→222/330;28 gains,24 losses | Do not promote across domains |
| Query hypotheses + source-only fusion vs typed-v2, same pilot IDs | 10→11/24;5 gains,4 losses | 9→10/12;1 gain,0 losses | Small mixed effect; extra call; not default |
| Derived catalogue counts + original C1 vs original C1 | Not applicable | 9→14/17;5 gains,0 losses | Promising narrow counting experiment; confirmation pending |

Full typed-v2 detail:

| Cohort | Original pass | Candidate pass | Candidate invalid | Unscored |
|---|---:|---:|---:|---:|
| 牛黄 original live205 |55|108|6|0|
| 牛黄 supplied evaluation110 |35|47|4|0|
| 光明 original live113 |60|58|0|0|
| 光明 supplied simulation217 |158|164|1|2|
| 光明 reserved40, overlapping the above |32|27|1|0|

The reserved40 had already been exposed to original evaluation; reserving them
from later tuning did not make them an untouched natural holdout. They have now
been consumed. The later17-case counting experiment includes previously exposed
cases and is explicitly exploratory. All known eligible originals have been
exposed. New natural dialogue and independent source adjudication are needed for
confirmation. The separate20 C1 contract regressions from the original full run
are not included in the645-case semantic comparison; offline tests do not turn
those into a fresh paid end-to-end safety evaluation.

## What the changes actually do

`answer_focus.py` adds a system suffix for direct answers, subject/scope fidelity,
historical attribution and appropriate abstention. Original retrieval is fixed.
`typed_boundaries.py` permits explicit boundary enums compiled to existing fixed
protocol strings. `typed_boundaries_v2.py` additionally normalizes redundant exact
boundary text or empty citations, while rejecting differing factual text, unknown
fields and nonempty citations. It does not launder arbitrary uncited claims.
Nine previously saved outputs were repaired without regenerating. The full run
reuses72 generations and63 unchanged reviews; it makes573 new generations and582
reviews. Ten 牛黄 and one 光明 mechanically invalid answers remain.

`evidence_pool.py` uses source-only lexical identity/body channels;
`query_plan.py` generates at most two uncertain retrieval hypotheses, retains the
original question, and does not guess missing dialogue. References never enter
these inference interfaces. The pilot does not reproduce CQC-RAG's confidence
estimator. Its latency and regressions do not justify default integration.

`catalogue_counts.py` counts source rows with row-locator and text-hash provenance,
reports distinct names and duplicates separately, and marks its evidence card as
computed rather than an original quotation. The experiment prepends one card and
retains seven original C1 context records, with the original generation prompt.
The screened catalogue has381 rows,379 distinct names, two duplicate-name extra
rows, and category counts166/171/44. These are catalogue counts, not the number
of all achievements in a city or on a publication platform. There is no per-case
answer lookup. Three remaining failures concern an ambiguous institution name
and platform publication totals beyond this catalogue. No failed scores were
recoded to create the improvement.

## Source and measurement reliability

The raw workbook has organization values in all381 rows. The screened derivative
omits131 because known contact-name substrings match institution names; redaction
inserts a marker containing 联系人 and a subsequent filter drops the entire line.
This is a verified preprocessing loss, not missing data in the workbook. The
experiment uses only screened fields and reports131 unknown organization values;
no contact dictionary or private contact columns were sent to model providers,
no denied strings were restored, and privacy checks were not weakened. A future
field-aware repair needs separate privacy review and a frozen re-extraction.

The supplied-reference overlap proxy for315 牛黄 questions is179 with at least one
reference in selected context,228 in the original top20 pool,230 in lexical rescue;
290 have supplied reference IDs. This is not gold retrieval recall. A balanced
40-live-case source audit is selected, but formal annotation of all40 is unfinished.
Nine diagnostic annotations distinguish retrieval misses, ungrounded reference
assumptions, missing dialogue and out-of-interface action requests. Some generic
biographies are penalized for unasked details. Promotional medical text cannot
establish modern clinical facts. Primary generation and scoring share Flash;
source-reviewed human calibration remains necessary. The earlier independent80
judge comparison had18 disagreements and does not validate this candidate.

The prior 光明 handle-order harness error is repaired by `ordered_context.py`.
All20 saved generations were reconstructed using original retrieval order and
freshly reviewed; invalid old reviews are retained as invalid comparisons.

## Resources, latency and accounting

Nearest-rank p95 below measures generation-stage work only. Query planning includes
its extra planning call and local retrieval; judges are excluded. Full typed and
focus summaries include reused generations. They are not matched full-pipeline
latency estimates and must not be compared directly with historical end-to-end p95.

| Experiment | Measured calls | Actual billed USD | Generation-stage p95 NH / GM |
|---|---:|---:|---|
| Answer-focus continuation |371|0.38291160|2.441s /2.333s|
| Evidence-selection pilot |108|0.12478590|Not summarized here|
| Targeted typed pilot |144|0.15451560|Not summarized here|
| Full typed comparison |1155|1.38216480|2.452s /2.253s|
| Query-plan pilot |108|0.08879520|3.873s /3.635s|
| Catalogue-count pilot |34|0.03998670|— /2.491s|

Cumulative spend is **$36.97890735 of the authorized $200 total**, carrying every
historical ledger, including earlier runs not listed in this table. Completed
ledgers have zero retries and zero open reservations. Actual API responses report
`deepseek-flash`; the provider alias was verified as V4.1 Flash on October13.
The requested working Codex model/effort is not exposed by tools, so no verified
runtime switch is claimed. A counting-run launch path error stopped before any
new dispatch; its zero-spend allocation and failure record are preserved, followed
by a newly frozen corrected allocation. No paid calls were duplicated.

All new implementations use the existing CPU/runtime; no GPU training or new
packages were required. The complete offline suite passes385 tests in normal
and optimized Python modes. No production default was changed or deployed.
No upstream source code or prompts were copied, installed or executed. README
credits only concepts actually used and distinguishes unverified code licenses.

## Next decision

Keep the original 光明 global prompt. Carry the 牛黄 focused/typed candidate and
narrow catalogue-count route into a new natural-question confirmation set only
after sources and dialogue are sufficient. Prioritize field-aware source repair
and missing-session recovery before another broad model call. A small, explicitly
oracle-labeled evidence diagnostic could separate remaining retrieval from
reasoning failures; its reference inputs must never enter production inference.
The current results establish useful improvements and concrete blockers, not
all-pass performance or a novel academic method.

Private evidence remains outside Git under
`/Users/monkey/Documents/Codex/2026-10-12/task/` in
`answer-focus-resume-20261013/`, `evidence-selection-cycle-20261013/`,
`typed-boundary-cycle-20261013/`, `full-typed-cycle-20261013/`,
`query-plan-cycle-20261013/`, `catalogue-count-cycle-corrected-20261013/`, and
`original-source-audit-20261013/`. No uploads, GitHub push or deployment occurred.
See [the literature-to-failure matrix](research-cycle3.md) for original-paper,
publication-date, repository-license and reproducibility checks.
