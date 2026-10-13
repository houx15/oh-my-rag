# oh-my-rag

Chinese document-grounded QA research with explicit evidence handles, offline
validation, budgeted provider calls and paired evaluation.

This is a **research checkpoint**, not a production release or a demonstrated
research improvement. C1 remains the reference candidate. On the historical
60-question comparison, both-judge adequacy was **44/60 for C1 versus 36/60 for
C2P**, with p95 latency **1.931 versus 2.041 seconds**. The judges and OCR-derived
references are not human gold. Longer passages and answers regressed in that
trial; those questions are now exposed diagnostics.

## Latest measured checkpoint — October 13, 2026

[Focused repairs and actual end-to-end results](docs/focused-results-cycle6.md):
whole-table aggregation and targeted building evidence now have measured answer
benefits. On9 newly frozen synthetic phrasings, source-requirement checks improve
**6/9→8/9**, with2 gains and0 regressions. The remaining “楼层范围” trigger miss
is retained without tuning on that check. These share source/entities with
exposed development cases and use assistant source review, not human gold.

The development comparisons reach5/9→9/9 for aggregation and3/6→6/6 for building
facts after versioned refinements; source restoration supplies the platform/subset
distinction in3/3 targeted cases. Final prompts map to the earliest matching
successful checkpoints, never to the highest-scoring answer. C1 remains the broad
default; these methods are opt-in research candidates.

All **49 paid requests** completed with known usage,0 retries and0 responses over
20 seconds. Actual warm end-to-end timing (retrieval through validated answer,
excluding cache hits/cold startup/offline review) is **p50 2.996s, p95 4.274s,
maximum 5.215s**.11 byte-identical outputs were reused and excluded from timings.
The120s collection/125s parent deadline preserves the20s latency-failure threshold;
these under6s results do not prove the longer deadline caused service recovery.

Known-token peak-price estimate this cycle: **CNY0.317262**; new unknown-usage
settlements0. Cumulative conservative ledger: **$69.18204225/$200**, zero open
reservations, no active paid run. All prior settlements remain.439 tests pass in
normal and optimized Python modes. No deployment, push or artifact upload.

GM161 is now disputed in the primary audit:22 supported passes,0 definite false
passes,13 genuine failures,6 false failures,7 disputed/ambiguous. Both readings,
its original full score and the historical audit snapshot are preserved.

## Earlier focused experiments — October 13, 2026

[Focused experiment results](docs/focused-experiments-20261013.md): the revised
judge rubric did not improve agreement on12 source-reviewed controls (9/12 for
both rubrics), so it was rejected. Source restoration produced48/74 outputs
before transport failures; only16/37 pairs are complete. On those pairs the raw
judge passes11→13, with two source-supported repairs to platform-versus-subset
counts. This is an incomplete development experiment, not population accuracy.

The separate aggregation phase then failed before its first output. Four
successive network attempts across two questions, including one bounded retry
each, timed out at about61 seconds before response headers. Paid work stopped;
the frozen bounded-retrieval experiment remains unrun. Successful calls are
checkpointed; local journal-ID validation and pre-reservation DNS checks are fixed.
All430 offline tests pass in normal and optimized Python modes.

Cumulative conservative budget accounting is **$68.86478025 / $200**, with zero
open reservations and no active paid work. Unknown usage is settled at the full
bound; this is not verified invoice spend. Successful Bailian token usage is
priced in CNY and booked at the same numeric USD amount conservatively. Default
C1 remains unchanged; no push, deployment or artifact upload occurred.

The [timeout follow-up](docs/timeout-diagnosis-20261013.md) identifies the local
60-second read deadline as the terminating mechanism; the upstream cause remains
unproven. One115-byte diagnostic call subsequently succeeded in1.677s,17 input/6
output tokens, zero retries. It does not establish full-size workload recovery.
The follow-up includes actual Chinese Q/A/source/scorer examples and explains
why the lexical abstention flag alone cannot establish a false pass.

