# RAG optimization: cumulative technical report

Canonical project narrative and dated research log. Last updated **2026-10-14**.
Detailed experiment records linked below retain frozen inputs and negative results;
this document is maintained as the project develops into a technical report.
Local artifacts remain private. No push, publication, upload or deployment is authorized.

## Current evidence and denominator summary — 2026-10-14

**The fresh645-question paired benchmark is complete; grounded-prose-v3 is not
promoted.** Model-and-delivery passes388→382, valid outputs636→585, and warm staged
p954.918→5.513s. Both arms use repaired deterministic retrieval and the Cycle10
baseline adapter; this is not exact historical C1/current-default reproduction.
The original20-regression comparison had a parser mismatch; after a blocked attempt,
a new corrected recovery completes20/20 baseline versus19/20 candidate. All attempts
remain visible. A narrow offline parser fix recovers one primary candidate answer
(585→586 valid) without changing original scores.
Final conservative ledger **113.89682145/200USD**, zero open reservations, no active
paid work. Fresh generations do not make historically exposed questions unseen.
Model judges, OCR references and assistant source review are not human gold.

The original **420 Guangming supplied Q/A pairs** contain181 real-user and239
simulated questions. Contact exclusions remove90 (68 real-user,22 simulated),
leaving330 (113 real-user,217 simulated). Near-duplicate grouping into300 groups
controlled the initial split; it did not remove another30 records. The initial
October12 run evaluated48 development and60 held-out questions, plus20 separate
regressions—not all420. The next60-question comparison was distinct from the108
previously exposed questions, but was itself50 simulated and10 real-user questions.
Its C1/C2P both-judge44/60 versus36/60 result is now exposed historical evidence.

Niuhuang starts with395 workbook rows (283 live,112 evaluation). Privacy screening
removes64 rows, leaving331 eligible rows;16 duplicate aliases map to retained
outcomes, yielding315 distinct questions (205 live,110 evaluation). Thus the
combined eligible pool is **645 questions =330 Guangming +315 Niuhuang**, comprising
**318 live/real-user +217 simulated +110 evaluation** questions. Adding20 separate
regressions yields665 scheduled cases. These are different populations, not a
progressive reduction of the original420-question benchmark. Excluded records and
duplicate aliases remain documented in private provenance; no exclusions changed.

| Campaign / date | Denominator and provenance | What the evidence establishes |
|---|---|---|
| [Full coverage, October13](original-question-evaluation.md) |645 mixed-origin questions +20 separate regressions;168 matching Guangming generations reused; all665 primary review requests finished, including one malformed/unscored review and one generation failure retained | Broad historical coverage, not an all-fresh current-default reproduction; GM218/330, NH90/315, regressions19/20 |
| [Coherent report, October13](original-optimization-cycle3.md) |645 matching saved outputs under explicit GM C1/count and NH focused/typed-v2 routing; no score-based answer selection | Latest complete coherent mixed-pool report: GM223/330, NH155/315. Assembled historical results, not fresh end-to-end execution or default promotion;20 regressions were not rerun for this candidate |
| [Subsequent fresh unified attempt](fairness-diagnostic-20261013.md) |665 planned;328 completed,337 incomplete after provider failures | Interrupted run; cannot establish full benchmark performance |
| [Broad live regression, Cycle7, October14](broad-original-cycle7.md) |318 live/real-user questions;373 outputs:55 changed cases independently paired and263 common outputs shared | Assembled baseline140/318 versus candidate144/318; exposed regression evidence, not two independent full runs or a mixed-pool/default reproduction |
| Later diagnostics, October14 |Cycles12/13/14/16:20 questions each; Cycle15:14; Cycle17:3; Cycle18:8; Cycle19:12 | Targeted, often repeated development cohorts; cohort membership and configurations differ. No overall performance estimate from these subset gains |
| [Cycle20 confirmation, October14](structured-confirmation-cycle20.md) |16 mixed-origin questions,32 fresh outputs:8 live/real-user,5 pre-existing GM simulated,3 pre-existing NH evaluation; all16 historically generated | Excluded from Cycles16–19 only, not truly unseen or original-only. Completion5→7/16, delivery16→14/16, adequacy8→7/16; confirmation gate failed |

Cycle20's8 live/real-user questions are3 GM and5 NH. N265 was also in Cycle14 and
GM124 in Cycles14/15. The8 planned synthetic checks for Cycles14/15 remain unrun;
they are distinct from Cycle18's8 evaluated questions. Every historical score,
failed/unscored outcome and negative result remains unchanged.

A comprehensible future full benchmark needs a frozen roster with origin,
exclusion/alias and exposure accounting; exact baseline/candidate versions;
explicit fresh/reused/failed/unrun status; full-pool results first with live,
simulated, evaluation and regression strata separate; and fixed, human-calibrated
scoring and comparable latency scope. Diagnostic subsets belong alongside those
results, not in place of them. The completed primary benchmark below supplies this accounting; human calibration
remains outstanding; the separate corrected regression recovery is recorded below.

## Historical experimental principle and keyword investigation (through Cycle15)

An initial aggregate score neither accepts nor rejects a strategy. Each strategy
gets a diagnostic optimization stage: inspect hypothesis quality, marginal evidence
recall, fusion/selection, answer use, and latency separately; repair the weakest
supported mechanism and retest controls. Preserve negative results and material
regressions. Stop based on measured tradeoffs, exhausted justified hypotheses, or
actual evidence/calibration blockers, not one disappointing aggregate score.

At the Cycle15 checkpoint, the authorized focus was **keyword diffusion**, including source-grounded
marginal candidate accounting and targeted selector diagnosis with downstream
settings fixed. The typed-policy-record idea below is deferred. Cycle14/15's failed
prompt gate is a result for those versions, not rejection of keyword diffusion or
all generation interventions. No additional paid work has started during this audit.

## Historical checkpoint through Cycle15

**Cycle15 completed:** task-focused prompt source-usefulness6→9/14, but only one
borderline content rescue; other gains repair a conditional referent and unsupported
UI capability. Strict sensitivity4→5; rawjudge5→4; validity13→14. The predefined
2-content-rescue gate failed, so8 frozen synthetic checks remain unrun. C1 unchanged.
[Results and failures](use-focus-cycle15.md). Cycle14's generic checklist likewise
found only a UI correction (8→9/20); [negative result](use-prompt-cycle14.md).
Stop this tested prompt-only line; no generalization or broad performance claim.

**No broad retrieval candidate has displaced C1.** Historical C1 scored44/60 with
both judges, versus36/60 for the longer-context/answer C2P; p95 was1.931s versus
2.041s. This is an exposed diagnostic comparison, not human-gold accuracy.

Cycle12 tested source-vocabulary and unrestricted small-model keyword hypotheses
on20 original questions (10 per corpus). Raw judge passes were8 baseline,
10 vocabulary (one additional unscored answer), and6 small-model. A separate
masked assistant source review instead rated9,9,12 useful answers. The disagreement
is material: source attribution and appropriate clarification can be penalized
by the original references. Neither reviewer is human gold. The small-model
component-sum p95 increased from6.140s to11.299s. Candidate-pool diagnostics show
correct sources dropped during fusion; more keyword calls are not the next step.
**Cycle13 is complete: equal fusion9/20 and token coverage10/20 source-useful,
versus12/20 for the earlier weighted small-model arm. Neither is promoted.**
Both new selectors have one protocol failure; source selection alone does not
resolve policy-scope, attribution or evidence-use failures. [Cycle13 details](keyword-selection-cycle13.md).

At Cycle15 closure, settled conservative cumulative spend: **86.45485345 of200USD**, including
all earlier ledger chains. This uses conservative numeric tariff reservations,
not an exchange-rate conversion or invoice. Cycle12/13 made219 paid calls; Cycle14 added80dispatches including1unknown-usage
judge timeout, conservatively settled without retry; Cycle15 added56 fully settled
dispatches at0.38709 incremental cost. All stages closed, no open reservations;
one judge request was rejected locally before dispatch and remains unscored.
No privacy-screen exemption was added. [Cycle12 details](keyword-cycle12.md).

## Objective and system

Improve useful, source-grounded Chinese answers while preserving conditions,
units, scopes, citations and appropriate uncertainty at bounded latency/cost.
A useful abstention on absent current data differs from failure to use an available
historical passage. A correctly retrieved candidate differs from evidence actually
selected, cited and used in the delivered answer.

The local system loads document-derived source records; existing lexical and
cached embedding retrieval produce candidates; optional facet/section selectors
choose bounded excerpts; the approved model produces a structured answer;
source-handle/citation and schema validators determine deliverability. Guangming
also has explicit catalogue-derived statistics. Niuhuang source handling retains speaker/book markers where available; generated
attribution remains an evaluated failure mode. Opt-in protocol normalization repairs narrowly declared
boundary grammar and aliases, not arbitrary unsupported prose.

In plain language: the system first finds potentially relevant pages, then chooses
short passages that fit the answer budget. The model writes an answer using those
passages and marks which passage supports each statement. Software resolves those
marks into exact quotations and checks the output format and source addresses.
A later evaluation step judges usefulness. A passage can be found but discarded,
selected but ignored, or quoted exactly without supporting the claim; these are
separate failures. For example, GM124’s correct safety-system entry reached the
model, but the model still said it had no evidence. The validator did not remove
a good answer in that case.

Experimental branches are distinct from the C1 default. Cycle12/13 use the current
Cycle10 baseline adapter (facet handling, restored Guangming source and protocol
normalization); they are **not exact reruns of historical C1**. Generated keyword
hypotheses only retrieve sources. They never become answer evidence. Original
query retrieval and half of original contexts remain protected. Source terms are
traceable to record IDs; pad/LivePad are separately user-supplied interface terms,
absent literally from the indexed snapshots. No UI action is actually implemented.

## Data, provenance and evaluation contract

Two corpora: Niuhuang historical materia-medica and Guangming institutional/
technology documents. The Cycle12 source-vocabulary inventory has1507 and1174
records respectively; these are index records, not independent original documents.
The retained live/real-user-question roster contains318 records:205 Niuhuang and113
Guangming. Niuhuang screening excluded64 source rows upstream; Guangming separately
excluded90 contact-related questions. Niuhuang’s315
presentation records came from331 screened rows with16 duplicate aliases; this
audit is not coverage of every collected original question.
The historical60-question C1/C2P comparison,318-question rerun, repeated outputs,
synthetic checks and20-case pilot have different denominators and versions.

