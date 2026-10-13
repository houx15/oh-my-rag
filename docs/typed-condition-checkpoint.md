# Typed-condition checkpoint — 2026-10-13

C15T is a promising opt-in candidate; **C1 remains default**. No overall plateau
is claimed. Paid work is blocked by the unchanged manifest's final-stage request
ceiling of 1,800, despite remaining dollar allowance. The original 60-question
regression is prepared but has dispatched zero calls.

## Test coverage reconciled

The 301-test checkpoint used full discovery. A later tracked-only selection ran
155 tests and wrongly omitted five applicable untracked legacy modules containing
161 tests. No tests were deleted or skipped. Fifteen intervening additions make
301 + 15 = 316 = 155 + 161. Full discovery restored all 316 in both Python modes.
Typed-condition tests added 16, report-preservation tests 3, and whole-batch request
preflight tests 2, yielding **337 passing tests normally and with `python -O`**.
The [detailed reconciliation](test-coverage-reconciliation.md) names every suite.
Initial restricted fixture-write errors and one subsequently fixed test-placement
import error remain in private logs; neither was hidden by excluding a suite.

## Method and controlled evidence

The independently written compiler extracts scalar thresholds with exact source
spans, normalizes currencies/time/area/count units with Decimal, resolves explicit
document-wide comparator definitions, and gives local endpoint exceptions
precedence. It preserves source-sentence scope and separate question provenance.
Entity binding is explicitly unresolved; time scope is only partially recognized.
Scalar comparisons are not verified semantic joins or eligibility decisions.
This is a narrow symbolic annotation aid, not a trained extractor or full logical
policy engine. It uses no imported paper code, weights or prompts.

| Frozen comparison | Assistant adequate | Wins / losses | Parent-observed transport p95 ms | Generation USD |
|---|---:|---:|---:|---:|
| C10D → C13T, six primary documents | 18/24 → 21/24 | 3 / 0 | 2022 / 2043 | .0274212 / .0389184 |
| C14E empty table → C14T populated table, identical guidance | 22/24 → 24/24 | 2 / 0 | 1955 / 1878 | .0297450 / .0389352 |
| C1 → C15T, broader eight-document comparison | 21/24 → 24/24 | 3 / 0 | 1837 / 1959 | .0278802 / .0382371 |
| C1 → unchanged C15T, all 24-pair repeat | 22/24 → 24/24 | 2 / 0 | 1894 / 1996 | .0279618 / .0384483 |

All 192 generation outputs are mechanically valid. Source obligations and questions
were frozen before outputs; arm-masked assistant scoring preceded mapping/model
verdict inspection. This is not independent human adjudication. Questions are
assistant-curated natural-style Chinese, not sampled user traffic. The broad
cohort uses eight primary document IDs absent from the earlier typed studies;
underlying policy content is not fully disjoint (for example D12 and earlier D22
cover the same manufacturing policy). OCR, related concepts and the overall
corpus were already exposed. Do not infer independence from document IDs.

C13T's role/premise repairs did not establish arithmetic compilation as the cause.
The next ablation held accompanying guidance fixed and varied only the table.
Before it, source review caught incorrect draft financial tiers; all affected
criteria were corrected before any dispatch, with draft artifacts retained.
A v1 parser defect in “不得超过” was also fixed before v2 testing. One irrelevant
v1 annotation in the earlier experiment was affected; its outputs and scores
remain unchanged. v2 also recognizes “不得低于”/“不高于” and skips selected
uncertain comparator forms. These repairs do not establish general parsing
coverage, especially for unrecognized measures, complex rates or subsection scope.

No definition chunk was inserted in the broader C15T comparison, so C1 and C15T
used identical original source chunks there. The three first-run gains repaired
a false cap explanation, a reversed opening conclusion, and an avoidable
approximate-unit-conversion refusal. The first two persisted as C1 errors on
repeat; the refusal disappeared. Across repeated observations, C1 is 43/48 and
C15T 48/48, with five wins and no clear new adequacy losses. There are only 24 unique
questions and three unique improved questions, not 48 independent trials. The
first-run exact paired sign test is p=.25; the repeat is p=.5. Small descriptive
bootstrap intervals are not proof of generalization. Borderline explanations and
protocol disclaimers remain recorded; no ceiling score is called perfect accuracy.

Generation cost rises about 37% versus C1; transport p95 rises 6.6% initially and
5.4% on repeat. These exclude retrieval and represent small interleaved samples,
not production end-to-end latency. Local annotation overhead has not been included
in these transport figures. Initial C13 gains over C10D and table-only gains over
C14E cannot be pooled as if all used C1 or the same candidate version.

## Reviewer validity, reporting and accounting

The paired model reviewer scored C13T 23/24 versus C10D 21/24, missing several
contradictions/local-scope errors. In the table ablation it scored 24/24 versus 23/24,
missing the mixed-policy explanation caught by assistant review. In the broader
C1 comparison it scored 24/24 versus 23/24, missing two contradictory C1 answers.
Agreement is not validity. The repeat has only 14/24 completed model reviews;
no full model score is reported. All 48 repeat answers have completed assistant
adjudications, which remain separate from the partial model reviews.

The private case report contains 300 rows in 12 declared cohorts, with exactly:
**Question | Our answer | Score | Response time**. It includes all 10 historical
user-provided cases, all 50 historical curated cases, and every answer in the
selected new/repeated comparisons. C1, experimental variants, fresh-at-run
questions and exposed diagnostics have separate headings. Raw model sentence
text is verbatim; scores are retained values with scorer/rubric limitations;
time is exact parent-observed transport milliseconds including worker/client/IPC,
not end-to-end application time. HTML cells match lossless CSV cells exactly;
Markdown, source hashes, raw-response IDs and timing evidence are also retained.
The reusable generator is `scripts/optimization_case_report.py`.

This typed continuation dispatched 278 calls (192 generations, 86 reviews), costing
$0.80989428. Cumulative spend is **$32.51849835 / $100**. The nested $12 allocation
has $7.17419100 remaining; global dollar headroom is $67.48150165. Eleven historical
ledger hashes match, the audit chain validates, all 11 recorded batches are closed,
and there are zero open reservations or retries. Pinned tariffs are accounting
estimates, not provider invoices. No manifest limit or historical record was reset.

The final review batch completed 62 of its 72 planned calls. At final-stage call
1,800, `TR-015` was rejected by the reservation gate before provider dispatch;
that terminal failure and nine not-yet-attempted reviews remain explicit. A
transient execution-service disconnect was separately recovered through read-only
inspection; it did not cause a provider retry. New activation preflight now
requires room for the entire planned batch in the existing request allowance.

## Exact continuation boundary

Further paid work requires coordinated authorization to revise the pinned request
allowance and its profile/freeze custody; do not switch stages, reset counters,
reopen a closed batch, or retry the terminal journal to evade it. The proposed
60-question regression is privately prepared in fixed 24/24/12 groups,
with original references explicitly unvalidated and zero paid calls. The 12-case
batch and remaining 10-review continuation need appropriately scoped audited
support; current activation only accepts 24-case batches. No claim that these
pending tests passed. Complete source review and the original-workload regression
before any default promotion; preserve both original and new scores. No push,
upload or deployment has occurred.

Compiler v1 is preserved at local commit `2ee1009`; v2 and experiment entrypoints
are preserved at `ed87785`. Each run's private freeze hashes define its exact
code/messages; these commits do not replace per-run hash custody. Literature
provenance remains in [the research matrix](research-cycle3.md), and README
acknowledgments distinguish implemented conceptual adaptations from unadopted
papers. The typed compiler is independent engineering, not a VeNRA reproduction.