## Previous diagnostic checkpoint — October 13, 2026

The [fairness audit](docs/fairness-diagnostic-20261013.md) reviews48 original
questions from both datasets, balanced between original passes and failures.
Assistant source review now records22 supported passes,0 definite false passes,13 genuine
failures,6 false failures and7 disputed/ambiguous cases. GM161 was moved to the
disputed category; both readings and its original full score are preserved. This deliberately stratified
sample does not estimate population error rates; no original scores changed.
Prior40 source annotations plus this sample cover82 unique questions.

The complete saved report remains223/330 光明 and155/315 牛黄, with original-user
subsets65/113 and108/205. The fresh unified candidate is **incomplete:328/665**
reviewed. Bailian returned the exact `deepseek-v4.1-flash` model name, but later
requests timed out. A separate `qwen3.8-flash` three-case service check passed2/3;
it is not a full-dataset comparison. The source-restoration pilot stopped locally
before dispatch due to a journal-ID validation error, so it has no quality result.
Cumulative conservative accounting is$55.93499825/$200, with0 open reservations
and no active paid work. The original $100 cap was explicitly increased while
preserving all prior charges; the figures below are historical checkpoints.

The user declared corpus/project content public, including institution names and
the platform-count statement. Source derivatives remain local, credentials remain
secret, and there is no authorization to publish artifacts or push this repository.
The next experiments must separate evaluation repair, source restoration,
aggregation scope and bounded evidence retrieval. No overall improvement claim
is made from incomplete or exposed data.

## Historical original-question checkpoint

The [original-question evaluation](docs/original-question-evaluation.md) now
covers the supplied utterances without rewriting them. Fresh Flash primary
review passes are **60/113 (53.1%) for 光明 original live questions** and
**55/205 (26.8%) for 牛黄 original live questions**; completed-request p95 is
**2.379 s / 3.024 s**. Supplied simulation/evaluation questions are reported
separately. The old 牛黄 115/120 curated result did not establish real-user
performance. These strict model judgments are not human-gold accuracy.

All 665 generation outcomes and primary reviews are recorded; 168 exactly
unchanged 光明 generations were reused with their original timings. One stream
failure and one malformed review remain visible. Cumulative accounted cost is
**$34.41373425 / $100**, with zero open reservations or provider retries.
The newly authorized scope carries all prior accounting forward and retires
old admission; it supersedes the historical request-cap blocker below.
A preselected independent 80-case check is complete: 18 verdicts disagree;
17/20 regressions pass both judges. Full offline acceptance passes 356 tests in
both Python modes. The private presentation keeps only 光明 / 牛黄 sections and four columns;
case exports, source text and ledgers remain outside Git. No deployment or push.

## Run locally

Use Python 3.9 or later on macOS/Linux. The existing environment uses
`numpy==2.0.2`, `jieba==0.42.1` and `requests==2.32.5`; no new dependencies were
installed for this checkpoint. Live TLS/provider compatibility must be checked
in the intended environment before spending.

```sh
python -m newdomain.runner help
python -m unittest discover -s tests -p 'test_newdomain*.py'
python -m unittest discover -s tests -p 'test_research_methods.py'
```

The published synthetic tests require no private corpus or network. Other legacy
local suites can depend on private fixtures and are not a portable benchmark.
See [runner documentation](newdomain/README.md) and the
[research plan](docs/research-cycle3.md).

## Data and recovery

Private corpora, questions, ledgers and results are excluded from publication.
New-domain paths are explicit and external to the repository. Existing private
legacy files remain local. Code and reusable tests belong in this repository.

Paid entrypoints default to dry-run. Explicit `--live --profile` requires a
verified private authorization profile and existing canonical ledgers. Generation
and judging hold a run lock and journal dispatch before calling the provider.
`--resume` reuses only completed, hash-pinned results with unchanged inputs and
implementation. In-flight, failed, corrupt or unbound results require manual
investigation. Old unjournaled outputs are report-only. Final runs also require
`--freeze`. No automatic retry, deployment or artifact upload is provided.