The historical presentation contains645 unique output records, including318 original
question records; it combines96 gm-c1,17 gm-c1-catalogue-counts and205
nh-focused-typed-v2 originals. It is not one current pipeline. Historical presentation-output snapshot
hash and audit counts are retained in [historical audit](historical-failure-audit.md).
See [case provenance](case-report-provenance.md) and [broad original run](broad-original-cycle7.md).

References and OCR transcriptions are not human gold. Inference inputs omit
reference answers and expected source IDs; evaluation-only files feed unchanged
judges after generation. This is logical separation on the same host. Exact quoted
substrings establish provenance, not entailment or completeness. Source-level
assistant review is a separate measurement, never a silent replacement of raw
scores. Prior-context and same-model-family bias remain even when arm labels are
masked. Human calibration remains outstanding.

Record protocol validity, source/usefulness judgments, citation errors, abstention
appropriateness, gains AND regressions, unscored requests and timing scope. Do not
count unscored as fail or treat repeated outputs as independent questions. Preserve
fresh frozen checks without tuning; exposed diagnostics support mechanism analysis,
not generalization claims. Fresh synthetic checks can still share source/entities.
Latency includes retrieval through validation when measured contiguously; Cycle12/13
instead sum measured staged critical-path components including keyword time. Cold
initialization, uncached embedding timing, grading and idle time are excluded.

## Five failure categories and research questions

The grouping below organizes interventions; original audit labels remain separate.
Counts below regroup the56 located primary defects among318 retained historical
original-question records (113GM/205NH), not current error rates. Secondary tags
can overlap but do not change this accounting.

| High-level category | GM | NH | Total /318 historical records | Original primary labels |
|---|---:|---:|---:|---|
| Evidence acquisition/selection |7|14|21|RET|
| Evidence use/completeness/scope |5|6|11|USE10 +SCOPE1|
| Numerical/source-processing integrity |4|0|4|SRC3 +aggregation1|
| Intent/uncertainty/interface interpretation |2|3|5|ASR1 +TASK4|
| Delivery/citations |1|14|15|PROTO7 +CIT8|
| Located defects |19|37|56|Mutually exclusive primary classifications|

The separate14 UI requests are outside these56 located defects, as are23
scorer/reference issues,85 unresolved,26 source-insufficient and114 no-material-
defect findings. Measurement validity is discussed with category5 but its23
reference problems are **not** added to the15 system-delivery/citation defects.


| Category | Source-grounded example and version status | Research question / actionable method |
|---|---|---|
| 1. Evidence acquisition and selection | Historical N417 lacks the valuation passage. Cycle12 relevant MD-011-0004 reaches candidate rank10 but is dropped; GM064 D30:1:01 reaches hypothesis ranks2/3 but is dropped. R065's possible 夜啼 source never enters its pool. | Pool recall versus ranking/window coverage. Deduplicate fusion votes; test marginal query-attribute coverage. Selection cannot recover a source outside the pool. |
| 2. Evidence use, completeness and scope | Historical GM124 retrieved D36:330 safety-interlock text but omitted it. Cycle12 GM064 answers broaden a20%/500万元 subsidy beyond its new-materials restriction. R021 retrieves 除邪逐鬼 but repeats instead of explains. | Claim sufficiency, requested facets and condition coverage. Keep full qualifying clauses, evaluate use separately from retrieval. |
| 3. Numerical and source-processing integrity | GM142/GM174 platform 超千项 was confused with381 collected catalogue records; restoration separates scopes in Cycle12. Historical GM090108/381=28.35% requires complete-catalogue aggregation. | Typed operands, population/period/unit scope and deterministic aggregation. Do not substitute a top-k count or correct arithmetic over wrong operands. |
| 4. Intent, uncertainty and interface | Cycle12 R095 contains unresolved 它: small-model arm asks for context, baseline silently assigns a book. N001 silently substitutes 牛磺 with 牛黄. GM125 can explain district facts but cannot switch a display. | Selective answering, conditional entity hypotheses and task decomposition. Separate missing dialogue, speech ambiguity and unavailable UI action; never confirm guesses as facts. |
| 5. Delivery, citations and measurement | Historical audit finds8 citation-attribution gaps despite exact source quotes. R034 small-model source-faithful attribution is a raw-judge loss. Cycle10 repairs3 final delivery failures; Cycle12 still has2 invalid boundary outputs. | String provenance versus entailment; validity versus reliability. Narrow schema normalization, masked source adjudication and reference-error tracking. |

Historical audit locates56 defects (19 GM,37 NH), including21 final-context misses,
10 retrieved-but-unused,8 citation and7 protocol problems. Other categories:
23 scorer/reference errors,85 unresolved,14 UI,26 insufficient-source and114 with
no material defect found. These are mutually exclusive primary historical audit
labels, **not current accuracy estimates or proof that114 answers are gold-correct**.

## Pre-Cycle14 USE-stage investigation — 2026-10-14

User hypothesis: usable evidence may be omitted by the generation instructions or
suppressed during structured-output validation. Compare the full chain, retaining
USE and PROTO as distinct primary labels and allowing secondary intent/scope tags.
The first offline trace examined6 saved outputs (2 historical,4 current Cycle12),
with no new inference and no validator changes. Local evidence:
`keyword-cycle12-20261014/use-stage-trace.json`.

| Case / version | Selected evidence and instructions | Raw response → parsed/delivered answer | Located failure |
|---|---|---|---|
| GM124 historical | D36:330:01 explicitly describes safety-interlock protection. Saved prompt requires grounded facts, permits fixed no-evidence sentence, but gives no explicit split between display operation and explanation. | Raw model already returns only “本次资料未包含回答该问题所需的依据。”; parsing adds protocol field, delivered text unchanged. | USE; secondary UI/intent. No postprocessing suppression. The interface wording may distract generation; prompt test was pending at this initial trace; completed results follow in Cycles14/15. |
| N265 historical | Selected MD-038-0008 explicitly says “药中之贵，莫复过此” and historical valuations. Exact historical prompt is not available in this inspected record; do not substitute a reconstructed current prompt. | Raw model says no price information and adds no-evidence boundary; factual sentence preserved, boundary expanded as declared. | USE; secondary missing antecedent/current-versus-historical ambiguity. Historical valuation should be distinguished from current price; not proof the user's referent is known. |
| R021 Cycle12 baseline | Selected passage contains除邪逐鬼 but no explicit explanation. Prompt says answer the question and permits only provided-source facts. | Raw response repeats the phrase and says no separate definition; both sentences delivered unchanged. | Incomplete requested explanation, with source-sufficiency/RET secondary possibility. Not evidence the validator deleted an available explanation; do not invent interpretation to force success. |
| GM064 Cycle12 baseline | Selected policy evidence contains new-materials context; prompt explicitly requires conditions/scope. | Raw answer already omits policy applicability and adds subsidy to achievements; delivered text identical. | SCOPE/USE and relevance, not protocol. Source-scope recognition is not guaranteed by exact handles. |
| R004 Cycle12 clean control |定精神 passage selected; same historical grounding/format instructions. | Raw factual sentences preserved; quote resolution and handoff completion succeed. | Useful answer survives, control against blanket claims that schema suppresses facts. |
| R065 Cycle12 baseline | Ambiguous液体 question, no夜啼 evidence; prompt explicitly requires clarify to be the entire answer. | Raw response mixes factual sentences with clarify; final answer rejected as unknown/mixed boundary. | PROTO primary with intent/source-gap secondary. This is actual delivery rejection; accepting mixed output would not make it answer the question. |

For all5 mechanically valid traces, every raw factual sentence survived delivery.
The sixth was correctly rejected under its declared mixed-clarification contract.
This small purposive sample localizes failure; it does not establish that no other
postprocessor suppresses information. Intermediate handle JSON can fail the final
schema before canonical conversion and still deliver successfully; do not count
that intermediate diagnostic as final rejection.

The pre-Cycle14 proposal was to hold contexts, model, schema, validators and token
caps fixed while changing generation instructions, with clean and missing-evidence
controls. Cycles14/15 have now completed that comparison: raw-to-delivered traces
and source review did not establish the required substantive content gains.
Their frozen confirmation sets remain unrun. No output fields or validators were
weakened; accepting unsupported prose would not establish task success.

## Literature and actual influence

Window: **2025-10-12 through2026-10-12 inclusive**. Original-source dates, repositories,
licenses, inspected commits and reproducibility limitations are detailed in the
[literature-to-failure matrix](research-cycle3.md). Links below are original sources
verified during that review; this cumulative document adds no unverified new paper.

