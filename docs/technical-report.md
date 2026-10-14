# RAG optimization: cumulative technical report

Canonical project narrative and dated research log. Last updated **2026-10-14**.
Detailed experiment records linked below retain frozen inputs and negative results;
this document is maintained as the project develops into a technical report.
Local artifacts remain private. No push, publication, upload or deployment is authorized.

## Experimental principle and active keyword investigation

An initial aggregate score neither accepts nor rejects a strategy. Each strategy
gets a diagnostic optimization stage: inspect hypothesis quality, marginal evidence
recall, fusion/selection, answer use, and latency separately; repair the weakest
supported mechanism and retest controls. Preserve negative results and material
regressions. Stop based on measured tradeoffs, exhausted justified hypotheses, or
actual evidence/calibration blockers, not one disappointing aggregate score.

The current authorized focus is **keyword diffusion**, including source-grounded
marginal candidate accounting and targeted selector diagnosis with downstream
settings fixed. The typed-policy-record idea below is deferred. Cycle14/15's failed
prompt gate is a result for those versions, not rejection of keyword diffusion or
all generation interventions. No additional paid work has started during this audit.

## Current state

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

Latest settled conservative cumulative spend: **86.45485345 of200USD**, including
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
The retained original-question roster contains318 records:205 Niuhuang and113
Guangming.64 sensitive live questions were excluded upstream. Niuhuang’s315
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


### Latest closure — Cycles14/15, 2026-10-14

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