## Research acknowledgments

The isolated tokenizer uses the existing [jieba 0.42.1](https://github.com/fxsjy/jieba)
`Tokenizer` API (MIT, verified in installed package metadata). No upstream source
was copied or redistributed; existing dependency notices remain intact.


The experiments and evaluation protocol are informed by
[S2G-RAG (ACL 2026)](https://aclanthology.org/2026.acl-long.1185/),
[CompSelect / Less is More (WWW 2026)](https://arxiv.org/abs/2502.11811),
[IRT-Judge](https://arxiv.org/abs/2602.00521), and
[Reliability without Validity](https://arxiv.org/abs/2606.19544).
These are **research references, not implemented model reproductions**. No
upstream code, prompts, weights or datasets from those projects are included.
The research plan records dates, repository checks and license limitations.
The opt-in `newdomain/clauses.py` C3B variant independently adapts exact
sentence-pointer representation and compact clause grouping, conceptually
informed by S2G-RAG and CompSelect. It reuses C1's inference contract and is not
either paper's trained system. Offline ablations rejected an initial variant
that exceeded the request limit on 46/60 prompts; complete-clause packing fits
all 60 exposed prompts. The completed fresh comparison found no measured
quality gain and higher p95 latency; C1 remains the default.
`newdomain/numeric.py` is independent engineering, not a paper reproduction,
and is not automatically routed into answers. Existing B0/C1/C2 methods retain
their local provenance in module documentation.

The fixed-answer calibration controls use the evaluation-validity questions
raised by IRT-Judge and Reliability without Validity; no IRT model was implemented.
The opt-in `newdomain/facet_recovery_v2.py` independently tests one requested-facet
addition under a fixed context count, conceptually informed by S2G-RAG and
CompSelect. Its first variant selected a neighboring property's evidence and was
rejected offline. V2 was tested, then `facet_recovery_v3.py` preferred concrete
entity-specific access facts over dated forecasts; see the measured checkpoint. These are conceptual
credits, not copied algorithms or reproduced models. `newdomain/scoped_aggregation.py`
is independent source-row arithmetic and conditional entity handling; it is not
attributed to a paper implementation. `scoped_aggregation_v2.py` corrects the
unique-mode wording and has the measured opt-in answer tests linked above.

The opt-in `newdomain/definitions.py` C10D selector is independent engineering:
it adds a bounded same-document definition chunk, without copying a paper
algorithm or code. Its targeted development test improved source coverage and
corrected two boundary answers, but left three interpretation errors and two
retrieval misses. It is not promoted; detailed negative results and evaluator
disagreements are in [the optimization log](docs/optimization-log.md).

`newdomain/lexical.py` C11B is also independent engineering: it preserves a
missing strongest lexical hit only within the existing top document. Targeted
gains replicated in an active-format confirmation, while a broader inactive
comparison provides only stability evidence. The limited reach and remaining
errors do not establish broad superiority.
It is opt-in and does not change C1.

`newdomain/predicate.py` C12P is a generic consistency-prompt experiment, not
verified symbolic reasoning. Its three wins and two regressions do not justify
promotion; the original C1 prompt remains unchanged.

## Completed frozen comparison — 2026-10-13

| Evidence | C1 | C3B packed clauses |
|---|---:|---:|
| Fresh Chinese final: both-rubric adequacy | 40/40 | 40/40 |
| Fresh final: p50 / p95 seconds | 1.522 / 1.685 | 1.545 / 1.796 |
| Fresh final: generation + judging USD | 0.319464 | 0.316990 |
| Exposed 20-case regression: both-rubric adequacy | 18/20 | 19/20 |
| Preselected 9-case repeat: p95 seconds | 1.714 | 1.821 |

**Retain C1.** C3B produced no measured fresh quality gain and had 6.6% higher
p95 latency. The regression difference is one case, with rubric disagreement;
it is not reliable evidence of improvement. All 154 generation outputs were
valid; 358 total generation/judge calls completed without retries or unresolved
jobs. New accounted spend was **$1.00760184**, cumulative **$28.70029119 / $100**,
with zero open reservations and exact response-to-ledger reconciliation.
These are conservative pinned-tariff charges, not a provider invoice.

Questions were frozen before answers; inference files excluded reference
answers. The final is assistant-authored on a previously exposed corpus, with
explicit source/facet prompts, only one numeric case, and weak coverage of
cross-page retrieval. Both judge passes use the same model with different
rubrics. A source spot-check found a C3B qualifier omission and a shared omission
also absent from the reference, despite agreement. The ceiling score and its
degenerate bootstrap interval are **not human gold or an equivalence proof**.

See the [research results and limitations](docs/research-cycle3.md) and
[integration acceptance evidence](docs/integration-acceptance.md). Private
Chinese QA, source-audit notes, frozen files and ledgers remain local. No deployment.

The [offline evaluation repair](docs/evaluation-repair.md) records source-bound
obligations, three observed omission flags, and explicit semantic blind spots.
It preserves frozen scores and requires source-aware adjudication before further
paid optimization; assistant source review is not independent human gold.

The continuing objective and plateau rules are in
[OPTIMIZATION_GOAL.md](OPTIMIZATION_GOAL.md); the
[optimization log](docs/optimization-log.md) tracks new work beyond this completed
comparison. Publication is blocked, but safe local research continues.

### Continuing research experiments (local, opt-in)

See [the continuing evidence log](docs/optimization-log.md) for completed prompt,
retrieval, model-capacity and premise-uncertainty ablations, including negative
results and evaluator failures. C1 remains the default. `newdomain.guardrails`
provides opt-in missing-record routing and exact fixed-sentence contract
normalization; these are independently implemented local engineering safeguards,
not claimed reproductions of a paper. They do not create facts or model usage.
The uncertainty prompt is experimental: two initial corrected errors did not
replicate as a net gain on a broader 32-question comparison (30/32 for both arms
under conservative assistant source review, with wide uncertainty). C9S requested-
scope preservation and subsequent experiments were evaluated in [audited bounded batches](docs/bounded-batches.md)
under the sustained optimization request; the original deadlines and all spending
history remain intact. Existing research acknowledgments apply only as described in
[the research record](docs/research-cycle3.md); no upstream code was copied for
these safeguards.

Latest checkpoint: [completed continuation outcome](docs/research-cycle3-outcome.md)
records C10D/C11B/C12P ablations, active and inactive controls, evaluator errors,
155 passing offline tests in both Python modes, and reconciled cumulative cost
$31.70860407. C1 remains default; all recorded batches are closed.

The typed-condition continuation is active. `newdomain/conditions.py` is an
independent deterministic scalar compiler with exact source provenance and
explicitly unresolved semantic bindings, not an implementation of VeNRA or a
trained verifier. Its initial 18/24→21/24 assistant-adjudicated result requires
an annotation-versus-guidance ablation and broader validation. C1 stays default.
[Full coverage reconciliation](docs/test-coverage-reconciliation.md) restores all
legacy tests: 330 pass normally and under `-O` after the compiler additions.
The private four-column case report is generated by
`scripts/optimization_case_report.py`; source data and exports remain outside Git.

Latest typed-condition evidence: [checkpoint and remaining request-cap blocker](docs/typed-condition-checkpoint.md).
C15T scored 24/24 versus C1 21/24 on the broader curated set, then 24/24 versus 22/24
on an unchanged all-case repeat. These are assistant source judgments on 24 unique
questions, not 48 independent cases or human-gold accuracy. It remains opt-in.
Full acceptance now passes 337 tests in both Python modes; cumulative cost is
$32.51849835. At that historical checkpoint, more paid work was blocked by the 1,800-call final-stage
request limit; all batches are closed, with zero open reservations. Private case
report: 300 verified rows, exactly four columns, no upload.

The latest [case-report provenance checkpoint](docs/case-report-provenance.md)
separates 光明 C1 from the verified 牛黄 K synthetic benchmark. It reports missing
real-user coverage and unfinished reviews explicitly; no cross-corpus SOTA claim
is made. The reusable four-column exporter preserves delivered outputs, actual
scores and each run's distinct timing boundary. Full offline acceptance is 350
tests in both Python modes. Those old request-allocation proposals stayed non-dispatching. The later explicit
Flash full-rerun authorization uses the audited successor described above; old
ledger history and stopped jobs remain preserved.

### Original-question optimization experiments

The [earlier checkpoint](docs/original-optimization-checkpoint.md) preserves the
partial-run history and repaired evidence-order harness error. The
[completed continuation](docs/original-optimization-cycle2.md) is the current
complete result, including negative transfer results and remaining source limitations.
The [latest checkpoint](docs/original-optimization-cycle4.md) records the additional
pilots and provider-blocked unified rerun; it does not supersede the complete scores.

The independent catalogue-to-evidence experiment in `newdomain/entity_bridge.py`
uses the distinction between retrieval keys and source evidence discussed by
[M-RAG: Semantic Key-Value Indexing for Retrieval-Augmented Generation](https://arxiv.org/abs/2603.26667)
(Xu Sun et al.; arXiv submission history reports January6,2026, revised July21,2026).
This is conceptual acknowledgment only: we do not reproduce its learned markers,
GPU experiments or performance claims. The paper links the
[authors' repository](https://github.com/9sxx/M-RAG); no upstream code, prompts or
assets were copied, installed or executed. No repository license was verified;
reuse of that code requires a separate license check. Our independently written exact-name bridge improved a four-question pilot
from3/4 to4/4; a paired replication over the same four questions with three
repeats yielded6/12 versus12/12. These are four exposed question clusters, not
12 independent test questions. Broader confirmation was interrupted by provider
HTTP402 and remains incomplete. See the [interruption checkpoint](docs/original-optimization-cycle4.md).

The [continued original-question experiments](docs/original-optimization-cycle2.md)
include the completed90→155/315 牛黄 comparison, negative 光明 global-transfer
results, and the narrow catalogue-count improvement9→14/17. All are exposed,
model-judged experiments; no production default or all-pass claim follows.
The query-plan experiment also acknowledges the meaning-preserving query-variant
idea in [CQC-RAG](https://arxiv.org/abs/2606.13438) (Sun, Liu and Shao; first
submitted June11,2026). Our bounded retrieval-hypothesis interface is independently
written and is not a reproduction of its multi-view confidence estimator.
The [author-linked repository](https://github.com/FrancesPlus/CQC-RAG) was inspected
read-only; no upstream code or prompt was copied or executed, no code license was
verified, and no peer-reviewed venue is claimed from its placeholder publication
metadata. The query-planning pilot gains one net pass in each small domain subset,
with regressions in 牛黄 and an extra model call; it is not adopted as a default.

The [coherent candidate checkpoint](docs/original-optimization-cycle3.md) records
223/330 光明 and155/315 牛黄 primary passes from deterministic replay of saved
experiments, with live and supplied questions separated. It preserves the
negative exact-book ablation, identifies additional privacy-filter evidence loss,
and documents the private four-column report. This is exposed-development
evidence, not a fresh joint run or production deployment.


The [Bailian/public-source continuation](docs/bailian-public-source-continuation.md)
records the explicitly authorized provider transition, exact model provenance,
legacy-host timeout failures, and separately versioned institution/platform source
restoration. Source restoration is not attributed to a new RAG algorithm or an
upstream paper. Performance claims await the recorded paired experiments.