| Work / date status | Connection and actual use |
|---|---|
| [S2G-RAG](https://arxiv.org/abs/2604.23783), first submitted2026-04-26; [ACL2026 proceedings](https://aclanthology.org/2026.acl-long.1185/) | Sufficiency/gap and exact sentence pointers conceptually informed independently written clause representation. [Official repo](https://github.com/nianaaa/S2G-RAG) had no LICENSE at inspected commit; no source, prompts or weights copied/run; trained method not reproduced. |
| [CompSelect](https://arxiv.org/abs/2502.11811), first submission2025-02-17 outside window; revision2026-01-27 and WWW2026 publication inside | Compact clue selection informed the same independent representation experiments. [Official repo](https://github.com/zqc1023/CompSelect) had no LICENSE at inspection. No copied code or oracle gold-answer extraction in inference; not a reproduction. |
| [SURE-RAG](https://arxiv.org/abs/2605.03534), first2026-05-05, revised2026-07-24 | Support/refutation/insufficiency motivates diagnostics only. PRAI submission is not verified acceptance; repository author linkage/full reproducibility unverified. Not adopted. |
| [IRT-Judge](https://arxiv.org/abs/2602.00521), first2026-01-31, revised2026-05-29 | Evaluation reliability background; author-reported ICML acceptance. Linked repo404 during review, license unverified. No IRT fitting or implementation adopted. |
| [Reliability without Validity](https://arxiv.org/abs/2606.19544), first2026-06-17 | Measurement caveat: judge agreement is not human validity. No official runnable repo or venue verified; no code adopted. |
| [From BM25 to Corrective RAG](https://arxiv.org/abs/2604.01733), first2026-04-02 | Retrieval versus numerical-quality diagnosis; no verified venue or accessible code/data record. Local selector predates review; no implementation credit claimed. |
| [VeNRA](https://arxiv.org/abs/2603.04663), first2026-03-04, revised03-08 | Typed operands/execution is related context. [Official repo](https://github.com/pagand/VeNRA) README states CC-BY-NC-SA4.0; file-specific terms unverified. No code/prompts/weights/data adopted; local Decimal utility is independent. |

[FinAgent-RAG](https://arxiv.org/abs/2605.05409) was withdrawn2026-07-05 for
methodological errors and is excluded. No unsupported novelty claim is made:
coverage, selective answering, numerical provenance and judge validity are known
problems. Domain-specific Chinese qualifier/attribution hypotheses are engineering
experiments. Keyword fusion and token coverage are independently engineered; no
external implementation or paper benchmark is claimed. README acknowledgments
remain precise and required existing notices preserved.

## Cumulative dated experiment log

| Date / experiment | Hypothesis and method | Observed result, cost/latency and decision |
|---|---|---|
| Oct12 C1/C2P | More context/answer space improves completeness |44/60→36/60 both-judge passes; p951.931→2.041s. Reject blanket length expansion; exposed60. |
| Oct13 clause C3B | Complete clause handles preserve qualifiers | Single-clause version rejects46/60 prompts from metadata bloat. Packed version fresh40:40/40 both arms, p951.685→1.796s; posthoc qualifier omissions accepted by both judges. No promotion; ceiling/contamination limits. [Details](research-cycle3.md). |
| Oct13 query/selector studies | Extra plans and source-aware selection improve recall | Earlier constrained plan raw10→11/24 NH and9→10/12 GM; mixed regressions/additional call. No broad adoption. [Outcome](research-cycle3-outcome.md). |
| Oct13 evaluation repair/source restoration | Rubric change fixes grading; restore missing source | Revised rubric9/12 agreement unchanged, rejected. Source restoration11→13 passes on only16/37 complete pairs; transport failures retained. [Details](focused-experiments-20261013.md). |
| Oct13 focused Cycle6 | Full catalogue statistics/building facts improve grounded use | Newly frozen9 synthetic checks6→8, remaining trigger miss preserved; warm p502.996s,p954.274s,max5.215s;49 paid calls. Source/entity overlap, not independent human gold. [Details](focused-results-cycle6.md). |
| Oct14 original Cycle7 | Requested-facet retrieval generalizes across originals | Changed55 GM pairs30→34 raw passes,8 gains/4 losses; all318 raw GM64/113,NH80/205. Warm p954.720s.746 paid requests, cumulative74.45438025. [Details](broad-original-cycle7.md). |
| Oct14 source Cycles8–9 | Restore source and select bounded sections | Source fixes and attribution improvements coexist with delivery/citation failures; no broad promotion. [Cycle8](source-grounded-cycle8.md),[Cycle9](source-grounded-cycle9.md). |
| Oct14 Cycle10 | Separate source/section factors; narrow protocol repair |17original:10/10/9/9 passes across baseline/source/section/both;6synthetic:5 each. Replay final34/37→37/37 valid with no prior-valid changes in328 records.79calls, cumulative82.03191625. [Details](protocol-cycle10.md). |
| Oct14 Cycle11 | Expand quotations with fixed answers |432replayed outputs:422valid in all arms;53masked outputs show different narrow repairs and unresolved attribution. No net quality gain, stop line;0calls. [Details](citation-cycle11.md). |
| Oct14 Cycle12 | Free-form Qwen keyword hypotheses plus source vocabulary |20 original×3 fresh arms. Raw8/10/6 vs masked-source9/9/12; source gainsR034,R095,GM125; vocabulary also losesGM128. p956.140/7.020/11.299s staged sum.139paid calls,.8737252 conservative incremental. Promising source result, no promotion; diagnose dropped candidates. [Details](keyword-cycle12.md). |
| Oct14 Cycle13 | Selection-only equal fusion versus marginal token coverage | 20frozenqueries reused,40fresh answers/40judges. Source-usefulness9/20 equal fusion,10/20 token coverage versus12/20 weighted; each19/20 valid. p959.856/10.431s staged sum.0.594322 increment; no promotion. [Details](keyword-selection-cycle13.md). |
| Oct14 Cycle14 | Fixed-evidence generic checklist |20pairs:raw6→9 with1unscored; source8→9, onlyUIgain; valid18→20; p956.387→7.705s contiguous.80dispatches,2.5678 increment including1unknown conservative settlement.8checks unrun. [Details](use-prompt-cycle14.md). |
| Oct14 Cycle15 | Task-focused fixed-evidence prompt |14pairs:raw5→4; source6→9 (strict4→5), only1borderlinecontentgain; valid13→14; p957.898→8.851s contiguous.56dispatches,.38709increment,cumulative86.45485345.2content-gain gatefailed;8checks unrun;stop testedline. [Details](use-focus-cycle15.md). |

Cycle7 warm latency is **p503.551s,p954.720s,max5.674s**. All times retain their original
measurement scope; different cycles/models/source versions are not a controlled
latency trend. Full experiment documents are authoritative for exact ledgers and
negative cases. Transport failures and reused outputs are never silently discarded.

## Exact keyword model, vocabulary and untested retrieval hypotheses

Cycle12’s approved fast route was **Alibaba Bailian `qwen3.8-flash`**, with20
actual keyword calls and returned model IDs checked. “Small model” is an arm label,
not a verified parameter-count claim. It was not a local model or DeepSeek keyword
stage. Source vocabulary used existing tokenization plus exact book-title/Latin
terms from1507Niuhuang/1174Guangming records: common top25 and lexically related
top60, deduplicated/top-filled to at most90 terms. Original conversational question
was unchanged; separately user-supplied pad/LivePad terms were not source-derived.
The model could propose up to3queries outside the vocabulary, without phonetic
constraints. Deterministic vocabulary expansion instead joined up to5overlapping
source terms. Generation/judging used approved `deepseek-v4.1-flash`.

The20-call keyword result is promising only under assistant source review and has
material latency cost. Cycle13’s two literal selectors did not improve it. Remaining
**untested hypotheses** include semantic/field-aware ranking of valuation clauses,
source-window extraction that preserves speaker plus requested attribute, and a
larger frozen original-question confirmation of the weighted keyword route.
These are hypotheses, not implemented benefits or a claim all retrieval ideas are
exhausted. They require separate source-grounded tests and resource estimates;
no new provider, trained model or extra keyword calls are implied. Cycle14/15 have now tested two generation-use prompt variants with fixed evidence.
Neither met the substantive content-gain gate. Earlier keyword negative findings
remain unchanged; no automatic next paid experiment is scheduled.

## Decisions, resources and open questions

Keep C1 default. Preserve opt-in narrow protocol/source fixes; do not broadly rewrite
unsupported model prose. Reject blanket chunk growth, oversized clause metadata,
unchanged-quality judge rubric and broad citation expansion. Do not train a new
sufficiency/reranker model or run unrecognized code without explicit review.
CPU source-only selectors have negligible API cost but measured local time matters;
one keyword API adds about2.734s median/5.047s p95 in this pilot. Extra verifiers
add latency/cost and require calibration. GPU/training reproduction is unverified.

Cycles14/15 isolate generation instructions with fixed contexts and unchanged
validators. All65 valid outputs across68 preserve raw factual text; one borderline
content rescue does not meet the frozen gate. Further work needs a distinct
hypothesis (for example claim/qualifier selection) and calibrated source labels,
not more spending on this failed gate. The larger40-original keyword confirmation
and both8-case prompt confirmations remain unrun. Avoid picking
one winning arm per question for the main report. Report question, answer, score,
response time in four columns with method/version and source-review caveats.

Outstanding: human source/OCR calibration; source-pool gaps (R065); meaningful
attribute/window coverage (N417); conditional entity interpretation; policy scope
(GM064); citation entailment independent of exact matching; cold/uncached timing;
reproducibility without private source/cache paths. No established novelty or
population improvement. Open questions and failed hypotheses stay in this log.

## Local reproducibility and artifact index

Implementation: `newdomain/keyword_hypotheses.py`, `newdomain/keyword_selection.py`,
`scripts/keyword_experiment.py`, `scripts/prepare_keyword_selection.py`.
Tests are in `tests/test_keyword_hypotheses.py` and `tests/test_keyword_selection.py`.
Each live stage freezes code/input/evaluation hashes, verifies predecessor ledgers,
reserves before dispatch and journals terminal outcomes. Paid execution requires
existing approved provider credentials and authorized local runtime/corpus caches;
this repository alone does not distribute a turnkey benchmark dataset.

Private artifacts under `/Users/monkey/Documents/Codex/2026-10-12/task/`:
`keyword-cycle12-20261014/` (60answers, raw/source scores, masked reviews, report,
settlements, frozen manifests); `keyword-selection-cycle13-20261014/` (plan,
input provenance,40answers,80calls, masked source reviews, verification and tests); `flash41-full-rerun-20261013/presentation/`
(cumulative four-column report and historical appendices). These paths are local,
not public downloads. [Optimization log](optimization-log.md) and the linked cycle
records preserve earlier detailed work without copying huge tables here.


### Earlier Cycle13 closing note — 2026-10-14

Cycle13 recovers GM064’s catalogue source in both arms, yet only equal fusion
avoids the inappropriate subsidy generalization. N417 still misses valuation:
real tokenization keeps很贵 together and source-only literal scoring ignores that
unseen term. R095’s useful raw clarification fails the declared schema in both new
arms; retain PROTO distinct from USE. All40 source reviews are complete, including
regressions and borderline cases.145scope hashes verified,483regression tests plus
10focused optimized checks pass. No active paid stage or open reservations.
A reproducible check finds293/293 delivered citations exact across100outputs,
not proof of entailment and not verification of the historical1206 tally.


### 2026-10-14 Cycle14 negative result

All38valid outputs preserve raw factual sentences. Source-usefulness8→9/20 reflects
onlyGM124’s corrected UI boundary. N170’s biography recovery is offset by答→牛黄
misattribution. N265/R095 become valid but remain semantically wrong. Preserve
PROTO versus USE/intent distinctions. Cycle15 subsequently tested task-focused instructions;
Cycle14’s8frozen synthetic checks remain unrun, not successful confirmations.


### Historical closure — Cycles14/15, 2026-10-14

No active paid work. Cycle15 all164 scope hashes verified,490 offline and17 focused
optimized tests pass. All28 outputs source-reviewed,83/83 delivered citations exact;
exactness is not entailment. Paired evidence/model/validators fixed; prompt-only
changes do not affect defaultC1. Generic then task-focused instructions fail the
predefined substantive-content gate. Richer biographies/definitions already useful
in the fresh baseline are not rescues. GM072,GM127,N466 andR095 remain instructive
failures. Retain all raw grades, borderline sensitivity, the Cycle14 timeout and
unrun frozen checks. Final cumulative conservative spend86.45485345/200.

New implementation/artifacts: `newdomain/evidence_use_prompt.py`,
`newdomain/evidence_use_prompt_v2.py`, corresponding runners/tests;
`use-prompt-cycle14-20261014/` and `use-focus-cycle15-20261014/` private directories.
The report presents one coherent current candidate, all paired outputs in appendices,
and unchanged historical tables. No external paper/code newly adopted in these
cycles; existing acknowledgments remain scoped to actual conceptual influence.


## Factual synthesis for user discussion — 2026-10-14

This section uses completed artifacts only. No new paid inference or algorithm
change. Source-review usefulness is not accuracy, and “small model” does not assert
a verified parameter count.

### Keyword route: exact inputs, full measured overhead and outcomes

Actual keyword model: Alibaba Bailian **`qwen3.8-flash`**,20 responses with actual
model IDs checked. Final answering and judging use `deepseek-v4.1-flash`.
The keyword call's user JSON contains `original_conversational_question`, a
`source_vocabulary` string list, and separate `user_supplied_interface_vocabulary`
(`pad`, `LivePad`). Vocabulary comes from existing tokenization, exact book titles
and Latin terms over1507 Niuhuang/1174 Guangming records:25 common terms plus60
lexically related terms, deduplicated and topped up to at most90. Term-to-source
IDs are retained locally; the prompt supplies terms, not gold source IDs or answers.
The original question is unchanged. Up to3 queries of at most60 characters may
use words outside the list; there is no phonetic-similarity gate. Generated queries
retrieve source text and are never passed off as answer evidence.

The comparator is the freshly run Cycle12 original-query baseline using the
Cycle10 adapter/source/protocol state, **not historical C1**. All20 questions per
arm are exposed diagnostics, not an untouched test population.

| Measurement | Original-query baseline | Free keyword hypotheses | Difference |
|---|---:|---:|---:|
| Source-review useful outputs |9/20|12/20|+3, no observed binary losses|
| Original judge passes |8/20|6/20|−2|
| Mechanically valid outputs |19/20|20/20|+1|
| Full pipeline-component p50 |4.568s|7.912s|+3.344s between arm quantiles|
| Full pipeline-component p95 |6.140s|11.299s|+5.159s between arm quantiles|

The keyword API alone has p50 **2.734s**, p95 **5.047s**. The full numbers above
also include vocabulary preparation, original retrieval, hypothesis retrieval,
fusion/window/prompt preparation, answer generation and canonical validation.
They are measured serial critical-path component sums, not contiguous wall-clock
requests. Cold initialization, uncached embedding network, idle stage gaps and
separate grading are excluded. Per-question full-component *paired differences*
have nearest-rank p50 **+3.596s**, p95 **+6.880s** (range+0.345 to+9.779s);
these differ from subtracting arm quantiles. Provider/generation variation is part
of those observed differences, not a causal estimate of keyword overhead alone.

Source-review gains: R034 speaker attribution; R095 missing-antecedent clarification;
GM125 substantive district information. All three have changed prompts/contexts.
These are not all newly retrieved missing facts: GM125's original selected context
already contained relevant district facts. Same-family assistant review with prior
context and coarse binary labels cannot establish population improvement. The
20 keyword calls cost0.0111792 in the conservative ledger convention; the entire
Cycle12 experiment (20Qwen+119DeepSeek dispatches) cost0.8737252, including judges.
Deterministic vocabulary alone remained9/20 useful: gainGM125, lossGM128.

Equal fusion and literal token coverage were subsequently tested and did not
improve the weighted route (9/20 and10/20 versus12/20 useful). Untested: semantic/
field-aware ranking of valuation passages already in the pool; evidence windows
preserving both speaker and requested attribute; and the larger frozen original-
question confirmation of weighted keywords. Neither8-case prompt confirmation
was run. These remain hypotheses, not hidden successes or proof retrieval is solved.

### Two actual Chinese raw-to-final examples

Both examples are fresh Cycle15 **baseline** outputs from
`use-focus-cycle15-20261014/answers/results.jsonl`; corresponding full prompts,
contexts and traces are retained. They are not constructed examples.

**GM072 — omission already occurs during generation.**

Question: “请开始介绍光明区简介。”

Raw answer:
```json
{"sentences":[{"text":"本次资料未包含回答该问题所需的依据。","evidence":[]}]}
```
Final answer:
```json
{"sentences":[{"text":"本次资料未包含回答该问题所需的依据。","citations":[]}],"handoff":false}
```
Selected D02:1:01 contains science-city/northern-Shenzhen/innovation positioning,
enough for a bounded introduction, though not a full district profile. The model
already refuses before validation; canonicalization changes handles/protocol only.
The task-focused arm also refuses. This localizes omission to generation under
these prompts, **not proof that a particular prompt sentence caused it**, and not
evidence that validation deleted an adequate introduction.

**R095 — downstream delivery rejection of a malformed clarification.**

Question: “它有什么影响？”

Raw answer:
```json
{"sentences":[{"text":"您问的“它”在本次资料中没有明确所指，无法确定要回答哪本书或哪味药的影响。","citations":[{"id":"MD-016","segs":[0]}]},{"boundary":"clarify"}]}
```
Final answer: `null`; gate failure: `unknown/mixed boundary`.

The missing referent warrants clarification, but the generated answer mixes a
factual/cited sentence with a boundary that the contract requires to stand alone.
The historical source citation cannot prove missing conversational context.
The downstream gate causes nondelivery of this raw clarification; generation
caused the incompatible form. This is not a factual answer removed by validation.
The task-focused arm becomes valid by silently choosing《新修本草》as “它”; source
review still fails it. Loosening the validator would not resolve the actual referent.

### What6→9/14 means, and what to do next

A separate assistant, with arm labels/raw scores masked but prior related context,
judged materially useful source-supported **delivered outputs** on14 exposed
original questions (8 targets,6 controls). It accepted6 baseline and9 candidate
outputs. This is a small binary usefulness assessment, not measured accuracy,
perfect support, successful UI execution, or independent human validation.

Only GM126 replaces blanket abstention with candidate-park content; it remains
borderline because noisy-name linkage/development scope are unresolved. GM119
repairs conditional referent wording; GM124 removes an unsupported UI-capability
claim. Neither adds previously missing substantive content. N170 biography and
N325 historical definition were already useful in the fresh baseline, so richer
candidate wording is not a rescue. Excluding all explicitly borderline passes
leaves4→5/14. The frozen requirement of2 content rescues failed; no confirmation
calls or promotion followed.

**Next justified algorithmic hypothesis, not implemented:** a narrow typed policy
fact representation and deterministic rendering, starting with the repeated GM127
failure. Preserve each source policy as a linked record of eligible beneficiary,
location/area/lease conditions, subsidy rate, cap/period and exclusions, all with
source spans. Keep buildings/bases as location conditions rather than recipients.
Generate a policy sentence only from a complete supported record; do not substitute
“符合条件” for eligibility. This differs from merely supplying complete clauses or
adding another reminder: it explicitly represents the relationships repeatedly
lost despite selected evidence. First test record extraction and rendering offline
on independently annotated positive/negative cases, with no new provider calls.
It addresses policy-scope errors only; it will not fix missing evidence or all USE.

Human/user calibration is essential **before treating the broader usefulness gains
as optimization success**: agree whether a tentative noisy-name park introduction,
a conditionally guessed referent, or a historical identity description satisfies
the task; annotate required facets and disqualifying omissions. Those choices
currently determine most of the6→9 gain. The original judge and source assistant
disagree, and fresh synthetic checks would reuse that unsettled standard. This is
an evaluation bottleneck, not a request to keep cycling prompts or an assertion
that all algorithmic avenues are exhausted. No new paid run is scheduled.


## Cycle16: matched lexical control and selective fallback — 2026-10-14

[Full causal audit, original questions and resource accounting](keyword-marginal-cycle16.md). Adding original-query lexical-top20 with the same fusion removes the earlier aggregate Qwen advantage: raw9/20 versus9/20, source-useful12/20 versus12/20, complete8 versus6. Dictionary: raw8/20 plus one unscored timeout, source-useful11/20. All60 scheduled outcomes and masked source reviews retained. This is exposed-development assistant judgment, not human-gold accuracy.

The earlier baseline omitted that lexical pool. Of38 new Qwen-selected case-record pairs,37 were already in original lexical candidates;24 were in dictionary candidates; none outside their union.524 Qwen-only candidate pairs produce one selected and zero cited passages. Nevertheless, useful valuation/inventory candidates get dropped, and GM068 loses flexible-computing coverage despite binary success. Diagnose and test selection before rejecting the strategy; do not rename clarification or richer existing evidence as novel recall.

Staged full p50/p95: lexical4.961/7.212s; dictionary4.785/8.260s (19returns); Qwen8.229/12.841s. Historical keyword-call time is added to measured warm answer pipeline; no live whole-path claim. The frozen no-evidence fallback triggers4/20, yields only one borderline partial gain (useful12→13, complete8 unchanged), and p95 rises to14.174s. No gate retuning or deployment.

119dispatches, zero retries, one conservatively charged generation timeout, zero open reservations at closure. Increment2.85524; cumulative89.31009345/200.151exact citations across55valid outputs do not prove entailment. Cycle17 separately tests bounded facet selection on three diagnosed original questions; defaultC1 remains unchanged. No new external paper/code adopted by this locally written repair.


## Cycle17: evidence-facet repair and evaluation limits — 2026-10-14

[Full paired development result](keyword-facet-cycle17.md):3original questions ×3query arms ×2selectors,18fresh answers. Seven contexts change;53/60prior preparations remain identical offline. No broad-quality or fresh-heldout claim.

N417 changes from bounded abstention to actual historical valuation in all3arms; lexical uses existing book-level evidence, while Qwen contributes explicit弘景曰 evidence. Dictionary retains a conflicting absence sentence; Qwen omits the speaker/transmission chain from its delivered short quote. GM068 Qwen recovers flexible computing and preserves the equal-workload40%+ condition; lexical/dictionary add that number but omit the condition. GM064 Qwen gains optional inventory detail, not a newly recovered technical achievement. Unchanged lexical/dictionary GM064 prompts produce protocol/policy errors; do not attribute their stochastic differences to selection.

Frozen source-usefulness is7→7/9, while conditional complete6→3. The rubric correctly credits safe selected-source abstention but therefore cannot measure end-to-end factual completion: three N417 baseline abstentions count complete even though the corpus has the valuation. Keep these primary ratings unchanged and show targeted-facet recovery separately. This is a measurement limitation, not evidence that recovering the valuation failed. A fresh confirmation needs an explicit end-to-end factual-facet metric, unseen original questions and unchanged controls; none is claimed completed here.

505offline tests and25optimized keyword checks pass;191scope hashes verified.18masked reviews complete;63exact citations across17valid outputs are not entailment proof.36dispatches, one saved answer with missing raw judge after timeout, no retry. Increment2.256376; cumulative91.56646945/200, zero open reservations, no active paid work. The bounded facet selector remains opt-in; C1 default unchanged. No new external implementation adopted or new novelty asserted.


## Cycle18: constraint reminders fail the matched test — 2026-10-14

[Full diagnosis, ablation and exact output examples](claim-constraints-cycle18.md). The [eight failed Cycle16 Qwen cases](keyword-failure-map-cycle16.md) are explained separately; the completed12/20 denominator and primary ratings are unchanged. Candidate recall, selected evidence and a complete delivered answer are distinct.

Cycle18 freezes8originals (4per corpus) and compares unchanged baseline, concise preservation guide, and the same guide plus exact selected-source constraint spans. Offline audit adds original policy headers and marks speaker neighborhoods unverified; all53spans exact. Retrieval, model, evidence, schema and validators fixed across24fresh answers. The new frozen rubric separates factual completion from safe absence/clarification; its labels are not a regrading of Cycle16.

Raw passes4/8in every arm. Factual complete1→2→2 reflects GM169 count-scope improvement shared by guide and cards. No target repair: N417 is already complete in the fresh baseline; GM068 still drops equal-workload40%+ conditions; GM064 still broadens new-materials subsidy scope; R034 acquires unsupported speaker attribution. R095 correct raw clarification becomes protocol-invalid under both interventions. Validity8→7→7; unsupported claims2→3→3. Gate fails: zero target rescues, control regression, no unique span benefit. Stop this candidate; C1 stays default.

Warm p50/p95seconds: baseline3.464/5.323, guide4.402/5.888, spans4.453/7.465. At n=8p95is the maximum. Staged totals add the cached historical keyword call forN417 equally acrossarms; no live keyword-path claim. Span inputtokens32,670vs24,634baseline (+32.6%).48calls cost0.35785; cumulative91.92431945/200, zero open reservations, no paid work active. No transport failures/retries; two invalid outputs retained.513offline tests,8optimized tests,202scope hashes verified;43raw factual sentences unchanged through22valid outputs,48exact citations—not semantic proof.

The next design decision is an explicit claim/condition/attribution output contract with deterministic rendering versus continued free prose. It requires offline design and source-binding validation before further paid work; nothing is implemented or scheduled for that proposal. Human calibration and unseen-original confirmation remain outstanding. No new external paper/code adopted, no push/upload/deployment.


## Cycle19: explicit source-bound claims — 2026-10-14

[Full implementation, paired results and limitations](structured-claims-cycle19.md). The user-approved opt-in alternative selects exact source units with mandatory source/condition/attribution attachments and deterministic rendering. It changes the declared output contract, style and length allowance, so this is a bundled pipeline comparison, not a fields-only ablation. Exact attachment does not prove semantic binding; C1 remains default.

Twelve exposed originals across both corpora,24fresh outputs. Factual completion3→7/12 and unsupported assertions4→0 under frozen same-model source review; valid delivery11→12 under the respective contracts. Three targets repair: R034 marked opinion, GM068 both research facets without optional40% claim, GM064 focused research without optional broad policy. The last two avoid risky claims rather than establish correct condition/policy binding. N417 speaker continuity and GM126 noisy-name intent remain unresolved. Ordinary controls retain completion; clarification improves on R095/GM119. Structured wording is usable but noisy in9/12. Frozen pilot gate passes, but no unseen-original or human-gold claim and no promotion.

Raw judge passes6→3/12. In N405 the judge says author/date absent despite the explicit delivered Sun Simiao/652quote; other disagreements reflect differing coverage expectations. Preserve all grades and source-review limits. Warm p50/p95seconds4.096/9.507→3.363/5.111; staged p957.070for candidate includes historicalN417keyworddelay. n12p95=max, no stable latency claim. Inputtokens37,270→46,935; outputtokens1,368→534; rendered median74→166.5characters.

527full tests,14optimized checks,24frozen-input reconstructions,587exact single-unit renders and215scope hashes verified.51exactcitations across23valid outputs,20candidatecitations visibly rendered; not entailment.48calls, no failures/retries, increment0.347608, cumulative92.27192745/200, zero open reservations. No additional paid allocation, push, deployment or upload. No new external implementation/paper adopted; acknowledgments unchanged in actual-use scope. Human calibration and unseen-original confirmation remain before any default change.


## Cycle20: held-out-from-iteration confirmation fails — 2026-10-14

[Full frozen selection, exact questions, paired outcomes and stopping decision](structured-confirmation-cycle20.md). Candidate b80bf48 and Cycle19 rubric rules unchanged;16 mixed-origin questions outside Cycles16–19 (8 live/real-user,5 pre-existing GM simulated,3 pre-existing NH evaluation), eightpercorpus across ordinary successes/conditions/ownership/intent. All16had earlier historical generations; N265Cycle14 andGM124Cycles14/15 exposure documented. Held-out-from-this-iteration, not truly unseen. Cases with representation/evidence gaps retained rather than replaced.

Source-reviewed factual completion5→7/16 (NH3→3,GM2→4), but valid delivery16→14, source-conditional adequacy8→7, rawjudge12→5. Ordinary GM388 classification regresses because required chart is unselectable and source/unit pairing invalid. GM120 also invalid. GM330 preserves actual required eligibility; GM177/410 gains are borderline completeness judgments. Accepting those two baseline answers as sufficient yields7→7 (posthoc diagnostic, primaryunchanged). GM201 category-to-cap relationship,GM124 “我院”,HOP04datasetcount remain unresolved; N265 clarification and modern-use boundary specificity regress. Frozen gatefails: no promotion and no further paidrun.

32matched-input/743single-unit checks;233scopehashes;73exactcitations across30valid outputs,26structuredcitationsvisiblerendered—not entailment. Unchangedcandidate's prior527+14tests remain evidence, not claimednew executions. Retrieval failed cross-process reproduction on HOP04, so identical frozen contexts were served; cause unresolved and diagnostic retained. Answer-only p50/p95seconds4.102/6.082→4.048/6.372 excludes retrieval, unlike earlierlatencies. Inputtokens50,880→61,811;output1,724→755; candidate9noisy+2undelivered.64calls,no provider failures/retries,increment0.456762,cumulative92.72868945/200,zeroopenreservations. Initial launcher failed beforedispatch due localmodule shadowing; isolatedlaunch fixed harness withoutcandidatechanges.

All rawgrades/sourcejudgments preserved; source-review remains same-model prior-exposed, human calibration outstanding. Lowerunsupportedassertions3→0 does not erase ordinary-control/deliveryloss. Real bottlenecks: long/table evidence representation, semantic relation binding, specific intent boundaries, missingaggregationevidence and retrievalreproducibility. No new paper/code attribution, no push/upload/deployment; C1default unchanged.


## Offline synthesis after Cycle20 — 2026-10-14

**Stop the current structured candidate; keep C1 default.** Its useful property is preserving a complete qualified assertion when the relevant subject, eligibility, basis and cap already occur together. Its failure is forcing every answer through a sentence-sized exact-quotation catalog. The catalog guarantees local text attachment, not semantic coverage or relationships. No additional provider calls, new candidate implementation, reference-score changes or promotion were performed for this review. Ledger stays92.72868945/200USD, open0.

### Five representative original questions and actual output excerpts

Excerpts below are from the completed matched Cycle20 outputs; source OCR is preserved apart from whitespace display. A raw invalid JSON selection is explicitly not a delivered answer. Full answers, context and source-review judgments remain in the private32-row report; these examples were chosen retrospectively for explanation, not a new test set.

#### 1. GM:GM-388 — 优合集创的医疗传感器里，体外检测和心电监测算同一类吗？

Baseline excerpt:

> 不算同一类：资料将体外检测（IVD）类传感器与无创/体表监测类传感器分列为两个不同类别。

Structured candidate (undelivered raw JSON, not an answer):

> {"mode":"answer","claims":[{"source":"S1","claim":"U1","conditions":[],"attribution":"A1"}]}

**Source-backed explanation:** D05:8:01 separates “体外检测（IVD）类传感器” from “无创/体表监測类传感器,” placing ECG under the latter. The selected OCR chart is485characters without sentence terminators; the entire0:485span is rejected by the300-character unit cap. It is visible to the model but cannot be selected. U1instead belongs to S2and describes an incubator operator. The S1/U1attachment fails, and correcting that pair would still leave irrelevant content. This is a representation-coverage failure plus a selection error, not missing retrieval or evidence that the chart distinction is unknowable. Shortening arbitrary rows would also risk detaching headings from their children.

#### 2. GM:GM-330 — 企业出钱发榜解决技术难题，光明的揭榜挂帅资助按出榜的钱算，还是按研发团队投入算？

Baseline excerpt:

> 对经评审通过的重大项目，按发榜方实际出资金额的20%给予最高500万元资助。

Structured candidate (exact quotation in delivered text):

> 支持区内龙头 企业以“揭榜挂帅”的方式发布重大技术攻关需求，鼓励区 内各类创新主体揭榜攻关，对经评审通过的重大项目，按发 榜方实际出资金额的 20%给予最高 500 万元资助。

**Source-backed explanation:** D02:3:01 places “支持区内龙头企业,” “经评审通过的重大项目,” actual issuer contribution,20%and500万元 in the same intact clause. Baseline answers the requested calculation basis but volunteers a benefit assertion whose prose drops the leading-enterprise qualification. The candidate retains it. This is the concrete eligibility success worth preserving, not omission of an optional number. Whether a narrow basis-only answer must volunteer every condition remains a user/domain completeness decision; once the benefit is asserted broadly, its scope matters. Additional damaged OCR clauses in the candidate are unnecessary noise.

#### 3. GM:GM-201 — 在光明做新型显示材料，关键材料项目和补薄弱环节的项目，投资补贴有什么区别？

Baseline excerpt:

> 补薄弱环节项目（新型显示、新能源和5G材料薄弱环节招商）按经评审核定项目实际投资的20%给予补贴，最高不超过1000万元。

Structured candidate (exact quotation in delivered text):

> 对项目落地投资予以支持，按经评审核定项目实际投资的 20%给予补贴，最高不超过 1000 万元。

**Source-backed explanation:** D14:4:01's preceding sentence identifies “产业链薄弱环节集聚招商”; D23:6:01 separately provides supported project types, support mode and “项目建成投产后” prerequisite. The candidate quotes the1000万元rate/cap sentence and operating prerequisite but omits the category joining them to the second branch of the requested comparison. Baseline preserves that category but omits some eligibility in prose. Both are partial under the frozen rubric. Source/condition IDs attached to a sentence do not encode which project category that sentence governs. A complete comparison needs two independently supported benefit records, not three disconnected quotations.

#### 4. GM:GM-124 — 呃，我们还有一页的科技成果是安全连锁保护系统给我们切换到那一页开始讲解。

Baseline excerpt:

> 该系统由深圳先进光源研究院完全自主搭建，基于EPICS/CS-Studio架构，采用冗余架构与故障安全设计，束流切断响应时间最高可达微秒级。

Structured candidate (exact quotation in delivered text):

> 该系统由我院实现完全自主化搭建，可实现定制化开发上层应用软件（上位机）。

**Source-backed explanation:** D36:330:01 later names “单位名称：深圳先进光源研究院”; D30:5:01 directly says “本成果由深圳先进光源研究院完全自主搭建.” Candidate's selected sentence retains “我院,” while its displayed source label names only the generic381-item catalog. The entity resolver is the missing relationship; exact quotation cannot supply it. Baseline resolves the institute but elsewhere says “可切换到该页讲解,” an unsupported UI capability. Candidate avoids that assurance yet does not improve full attribution. Neither issue is corrected by merely enlarging sentence limits.

#### 5. NH:N265 — 它是不是很贵啊？

Baseline excerpt:

> 请补充您指的是哪位人物、哪本书、哪个方剂或哪件事，以及想了解的具体内容。

Structured candidate (delivered boundary):

> 本次资料未包含回答该问题所需的依据。

**Source-backed explanation:** The isolated original question contains no antecedent for “它.” Retrieved price or historical valuation passages cannot identify the intended object. Baseline asks for the missing referent, albeit awkwardly; candidate's generic absence sentence treats missing conversation context like missing documentary evidence. There is no requested factual answer to recover until intent is resolved. This is boundary-reason selection and wording, separate from excerpt coverage.

### Smallest general design recommendation: qualified clauses as an optional output type

Retain ordinary C1 prose with its existing citations and full evidence access. Add a narrowly scoped **qualified-clause segment** only for claims whose full material scope can be assembled and checked from source evidence. Do not force table classification, general introductions, entity explanation and boundary messages through that segment type. This is a proposed engineering change, not an implemented hybrid or a claimed improvement.

A minimal implementation would add one opt-in segment variant alongside existing prose: `qualified_clause(group_id)`. The model chooses an immutable group ID; deterministic rendering supplies the entire qualified clause. Ordinary segments keep their existing prose/citation contract. This requires one versioned output adapter and one group builder/validator, not another model pass or a new retrieval system. A qualified group contains source/version, exact span witnesses, subject/domain, eligibility, calculation basis, rate/cap/period where applicable, and an explicit completeness status. Fields are validated relationships, not labels copied from nearby punctuation. They may be stored as references to an intact self-contained clause first; no requirement to infer every policy as a graph.

Start with unambiguous complete clauses such as GM330. The source-backed group must visibly retain district-leading-enterprise eligibility, reviewed-major-project condition, issuer-actual-contribution basis and the offered20%/500万元benefit. Do not generate a new paraphrase from unverified IDs. Groups with unresolved “该项目/我院,” mixed beneficiaries, uncertain OCR or missing domain must not be labelled complete. Record them as unsupported for this route; preserve supported ordinary answer portions and state the specific limitation rather than silently weaken the policy claim or abstain from the entire question.

Routing must depend on the claim's content and verified group availability, not question IDs or a whitelist of observed wins. A policy-number claim must not bypass qualification checks by being emitted as ordinary prose. Conversely, ordinary factual classification must not fail just because a source has no300-character sentence. Missing-reference, missing-documentary-evidence and unavailable-UI-action boundaries should have separate reasons and appropriate wording; that is a small separate boundary change, not evidence for a renderer improvement.

**What this does and does not buy:** GM330's complete-clause preservation can be reused without removing GM388's ordinary source-backed answer path. It does not solve GM201 automatically: cross-sentence category/benefit links need verified groups before deterministic comparison is safe. It does not resolve “我院” merely from source adjacency, produce absent HOP04dataset counts, or establish modern medical facts from historical sources. The representation coverage and group-construction problem must be made explicit rather than transferred to an untested selector.

Proposed offline acceptance work, before any model experiment: a reviewed fixture for each evidence shape (complete clause, cross-sentence category, table heading/row, anaphoric owner, missing referent); exact-span/source-version checks; reject incomplete policy groups without corrupting unrelated prose; ordinary-path output remains identical when no group is used. Inspect all support relationships manually on these development examples. A subsequent evaluation would still need separately frozen questions and human-calibrated criteria. Do not claim a lower cost or latency until measured; the proposed route adds no required model pass but may increase prompt size/validation work.

### Retrieval reproducibility is a separate confirmed mechanism

The original Cycle20 pre-call reconstruction swapped NH-HOP04's MD-023-0004forMD-023-0002. This review reproduced that same alternative selection using **only the lexical pool/fusion**, with identical records, question and baseline IDs, no dense retrieval, generation or renderer. Across20Python hash seeds,19select0002and seed14selects0004. Three full offline restarts at seeds0/1/2also retain the same baseline IDs; their score rounding varies.

`newdomain/evidence_pool.py` computes scores with `sum(... for g in q & gs)`. Set iteration order changes with process hash seed. At seed14, the mathematically equal title-overlap scores become9.405013009357269for0002and9.405013009357270for0004—one floating-point unit apart. Sorting by descending score before ID means the nominal ID tie-break never sees a tie. Interleaving and `keyword_control.select` then propagate the changed rank to selected evidence. This is sufficient to reproduce the saved source swap independently of rendering. The original failed process's seed was not recorded, so this does not prove there are no additional nondeterministic components.

A diagnostic calculation using sorted terms and `math.fsum` gives the same score and key-top5ordering across all20seeds. **No ranking code was changed.** A future focused reproducibility fix should canonicalize score accumulation in both pool scoring and lexical window scoring, retain explicit ID/offset tie-breaks, and compare complete context text/order/hashes across processes and seeds. The stable diagnostic key ranking is not yet proof of a complete-pipeline fix. Numerical backend warnings from the full retrieval startup are retained separately; they are unnecessary to reproduce this lexical instability and should not be declared its cause without evidence.

Cycle20 served its already-frozen contexts identically to both arms after this mismatch; its answer-only timing and matched rendering comparison therefore remain correctly scoped. It establishes no live retrieval latency or stability. Neither the table failure nor the policy/owner binding failure should be blamed on that separate retrieval defect.

### Decisions still needed for discussion

1. **Required versus volunteered policy detail:** is a correctly scoped calculation-basis answer sufficient, or should every numerical benefit include the full eligibility set? The answer affects GM330/201 grading and how large qualified groups must be. Required information should be visible in delivered text, not only citations.
2. **Presentation and OCR trust:** permit concise paraphrase for ordinary tables while preserving heading/row provenance? Who verifies ambiguous OCR hierarchy and owner links before a group can be called complete? Enlarging quotation limits alone does not settle those relationships.
3. **Intent and domain boundaries:** when the antecedent is missing, should the assistant ask a focused follow-up using available conversation state? What explicit wording is required for modern-use uncertainty and unsupported UI actions? Generic abstention is safe in some cases but not equally helpful.
4. **Evaluation standard:** calibrate the borderline GM177/410 completeness gains and historical-introduction coverage with a human/domain reviewer. Preserve raw and source scores; do not tune the rubric to make the proposed hybrid win.

This review is a stopping point for discussion. No speculative model cycle, runtime implementation, push, upload or deployment. Local diagnostic artifacts contain the five paired examples and20seed results; spend remains unchanged. No new paper/repository method was adopted, and no novelty is asserted.


## Retrieval repair and prose diagnostics — 2026-10-14 (historical preparation)

User authorized implementation after the denominator audit. Commit8289861 replaces
unordered floating-point overlap sums with sorted-term `math.fsum` in lexical
pools, keyword windows and token-coverage gains. Existing record-ID and earliest-
offset tie breakers remain; there is no rounding tolerance or changed weighting.
Six fresh processes (hash seeds0,1,2,7,14,19) reproduce identical context and prompt
hashes on16 mixed-origin questions spanning both corpora. NH-HOP-04 is the sole
context difference against frozen Cycle20: the formerly unstable tie now selects
MD-023-0002 consistently. Historical outputs/scores are not rewritten.

The generation revision retains ordinary source-cited prose and full selected
source/table order; it adds optional exact whole policy-section clauses rather
than requiring every answer to select a short quotation unit. No300-character
unit exclusion applies to ordinary factual prose. Structural grouping does not
certify cross-sentence semantics, OCR hierarchy or speaker ownership. Typed
clarification, missing-evidence, UI and modern-evidence boundaries are separate.
No new external paper/code is used; existing acknowledgments retain their scope.

Cycle21 reused the16 exposed mixed-origin questions from Cycle20 (8live,5simulated,
3evaluation) with32 fresh answers and32 fresh reviews. Baseline is the Cycle10
adapter plus repaired deterministic original lexical fusion, not exact historical
C1. Both arms have the same selected evidence and unchanged original full-run
judge rubric. Baseline raw passes11/16 versus candidate10/16; valid16/16 versus
14/16; paired1win/2losses. Warm staged latency p50/p95 is3.716/4.639s baseline and
3.545/6.295s candidate (linear interpolation; n16 is unstable). All64 calls settled
without failures/retries, incremental0.316342, cumulative93.04503145/200.

The candidate restores valid table classification (GM388), retains explicit
policy eligibility/basis/cap (GM330), provides specific clarification (N265), and
handles UI-plus-content (GM124). These are exposed mechanism checks, not overall
performance gains. It unnecessarily clarifies GM120 and adds irrelevant material
in several answers. Two candidate delivery failures are contract artifacts:
GM177 appends clarification to factual prose; GM201 provides complete clauses
then restates their amounts. Raw grades and invalid responses remain preserved.

Commit55cd844 permits partial factual prose with an explicit clarification and
permits numerical policy explanations only beside selected whole clauses whose
same-source amount set contains every stated amount. It does not discard factual
text or infer semantic relationships. Instructions also distinguish explicit
objects from unresolved referents and discourage unrelated background/medical
boundaries. The complete offline suite passes541 tests. Cycle22 freshly tests
this v2 contract on the same exposed16 cases; it is not independent confirmation.
The subsequent full benchmark is planned as665cases ×2 independently regenerated
arms (645 mixed-origin questions plus20 separate fixed-context regressions), with
no saved-answer reuse, new exclusion or claim of unseen questions. Outcomes and
ledger totals will be appended after completion; no promotion is authorized.


## Fresh full benchmark freeze — 2026-10-14 (frozen protocol)

Cycle22 completes32 fresh outputs/64 calls: baseline12/16 raw passes and16/16
valid, candidate13/16 and15/16 valid; paired2wins/1loss. Warm staged p50/p95
3.861/8.859s baseline versus3.658/4.921s candidate. Increment0.317146, cumulative
93.36217745/200, no retry/provider failure. This remains an exposed mixed-origin
diagnostic, not full performance. GM201 is still invalid because one comparison
clause crosses the selected D14 pages3/4 and lacks an eligible complete group.

Before the full freeze, v3 adds multi-source clauses only for explicit adjacent
selected pages of the same document, with separate exact offsets/citations and
no cross-document joins. The numeric policy summary remains linked to selected
whole clauses; semantic relevance and category binding are not certified.
Three NH supplied evaluation questions also had selected text matching the existing
contact-name denylist. Preflight blocked both arms before dispatch. Additional
exact redaction now applies symmetrically to outbound evidence/questions/references;
only already-approved institution literals retain their existing exemption.
No question was excluded or silently replaced. Private originals are unchanged.

Candidate freeze1443e35:546 offline tests pass; all665 two-arm inputs match;934
whole-clause renders verify exact source custody; all1330 generation prompts
pass the existing privacy screen. All258 scope files match. This v3 repair has
offline validation plus preceding v1/v2 diagnostic evidence; no separate v3 pilot
score is claimed. Full roster: GM113real+217simulated, NH205live+110evaluation,
20 separate fixed-context regressions.1330 independently fresh generation jobs
and1330 fresh reviews; zero saved-generation reuse. Historical exposures and
the16 diagnostic overlaps remain disclosed. Current baseline is the Cycle10
adapter with deterministic original lexical fusion, not exact historical C1.

Remaining allowance before full allocation106.63782255. Recent diagnostic usage
projects13.181380625 for2660 calls; a deliberately pessimistic UTF-8 payload-size
scenario is129.623696 and exceeds remaining allowance. Neither scenario replaces
the enforced ledger: each call reserves the pinned full-context bound (2.0064),
actual usage settles, and up to3 in-flight reservations total6.0192. The run must
stop on admission/provider failure before exceeding cumulative200; complete
execution is not guaranteed under pessimistic usage. No automatic retries.

The primary private report has one four-column question/answer/score/latency
view with a whole-arm switch, never per-question best-answer selection. It labels
partial progress and includes every scheduled record, failure and unscored item.
A24-case source audit is selected by fixed case-ID hashes,6 per origin stratum,
without reading scores; it supplements the complete raw evaluation and is not
human gold. Candidate/prompt/rubric remain fixed during the full run.

## Completed primary benchmark and blocked regression correction — 2026-10-14

**Do not promote grounded-prose-v3.** The first complete fresh paired run on the
645 eligible mixed-origin questions yields **388→382 model-and-delivery passes**,
**636→585 valid outputs**, and warm staged p95 **4.918→5.513s**. Niuhuang improves
while Guangming regresses. The deterministic ranking repair is independently
verified; this generation bundle does not establish an overall improvement.

| Population | n per arm | Baseline passes | Candidate passes | Valid baseline→candidate | p50 baseline→candidate (s) | p95 baseline→candidate (s) |
|---|---:|---:|---:|---:|---:|---:|
| Primary mixed-origin pool |645|388|382|636→585|3.913→3.924|4.918→5.513|
| Guangming |330|225|208|329→281|3.831→3.873|4.817→5.364|
| GM real-user |113|74|71|112→108|3.953→4.102|4.878→5.770|
| GM simulated |217|151|137|217→173|3.773→3.801|4.764→4.891|
| Niuhuang |315|163|174|307→304|3.995→4.018|4.975→5.540|
| NH live |205|113|117|199→200|3.994→4.110|5.081→5.941|
| NH supplied evaluation |110|50|57|108→104|4.035→3.757|4.915→5.312|

Pass means all four frozen judge axes equal2, citation entailment and reference
completeness true, **and valid delivery**. The unchanged raw judge JSON is retained.
Before the delivery gate, primary rubric passes are391→413; these are not delivered
successes. Paired primary outcomes are73 wins/79 losses (GM29/46; NH44/33).
The descriptive exact two-sided McNemar p=0.685 does not support a gain and is not
a population-valid efficacy claim on this exposed, model-judged roster.

Both arms independently generated every answer and review:1330 generations and
1330 reviews across645 primary plus20 regression cases. All scheduled outputs
are recorded/scored; zero execution failures, retries, answer reuse or new exclusions.
At closure258 frozen scope hashes matched; the later isolated parser correction
is versioned separately, and the original runner is archived privately. Candidate
freeze1443e35, same retrieval/context across arms, baseline Cycle10 adapter with
repaired lexical fusion—not exact historical C1/current-default reproduction.
The preceding16-case diagnostics overlap this historically exposed pool. Regression
contexts were fixed fixtures; primary retrieval ran locally with cached embeddings.
Latency is the sum of warm retrieval/prompt, generation and validation stages,
excluding queue, grading, cold setup and new embedding requests. One generation per
arm; no human gold, independent-provider judge or unseen confirmation is claimed.

### Regression adapter defect and transparent correction attempt

The original20 baseline regression fixtures requested GM `evidence` handles but
were sent through NH canonicalization. All20 failed `sentence_schema`; the candidate
passed20/20. **The apparent regression0→20 and combined665 gain388→402 are invalid
comparative evidence.** Primary645 parsing is unaffected. All original outputs and
scores remain unchanged, including the defective regression rows.

Commit3eeea7e routes regression fixtures to the correct GM parser.20 targeted
unittest checks pass, and offline reconstruction accepts all20 existing baseline
outputs under their requested schema; these reconstructions are diagnostic only,
not retroactively rescored successes. A separate frozen20-pair correction scheduled
40 fresh answers/40 reviews. Its first3 connection attempts failed before headers
or usage; admission stopped, with0 generations/reviews and37 outputs unstarted.
No automatic retry or hidden substitution. Exact network/provider cause is not
established. Corrected paid regression validation therefore remains **blocked**.

### What the source audit explains

A fixed hash sample selects6 cases per origin (24 questions/48 answers). This
assistant reviewed selected source evidence with arms visible and raw scores hidden,
then froze annotations before comparing scores. It is prior-exposed, not arm-blind,
not human gold, and not a full-corpus recall audit. Sample factual completion is
14→10/24, source-conditional adequacy18→14/24 and valid delivery24→22/24. Unsupported-
relation flags2→4 include borderline OCR identity and eligibility interpretation,
not four proven fabricated facts. These sample rates must not be extrapolated to645.

| Observed mechanism | Paired evidence and practical consequence |
|---|---|
| Numeric answer-use regression | GM048 baseline computes42above+4below=46 with the numbering assumption; candidate repeats the range. Candidate prompt replacement dropped existing source-derived floor guidance. This is a bundled prompt regression, not retrieval failure. |
| Overstrict delivery contract | GM305/315 baseline answers the requested calculation basis; candidate is rejected. Across the primary pool,40 candidate failures are numeric-policy clause/amount checks,10 fact schema,9 source handle and1 qualified handle. Exact clause enforcement costs usable answers. |
| Relation/scope errors remain | GM142 candidate reverses the381-collection versus over1000-online relationship. GM059 identity binding and GM362 missing preceding category heading remain uncertain in both arms. Full quotation does not prove semantic relevance or OCR layout. |
| Boundary usefulness can improve | GM193 explains missing current application dates rather than giving a generic refusal. NH-SKILL-044 distinguishes historical memory wording from modern cognitive evidence. These local improvements do not offset full-pool losses. |
| Retrieval/aggregation still limits answers | NH-HOP-04 still lacks the requested corpus count and two formula names. Adjacent-page clause assembly only works when both pages are selected; it does not recover a missing page. |

Twelve source-review/judge adequacy disagreements remain in the sample. Some concern
reference material absent from selected retrieval (for example additional awards
or formula indications); others concern ambiguous intent or eligibility inheritance.
They are **not automatically judge errors**. The source audit can assess selected-
evidence binding without proving complete corpus coverage. Preserve both judgments
for human/domain calibration instead of changing a rubric to favor a candidate.

### Cost, artifacts and research interpretation

The complete run costs14.162858USD; cumulative107.52503545 at its closure. The
failed correction reserves and conservatively settles3×2.0064=6.0192USD because
usage is unknown. **Final conservative cumulative113.54423545/200USD; remaining
86.45576455; zero open reservations and no active paid run.** Unknown-use charges
are upper-bound accounting, not confirmed provider billing. Including the two
0.633488 diagnostic stages, this continuation adds20.815546USD to92.72868945.
Primary generation input tokens decrease2,019,315→1,679,897, but judge input rises
983,724→1,273,994 because broader quotations travel with answers. Output tokens are
81,776→82,314; lower generation input did not improve p95.

Private artifacts: `grounded-prose-full-v3-20261014/` contains frozen inputs,
all responses, scores, completion verification, source audit and primary metrics;
`grounded-prose-regression-correction-20261014/` retains the parser reconstruction,
failed requests, unstarted roster and closed ledger. The single primary four-column
report is `flash41-full-rerun-20261013/presentation/report.html`; historical report
and failed correction are linked as secondary evidence. No artifact upload/push/
deployment. HTML structure and row accounting are checked; browser visual QA was
unavailable and is not claimed.

This remains the known problem of evidence sufficiency versus faithful answer use,
with an additional engineering contract tradeoff. Earlier S2G-RAG/CompSelect concepts
motivated bounded evidence work; this independent prose/whole-clause implementation
is not a reproduction or new academic method. Existing README credits retain their
actual-use scope; no new upstream code/prompts/weights were adopted. The next
bounded research questions are whether a non-destructive clause aid preserves
conditional coverage without rejecting ordinary explanations, whether source-aware
numeric helpers survive prompt changes, and whether layout/identity evidence resolves
relation ambiguity. Human calibration, independent testing and corrected regression
validation are still needed; no further paid optimization is scheduled.

## Invalid-output diagnosis and regression recovery — 2026-10-14

**Baseline retained; no candidate promotion.** The primary645 live results remain
388/645 baseline versus382/645 candidate passes and636→585 valid outputs. The
regression adapter defect never applied to primary GM/NH routing. Its corrected
fresh20-pair recovery now completes: baseline20/20 passes/valid versus candidate
19/20, with0wins/1loss. Candidate's remaining failure adds an unallowed top-level
`note`; the frozen root-schema check correctly rejects it. Raw judge rubric passes
20/20 in both arms do not make the undelivered candidate output successful.

| Corrected regression (20 cases/arm) | Baseline | Candidate |
|---|---:|---:|
| Model-and-delivery passes |20|19|
| Valid delivery |20|19|
| Warm staged p50 (seconds) |4.223|4.359|
| Warm staged p95 (seconds) |5.267|5.558|

All40 answers/40 reviews are fresh under a new recovery ID, same fixed fixture
contexts/prompts and unchanged candidate generation contract.274 scope hashes
matched at closure. No in-run retry/failure, no saved generations substituted.
The recovery explicitly reattempted the three previously failed logical jobs and
newly attempted37. Prior failed requests, unknown usage,6.0192 conservative charge,
and37 unstarted rows remain in the original correction artifact. Do not describe
this cumulative history as retry-free or rewrite its original0→20 parser artifact.

### Exact mechanical categories across primary invalid outputs

All69 invalid responses (60 candidate,9 baseline) parse as JSON; none is a JSON
syntax failure. Schema/protocol noncompliance and semantic correctness are separate
axes. A mechanical rejection is neither proof of hallucination nor proof of a
correct answer being lost.

| Candidate rejection category | Count | Diagnosis / action |
|---|---:|---|
| Numeric policy, no required Q selected |19|Model violates explicit whole-clause contract; source amounts may still be correct. No check waived.|
| Numeric policy, selected Q does not cover every stated literal with its bound source |21|Includes wrong/incomplete clause choices, user premises and calculations. Ten cases have no matching selected clause source for the rejected statement. Requires semantic/operand evidence, not a blanket numeric whitelist.|
| Mixed `text` + `boundary` objects |10|Prompt explicitly permits only a boundary object alone. Dropping arbitrary boundary prose could discard claims; not normalized silently.|
| Four source handles where prompt allows at most three |9|All handles exist and are distinct; this is a presentation-limit/model-compliance issue, not unknown sources. Increasing the limit would be an explicit contract change.|
| Repeated valid Q handle |1|Prompt does not forbid repeat selection, renderer rejected it. General idempotent exact-clause fix917a7a6 recovers this one case.|

Baseline9: four clarification protocol violations (three non-exclusive clarify,
one mixed text/boundary); two invalid segment references; two title-support/alias
failures; one overlong sentence. The latter is172characters against160 in the GM
contract. These are not the regression wrong-corpus-parser bug. No unsupported
segment, uncited title or unverified alias was silently repaired.

Among40 numeric rejections,34 have every rejected literal somewhere in their cited
source text. That is **not** semantic support: it does not bind beneficiary, basis,
period, cap or an OCR table relationship. The other six include user premises,
arithmetic and a missing own-citation continuation. Their evidence is preserved in
private `invalid-classification.json`, with per-statement amounts/source bindings.

### Recoverable correct answers versus unsafe blanket acceptance

Source-visible assistant review establishes a **lower bound of five sound candidate
answers** in the60 invalids; this is not a complete semantic adjudication or human
gold. Only one is mechanically recovered by the narrow fix. Four remain rejected
under the frozen literal-matching contract:

- GM293: both platform-construction and compute-purchase subsidy summaries match
  the full selectedQ12, including conditions, rates/caps/duration. Rendering its
  duplicate selection once preserves all factual prose and exact evidence.
- GM325: user35% falls in the30–40% band;10+30=40万元, below60万元 cap. The guard
  rejects the user-provided35%, although both full policy clauses are selected.
- GM197: conditional800万元×50%=400万元, capped at300万元; eligibility and cap remain
  explicit. User premise and derived value need typed verification, not quotation.
- GM305: correctly distinguishes annual sales increment from gross600万元. The
  rejected600万元 is the user's premise in a negative comparison, not a policy cap.
- GM309:200/300/500万元 caps imply100/300/200万元 differences; source and no-subletting
  condition are retained, but derived100万元 is rejected.

Counterexamples show why broad acceptance is inappropriate: GM168 asserts−196°F
where the cited source supplies only`-196&#176;` with no scale; neither F nor C may
be inferred from that string. GM304 supplies a monetary-unit/600万元 continuation
missing from its own cited page excerpts. GM297 confuses the requested cloud-service
versus university AI-service comparison with other expenditure categories. These
are source/task defects independent of formatting. Remaining invalids are mechanically
classified, not all semantically adjudicated; no total hallucination count is claimed.

### Controlled offline parser ablation

Commit917a7a6 renders repeated identical valid Q selections once and records their
provenance. It preserves all ordinary factual/boundary text and exact source spans;
unknown handles, unsupported amounts, duplicate JSON keys, mixed schemas, envelope
and length checks remain.23 targeted unittest checks pass, including adversarial
wrong-amount/unknown-handle/extra-root/mixed-boundary cases.

All645 saved primary pairs plus20 corrected regression pairs are replayed through
the current parsers: **one change only**, GM293 candidate invalid→valid. Baseline
primary636/645 stays636; candidate585→586/645. All1,260 previously valid answers
across those populations remain identical. Corrected regressions stay20→19/20.
Original result files retain their SHA256 hashes and all original scores. This is
an offline deterministic parser ablation, not a fresh generation benchmark; no
new overall pass rate or latency result is substituted for the original.

Scientific scope before further spending: unchanged prompts/models permit the
controlled all-case saved-response replay to isolate this parser effect at zero
API cost. No primary paid rerun was needed or dispatched. A future change to numeric
rules, boundary schema or source-count prompts would need newly frozen paired tests
with controls, not just regrading these exposed invalids. Any full performance claim
would require both arms on the645 primary roster; the observed full1330-output run
cost14.162858USD provides a planning scale, not authorization to launch another run.

### Connection diagnosis and final accounting

The restricted shell reproduced DNS`gaierror errno8` in1ms. The same approved host
resolved four addresses and established TLS1.2 through the permitted execution
route, with no credentials sent during diagnosis. This explains the boundary and
is consistent with the earlier immediate errors; the original transport did not
capture DNS-level cause, so exact historical causality remains an inference.
One authorized ledgered health check after cooldown returned expected JSON/model/
usage (30input/5output tokens), costing0.0001USD. No auth, endpoint or provider change.
The following fresh regression recovery costs0.352486USD.

**Final conservative cumulative113.89682145/200USD; remaining86.10317855; zero open
reservations and no active paid run.** Prior unknown-use6.0192 remains charged.
Private artifacts: `grounded-prose-invalid-recovery-20261014/` (classification,
source notes, network diagnosis, health settlement and all-case offline replay),
`grounded-prose-regression-recovery-20261014/` (fresh corrected pairs and ledger).
The primary four-column report shows original645 results, corrected20 regressions,
and the one offline recovery separately. Historical failures and blocked attempt
are secondary preserved evidence. README credits are unchanged: no new external
paper/code/prompt/weight adoption. No push, upload or deployment.


## Research-informed component ablations — 2026-10-14

The [component protocol and source matrix](component-ablations-20261014.md) integrates
both source-review rounds, separates in-window papers from older supplementary
work, and freezes A/B/C/D contrasts before paid evaluation. A0 retains only the
verified idempotent parser repair. Further methods are considered or proposed,
not claimed as implemented improvements. Budget remains $113.89682145/$200;
$35 is reserved for broader confirmation and $10 for uncertainty.


### Component-ablation checkpoint: incomplete, baseline retained

The [trial record](component-ablations-20261014.md) now includes A0, B1, C0 and D0 offline controls and the interrupted fresh A1/C1 experiment. On 68 frozen development cases ×3 arms, 85 outputs/reviews completed; three calls were interrupted and 116 output jobs remain unstarted. Automatic approval review rejected paid continuation for lack of recognized trusted parent clearance. All 284 scope hashes passed; no historical outcomes were rewritten.

Two observed pairs have identical delivered answers and identical review prompts but opposite pass/fail judgments. These are demonstrated judge inconsistencies, not measured component regressions. Five discordant pairs were source-reviewed separately; broad-introduction completeness remains uncalibrated. No aggregate improvement claim, combination or confirmation is warranted. The baseline remains in place.

Cumulative conservative spend is **$120.78139745/$200**, remaining **$79.21860255**, zero open reservations and no active paid work. The partial trial cost $6.884576 includes $6.0192 for three unknown-use interrupted calls; no retries. Private artifacts are `component-A1-C1-development-20261014/` and `component-ablations-20261014/`. No push, upload or deployment.


### Offline source adjudication: no new calls

The [updated ablation record](component-ablations-20261014.md#offline-adjudication-after-continuation-denial) audits all85 saved reviewed outputs:53cases, only4complete triplets,15A1pairs and11C1pairs. It withholds overall gains and preserves all raw outcomes.

GM349's two identical answers share a verified missing-procedure defect: preceding page6 was in the lexical candidate pool but dropped from selected context. NH R063's two identical introductions are source-supported; the opposite verdicts arise from an unstable optional-detail requirement. These are separate assistant source adjudications, not rewritten judge scores or human gold. C1 also drops a useful comparison source in NH-LIVE-07; another apparent C1 regression occurs on an identical fallback prompt and cannot be attributed to packing. Baseline retained; paid continuation blocked. Spend and remaining budget are unchanged at $120.78139745 and $79.21860255, with zero open reservations.
