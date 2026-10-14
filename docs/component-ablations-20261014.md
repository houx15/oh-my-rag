# Controlled component ablations — 2026-10-14

Latest status: the116authorized jobs are complete. Primary passes: baseline28/48, A1 26/48, C1 25/48; regressions20/20,18/20,18/20. Neither component is promoted. Cumulative$121.98103945; remaining$78.01896055; no active paid run. Earlier blocked-state entries below are historical.

Baseline remains the Cycle10 adapter with deterministic original-query lexical fusion, not exact historical C1. Grounded-prose v3 is a rejected overall candidate: on 645 primary cases its original valid-and-all-rubric passes are 382 versus baseline 388; validity is 585 versus 636. Corrected fresh fixed-context regressions are 19 versus 20 out of 20. The narrow duplicate-clause repair independently recovers one saved candidate output (585→586 valid), preserves all 1,260 previously valid outputs, and does not establish a new generation pass rate. Original outcomes remain immutable.

## Verified research and applicability

Requested paper window is October 12, 2025–October 12, 2026 inclusive. Inspection on October 14 does not extend eligibility. Submission and publication are separate dates; software references have no paper-window eligibility implied. These are known research problems and testable local hypotheses, not novelty claims.

| Source and date | Measured problem → actionable hypothesis | Verification, cost and status |
|---|---|---|
| [VeriCite](https://arxiv.org/abs/2510.11394), first submission October 13, 2025; in window. arXiv identifies SIGIR-AP 2025 and [DOI](https://doi.org/10.1145/3767695.3769505); exact publication day not independently verified. | Cross-page support and missing qualifiers → evaluate claims against cited passage groups, preserving claims during verification. | [Official implementation](https://github.com/QianHaosheng/VeriCite/blob/main/vericite.py) uses local vLLM, English NLTK segmentation and a fixed CUDA device. Reviewed hazards include dropping unsupported claims and synthesis after verification. Software license unverified; no copying or execution. Considered for offline evaluation, not an extra production judge. |
| [Recall Is Not Enough: A Reader-Context Diagnostic for Budget-Constrained RAG](https://arxiv.org/abs/2607.00725v2), first July 1, 2026; v2 August 5, 2026; in window, publication venue unverified. | Retrieved evidence may disappear during packing → distinguish candidate availability, selected-source coverage and actual retained-text support at fixed budget. | [Author repository](https://github.com/nayanananto/Diagnostic-for-Budget-Constrained-Multi-Hop-RAG) retains an older title. Source review found short-term filtering, whitespace truncation, potentially oversized first selection and quadratic similarities. Authors report limits with stronger readers/tuned heuristics. License unverified; no copying. Candidate diagnostic adapted independently below, no efficacy reproduction. |
| [Instructor retry](https://github.com/567-labs/instructor/blob/main/instructor/v2/core/retry.py) and [OpenAI handlers](https://github.com/567-labs/instructor/blob/main/instructor/v2/providers/openai/handlers.py) | Valid JSON but invalid response contracts → one schema definition and error-specific diagnostics; test content-preserving handling separately from generation. | [MIT](https://github.com/567-labs/instructor/blob/main/LICENSE). Generic retries do not ensure minimal semantic edits. No installation/copy/provider compatibility claim; bounded re-asking is considered, not enabled. The completed duplicate-Q repair predates this review and is not attributed to Instructor. |
| [CiteCheck](https://arxiv.org/html/2502.10881v1), first February 15, 2025; outside window, supplementary older work. | Citation overlap is insufficient for condition/cap correctness → remove or mutate a qualifier and test whether the answer-support judgment changes. | [Official repo](https://github.com/xzy-xzy/CiteCheck), [MIT](https://github.com/xzy-xzy/CiteCheck/blob/main/LICENSE). Paper and directory/schema verified; not a complete implementation audit or reproduced benchmark. Proposed offline counterfactual evaluation with source review; no training or online judge adopted. |
| [XGrammar HF integration](https://github.com/mlc-ai/xgrammar/blob/main/python/xgrammar/contrib/hf.py) | Schema-invalid responses → constrained decoding if the serving stack supports it. | [Apache-2.0](https://github.com/mlc-ai/xgrammar/blob/main/LICENSE). Requires generation-logit control. [Bailian structured-output documentation](https://help.aliyun.com/zh/model-studio/qwen-structured-output) distinguishes JSON syntax from strict schema and has model restrictions; it does not certify our exact DeepSeek endpoint. Considered only; no provider probe or dependency. |
| LlamaIndex [fusion](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/retrievers/fusion_retriever.py) and [auto merging](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/retrievers/auto_merging_retriever.py) | Expansion can displace original evidence; parent merging may add irrelevant text → track branch provenance and protect original evidence before filling uncovered facets. | [MIT](https://github.com/run-llama/llama_index/blob/main/LICENSE). Original query inclusion alone does not guarantee final retention; inspected RRF path does not use retriever weights. Default child-ratio merging does not prove qualifier preservation. Independent offline control proposed, no copied code/dependency. |
| [Docling hybrid chunker](https://github.com/docling-project/docling-core/blob/main/docling_core/transforms/chunker/hybrid_chunker.py) | Table rows lose headers, or conclusions lose conditions → exact-source dependency bundles of row/header/title/qualifier, within a fixed byte budget. | [MIT](https://github.com/docling-project/docling-core/blob/main/LICENSE). Header repetition is conditional on table representation/serializer; oversized metadata may be dropped. Considered, not installed; no claim that arbitrary OCR text supplies reliable table structure. |
| [Do RAG Systems Cover What Matters?](https://aclanthology.org/2025.naacl-long.301/), NAACL April 2025; outside window, supplementary older work. | Unnecessary abstention and incomplete comparisons → distinguish required answer facets from optional background/follow-up content. | [Author notebooks](https://github.com/SalesforceAIResearch/answer-engine-eval/tree/main/Xie.et.al.2024), [Apache-2.0](https://github.com/SalesforceAIResearch/answer-engine-eval/blob/main/LICENSE). Folder year is not publication date. Notebook inspection reported by the coordinating research review; this executor did not run them. Proposed offline annotation, not three added online model calls. |

All repository links above point to moving branches inspected read-only, not pinned runnable reproductions. Any future source reuse requires a pinned revision and license/notice review. No upstream code, prompts, weights or datasets were copied, installed or executed. Conceptual use in the diagnostic protocol is distinguished from implemented generation methods. Model-judge/OCR agreement is not human gold; citation substring inclusion is not entailment.

## Frozen experimental protocol

One writer and one active ledger. Current conservative cumulative spend is **$113.89682145 of $200**, leaving **$86.10317855**; no open reservations. Failed unknown-usage calls remain charged. No paid calls until a concrete arm, roster, hashes, costs and closure checks exist. Use only the approved model/provider and existing screening. No silent retries, hidden exclusions, push, upload or deployment.

The common source roster is the frozen 645 primary cases plus 20 corrected fixed-context regressions. All are historically exposed, including diagnostic examples. Select a deterministic origin-stratified development subset using case identifiers only before examining component outcomes. Remaining cases are a confirmation partition, not an unseen holdout. Freeze question/context/reference/config/code/model/prompt hashes separately; reference material never enters retrieval or generation. Components are off by default.

| Component | Isolated contrast | Offline gate before paid tests | Decision rule |
|---|---|---|---|
| A: schema/parser contract | Same raw response through old/new parser first; later, same context and answer renderer with schema-only prompt changes | Existing duplicate-Q replay is A0: one recovery, all valid controls unchanged. New normalization may not drop ordinary facts, conditions, boundaries or unknown fields. Test negative controls and schema/prompt consistency. | Retain A0 narrow engineering fix. Do not infer overall answer-quality gain. A1 prompt changes need independent fresh pairs. |
| B: minimum dependency bundles | Same selected source IDs/ranking, same total context-byte ceiling; exact-source boundary/header/qualifier representation only | Verify source offsets, complete dependency representation and deterministic reconstruction. No inferred OCR column relations, whole-parent expansion, or sentence-only output requirement. | Reject bundles that lose original evidence or exceed the budget. Structural proxies alone do not authorize adoption. |
| C: packing/original-query protection | Same candidate pool and span extraction, original branch retention off/on under identical source/byte budgets | Record original/candidate/selected provenance. Diagnose candidate-available versus context-retained support separately; cached reference IDs are evaluation-only proxies. | Advance only if coverage gains do not come from budget growth or loss of required original facets. |
| D: keyword expansion | Fixed selected packing strategy, identical generator; expansion off/on | Reuse frozen hypotheses where available; no answer/reference-conditioned keywords. Measure additional candidates and displaced original evidence. | Test only after packing; reject gains that trade away required evidence. |

Per trial record: hypothesis; code/config/model/data hashes; origin and exposure; component switches; every scheduled output and failure; mechanically valid fraction; all-denominator rubric passes; separately source-reviewed required content/qualifiers; p50/p95 with identical warm retrieval + generation + validation scope (grading/queue excluded); input/output tokens and conservative cost; both-corpus and regression deltas; retain/reject/uncertain decision. A zero-call replay has no fresh generation latency or fresh judge score, and those cells must be marked not measured.

Reserve **$35** for broader confirmation and **$10** for failure/uncertainty headroom; exploratory paid ceiling is **$41.10317855**, additionally constrained by per-dispatch ledger worst-case reservations. The prior full paired run cost $14.162858 for planning only, not a guarantee. Start with small paired edges; stop on errors or budget threat. Do not run an entire factorial blindly. Only combine independently promising components; test the combination and leave one component out before broader confirmation. If the required matrix cannot fit, report the untested cells rather than shrinking scope silently. Keep the established baseline unless gains survive both corpora and general regressions; uncertain tradeoffs stay opt-in.

## Trial log

### A0 — completed independent parser ablation

- Hypothesis: repeated identical valid clause selections are an idempotence mismatch, not new facts.
- Change: local commit `917a7a6`; original candidate `1443e35`; context/prompt/model fixed. All 645 primary pairs plus 20 corrected regression pairs replayed; source files hash-checked unchanged.
- Outcome: candidate primary validity 585→586/645; baseline 636 unchanged; corrected regression validity 20 baseline/19 candidate unchanged. All 1,260 previously valid answers unchanged. Source review supports the single recovered answer; no new judge passes or latency measured. Cost $0.
- Decision: retain narrow parser fix; reject any extrapolation to overall model improvement. Broad numeric acceptance remains unsafe because source-visible counterexamples include wrong scale, missing cited continuation and category confusion.

### B0/C0 — pre-implementation cached evidence diagnostic

Completed at zero API cost. Frozen development selection uses 12 hash-ranked IDs from each of four corpus/origin groups (48 primary), plus all 20 fixed regressions; 597 primary cases remain confirmation-only. No development selection used outcome scores. On 24 NH development cases, current packing retains 27/63 supplied reference IDs; both unprotected RRF and all-original selection retain 28/63, with complete-reference coverage unchanged at 5/22 cases having references. Original-source retention is 68/96, 65/96 and 96/96 respectively. All 24 GM development cases have empty reference-source maps, so this proxy cannot evaluate GM quality. This is an evaluation-data limitation, not zero evidence quality.

Decision: uncertain. Neither one extra reference ID nor original-branch retention establishes semantic benefit. C1 receives an isolated fresh test on the common roster, with source and UTF-8 context-byte ceilings enforced by fallback; no silent truncation. B remains a structural feasibility audit because reference IDs do not identify missing headers/qualifiers. D waits for packing outcomes. No combination is yet justified.

### A1/C1 — frozen fresh development contrasts

Three arms on all 68 development cases: incumbent baseline, A1 schema reminder only, and C1 all-original branch protection only. A1 appends a compact contract summary, drawing GM limits from existing validator constants; it does not change parsers, handle formats, facts or retrieval. This is a prompt-contract test, not complete schema unification. C1 preserves the original branch only when it fits the baseline source and context-byte ceilings; otherwise it falls back unchanged. All arms use the existing baseline renderer. Twenty regression fixtures have identical C1/baseline prompts and are stochastic repeated-generation controls.

Maximum 204 fresh outputs and 204 fresh rubric reviews (408 calls), no cached outputs as controls. Exact prepared jobs, configuration, evaluation-only references and code hashes are frozen privately. The runner protects the $41.10317855 exploratory ceiling with three-request worst-case headroom; shared cumulative ledger remains authoritative. Outcomes pending; no promotion.


### B1 — boundary-envelope feasibility, completed offline

On the frozen 48 primary development cases, 72 newly introduced lexical windows have recorded source offsets. All 72 reconstruct exactly after approved redaction. Minimal enclosing line/sentence envelopes leave 69 unchanged; three require 216 additional UTF-8 bytes in total. The enlargement preserves the original excerpt but cannot fit the unchanged per-case byte ceiling without removing other text. Rejected under this strict control, at $0 and zero generation calls. This is not a semantic table/qualifier completeness test; original-branch windows are outside this diagnostic and no OCR column relationships were inferred. A meaningful dependency-bundle arm requires source-adjudicated dependencies and an explicit displacement control. No B improvement is claimed.

A1/C1 preflight: 204 jobs prepared without failures; A1 contexts and user evidence messages exactly match baseline. C1 changes 14 GM and 11 NH contexts; 7 GM and 8 NH cases fall back because original evidence exceeds the baseline ceiling. Other cases, including all 20 regression fixtures, remain unchanged controls. Recorded legacy retrieval trace fields describe the starting baseline; each job's actual `context` is authoritative for the C1 selected source set. The new component trace identifies fallback explicitly.


### Interruption, accounting and approval blocker

The execution tool session disappeared after 85 complete outputs/reviews. Read-only process inspection found no remaining experiment or provider worker. The precise OS termination cause was not logged. Two generations and one review had started without saved responses; one interrupted-review job retains its already saved generation. All three open reservations were settled at their conservative $2.0064 bounds, and journal terminals/failure rows were appended without overwriting prior evidence. There were no retry dispatches. A continuation request for only the 116 never-started jobs was rejected by automatic approval review, which stated that trusted parent clearance for paid calls was missing. No workaround or further paid call was attempted.

The incomplete run is closed: **204 scheduled outputs; 85 completed with reviews, 3 interrupted, 116 not started**. Its 174 dispatched calls cost a conservative **$6.884576**, including **$6.0192** unknown-use charges. Cumulative **$120.78139745/$200**, remaining **$79.21860255**, zero open reservations, no active paid process. Frozen hashes verified: 284. Partial arm counts/latencies are retained privately as observed-subset diagnostics only; they are not comparable final quality estimates. No combination, leave-one-out run, or confirmation was launched. Resumption requires the clearance requested by automatic review and reconciliation against this exact closed state.

### Evaluation reliability — observed identical-answer discordance

Among seven observed arm-pairs with identical canonical answers, two have opposite pass/fail judgments **and identical review prompt hashes**: GM349 baseline/A1 and NH R063 baseline/C1. These pairs are dependent and selected from an incomplete trial, so 2/7 is not a population error-rate estimate. They nevertheless prove that these score flips cannot be attributed to the component's delivered answer. Preserve both raw judgments; do not relabel one arm to manufacture improvement.

Source-visible assistant review of all five observed discordant pairs (four questions) found: the two identical-answer judge disagreements; introduction-question completeness thresholds that inconsistently demand optional book details; and one C1 answer adding a cited but off-target gallstone-origin statement to a question about Bian Que's discovery. Exact citations do not establish relevance or required-facet coverage. This is assistant review, not human gold; no replacement aggregate score is assigned. Required core facets versus optional background need calibration before promotion.

### D0 — frozen offline expansion control

Expansion-off reproduces every frozen development baseline context exactly. Source-vocabulary expansion changes candidate admission only; the original question still chooses source spans, and RRF weights/protected-prefix packing stay fixed. Across 24 NH cases it creates 10 raw context changes, with 2 byte-budget fallbacks and 8 effective changes. Across 24 GM cases it creates 16 raw changes, with 9 fallbacks and 7 effective changes. Source guesses never enter the answer as evidence. Cost $0; two focused tests pass. No quality, latency or causal benefit is established, and no D paid test was launched because packing remains unresolved and paid continuation is blocked.

### Retain / reject / uncertain checkpoint

- Retain A0's narrowly verified duplicate-clause parser repair; it preserves all previously valid outputs and recovers one source-reviewed answer offline.
- Reject B1 enlargement under the strict no-loss/no-growth control; 69 no-ops and three over-budget envelopes are not a useful new arm.
- A1 and C1 remain uncertain and opt-in: the trial is incomplete, with direct evidence of judge inconsistency. Keep the incumbent baseline.
- D0 remains an offline candidate, not an improvement. No components are combined and no default is changed.

External-use scope: the reader-context and original-query provenance literature informs these diagnostics; the isolated implementations are independently written. Instructor motivates evaluating an explicit contract reminder, not installation or adoption of its retry engine. No upstream source, model, dataset or prompt was copied. Docling, CiteCheck, VeriCite, XGrammar and facet-coverage work remain considered evaluation/representation directions, not reproduced systems.


## Offline adjudication after continuation denial

No new provider calls. All 85 saved reviewed outputs were inventoried; raw result, response, job and reference hashes are unchanged. They cover 53 of 68 cases, with only **four complete three-arm cases**. Common reviewed pairs are **15 A1/baseline** (3 GM, 6 NH, 6 regressions) and **11 C1/baseline** (2 GM, 8 NH, 1 regression). This is inadequate coverage for overall quality, latency or cross-corpus adoption claims. The 116 unstarted jobs and three interrupted outputs remain separate.

### Two identical-answer disagreements: source adjudication

**GM349:** local corpus page `D01:6:01` explicitly supplies application, operator initial review and science/innovation-center review. The chosen `D01:7:01` starts at step four. Page6 was available at rank11 in the recorded original-query lexical candidate branch but was not selected. Both identical answers correctly state subsidy commencement but omit the earlier steps despite the question asking the pre-signing process. Assistant adjudication: both materially incomplete; the baseline full-pass verdict is not supported. This establishes a candidate-to-context evidence loss and a shared answer defect, not an A1 treatment effect. Source is local OCR, not independently verified human gold.

**NH R063:** both identical answers cite source support for the book identity, volume count, author/date, organization, classification and entry columns. Under the existing rubric to answer the actual broad introduction request, assistant adjudication considers both adequate concise introductions. Drug count, gallstone-formula count and a world-memory listing are optional background unless requested; demanding all reference details is not a calibrated completeness rule. The world-memory sentence appears in the full supplied reference source but is beyond the truncated reader excerpt. This explains a reference-versus-reader asymmetry without excusing unsupported claims. Neither raw score is overwritten, and this assistant adjudication is not promoted to human gold.

### Mechanisms and preliminary regressions

| Observed comparison | What the saved evidence establishes | What it does not establish |
|---|---|---|
| A1, all15 paired cases | Identical contexts; all baseline and A1 outputs mechanically valid. Two raw pass losses include one identical-answer judge flip and one uncertain introduction-facet threshold. | No observed paired validity gain; no robust quality loss or gain. |
| C1, 11 paired cases | Four change source content, one changes only source order, six have identical prompts. | Treating all eleven as effective packing changes would be misleading. |
| NH-LIVE-26 | An off-target but cited extra claim appears in the C1-labeled output. C1 actually fell back, leaving the prompt identical. | The content defect cannot be attributed to changed packing. |
| NH-LIVE-07 | All-original protection drops `MD-028-0004`, containing one compared formula's composition/indications. The answer covers fewer requested comparison details; both judges fail. | A binary pass metric alone does not capture the evidence-content regression. Original-branch protection does not guarantee required-facet preservation. |
| NH-HOP-02 | Same source texts, different order under C1. All three arms substitute a book-level formula count for the requested dataset count and fail to supply two names. | Format reminders or reordering cannot create missing collection-level aggregation evidence. The supplied exact reference count is not independently accepted as gold here. |
| NH-SKILL-008 | C1 emits a mixed boundary/text object and is rejected. Raw output is retained. | No silent text deletion or clinical inference is justified; a schema failure is separate from semantic/source safety review. |
| NH R071 | Core book source remains, secondary records and answer emphasis change. | A reliable completeness regression is not established without agreed required facets. |

The next useful representation hypothesis is to preserve a selected procedure's preceding structural steps when available in the candidate pool, with explicit byte/displacement controls. GM349 is a motivating example, not a per-question rule or validation set. No such change has been implemented. For evaluation, define question-required core facets separately from optional reference background before examining confirmation outcomes; keep exact-answer/prompt consistency checks as an audit. No additional judge call or automatic regrade was made.

**Current decision:** baseline retained; A0 remains the only narrowly supported retained repair. A1/C1 efficacy is unresolved, B1 remains rejected under its strict budget control, D0 is offline-only. Paid continuation remains blocked after two automatic-review denials; no workaround attempted. Spend remains **$120.78139745**, remaining **$79.21860255**, zero open reservations. Private supporting artifacts: `offline-paired-audit.json`, `offline-source-adjudication.json`, `offline-source-page6.json`.


## Authorized continuation completed — October 14, 2026

Direct user instruction authorized the116unstarted jobs within the existing $200 cumulative cap. The same frozen run resumed; all88 prior outcome rows remain byte-identical, including the three interrupted failures and their conservative charges. **All116 resumed jobs completed with fresh generations and reviews, without new execution failures or retries.** The full scheduled scope now has204outcomes:201completed with reviews,3preserved interruptions,0unstarted. Total406dispatches (232new), with284scope hashes verified and zero open reservations. The earlier denials/incomplete reports remain historical evidence.

### All-denominator results

Every scheduled case remains in the denominator; interrupted or undelivered outputs do not pass. These are exposed development cases, not human gold or a fresh unseen test. Primary48cases and20fixed-context regressions stay separate.

| Population / metric | Baseline | A1 schema reminder | C1 original-query protection |
|---|---:|---:|---:|
| GM passes /24 |17|15|17|
| NH passes /24 |11|11|8|
| Primary passes /48 |28|26|25|
| Primary mechanically valid /48 |47|47|47|
| Regression passes /20 |20|18|18|
| Regression mechanically valid /20 |20|18|19|
| All68 passes (descriptive only) |48|44|43|
| All68 mechanically valid |67|65|66|

The baseline's missing primary output is an interrupted generation; A1 and C1 each have one mechanically invalid primary output. In regressions, A1 has one interrupted generation and one schema-invalid answer; C1 has one interrupted review of a valid generation and one schema-invalid answer. No historical failure was replaced. The primary differences therefore do not establish a validity benefit for either component.

| Population / observed warm p50, p95 seconds | Baseline | A1 | C1 |
|---|---:|---:|---:|
| GM |3.778,4.476|4.120,4.894|3.871,5.468|
| NH |4.454,5.268|4.450,5.054|4.343,5.035|
| Fixed-context regressions |3.887,4.877|3.928,5.065|4.026,5.066|

Latency is warm retrieval/prompt +generation+validation component sum, excluding grading, queue and cold setup. It uses observed generations only: NH baseline n23 and regression A1 n19; other cells have the scheduled population size. Unknown interrupted generation latency is not imputed. C1's interrupted review retains a measured generation. Concurrent, interrupted/resumed phases are disclosed; these are not cold serial SLA estimates or convincing small-sample latency improvements.

### Reliability, source review and decisions

There are65complete three-arm reviewed cases and66reviewed baseline pairs per component. C1's66pairs comprise24source-content changes,4order-only changes and38identical-prompt controls. Across all arms,17pairs have identical canonical answers; two have opposite judgments with identical review prompts (GM349 and NH R063). This dependent audit is not a population error-rate estimate. Earlier source adjudications still apply; raw judge scores are unchanged.

The sole GM C1 pass gain, GM120, replaces abstention with a supported introduction, but its used source IDs were already present in the baseline context. A1's interface-response gain at NH N026 is locally useful but not a general schema effect. Near-equivalent NH N173 answers and personal-use-boundary cases expose further threshold inconsistency. Actual mechanical failures include A1's shortened unsupported source title, A1's non-exact uncited boundary text, and C1's missing boundary evidence field. The C1 regression fixture uses the identical baseline prompt, so its failure is not caused by changed packing. NH-LIVE-07's dropped useful comparison source remains a concrete evidence-content drawback. No medical gold or clinical advice is inferred from historical excerpts.

**Decisions:** reject A1 and C1 as default replacements under this tested configuration. Neither improves primary passes, neither preserves general regression performance, and C1 trades a local GM gain for NH losses. This is not a universal rejection of schema validation or evidence protection. Keep the incumbent baseline and the independently verified narrow A0 parser repair. B1 remains rejected under its strict no-growth control; D0 remains offline-only. No independently promising pair of components was established, so no combination, leave-one-out trial or broader paid confirmation was launched. The597-case confirmation partition remains unscored by these new components.

### Cost and closure

The116-job continuation costs **$1.199642** conservatively. Whole A1/C1 stage: **$8.084218**, including the unchanged **$6.0192** for three unknown-use interrupted calls. By arm, generation+review conservative costs are baseline$2.682298, A1$2.718962 and C1$2.682958; each includes one$2.0064unknown-use charge. These are budget ceilings, not an invoice or FX calculation.

**Cumulative $121.98103945/$200; remaining $78.01896055; zero open reservations and no active paid run.** No push, upload or deployment. Private files include completed-costs.json, completed-reliability-audit.json, completed-source-review.json, summary.json and the updated four-column report. Original results and historical partial checkpoints remain preserved.

## Mechanism-level interpretation and next offline refinement

This section clarifies the completed result; it does not authorize or launch more paid work.

### Exact paired denominators

Each baseline/component contrast schedules **68paired cases:24GM+24NH+20fixed-context regressions**. All-denominator passes count every scheduled case, including interrupted outcomes. Both generations/reviews are available for **66pairs per contrast:24GM+23NH+19regressions**. Both delivered answers are mechanically valid for **64pairs per contrast:24GM+22NH+18regressions**. Across three arms there are65complete reviewed triplets. These populations must not be substituted for one another.

| Contrast | All68 paired wins / losses | Both-reviewed66 paired wins / losses | GM / NH / regression all-scheduled wins-losses |
|---|---:|---:|---|
| A1 vs baseline |2 /6|2 /5|0-2 /2-2 /0-2|
| C1 vs baseline |3 /8|3 /7|1-1 /2-5 /0-2|

These are raw valid-and-rubric outcomes, not source-adjudicated effects. The difference between scheduled and reviewed pairs includes an interrupted regression in each component. The baseline also has an interrupted NH generation. No interruption is imputed as a semantic error, silently excluded, or replaced.

### What A1 actually tests

A1 holds retrieval, source order/text, renderer, model and settings fixed and appends an explicit contract reminder. All66reviewed pairs are prompt-only changes. It therefore isolates this **particular reminder**, not a unified schema/decoder architecture: legacy instructions remain, server-side constrained decoding is not enabled, and no automatic repair or retry is used. Extra prompt length is part of the treatment.

Its two observed mechanical failures are a shortened source title unsupported by the declared alias rules (NH-LIVE-07) and non-exact uncited boundary text (REG-FAQ-04). The reminder does not resolve either constraint. The useful interface boundary at N026 is an answer-level observation, while N173's near-equivalent answers reveal grader-threshold sensitivity. GM349's identical-answer score flip is not an A1 effect. Thus the tested reminder is not promoted; the broader mechanism of a genuinely shared schema/prompt/parser contract remains promising for offline consistency checks and content-preserving normalization. Do not infer that schema validation itself failed.

### What C1 actually tests

C1 is a bundled **packing policy**: all-original branch retention under unchanged source-count and context-byte ceilings, with fallback. Across66reviewed pairs,24change source content,4change source order only, and38have identical prompts. By corpus: GM14content+2order+8identical; NH10content+2order+11identical; regressions19identical. It does not separately isolate the effects of removing lexical additions, changing source order and changing available evidence. The byte/source ceilings are shared upper bounds, not exact equal-length contexts. Earlier descriptions of fixed span extraction mean the extraction algorithm is unchanged, not that selecting another source leaves the effective evidence unchanged.

GM120 shows a useful supported answer replacing abstention, but its cited evidence was already in baseline context; reduced distraction or stochastic answer use is plausible, not proven. NH-LIVE-07 loses a source carrying comparison-relevant composition/indications, showing why protecting every original source can crowd out useful lexical evidence. NH-HOP-02 changes order only and still lacks collection-level aggregation evidence. NH-LIVE-26, NH-SKILL-090 and the regression fixtures use identical prompts: their differing outputs cannot be attributed to an effective packing change. The policy is not promoted, while branch provenance and required-facet protection remain useful mechanisms for refinement.

### Judge scores versus source judgments

The source review supplies no replacement aggregate pass count. Its firm conclusions include: both GM349 answers omit requested early workflow steps available on the preceding candidate page; the identical NH R063 introductions are supported for a concise general introduction under the current actual-question rubric; NH-LIVE-07 loses a relevant comparison source; and the four malformed outputs fail the unchanged declared contracts. Source appropriateness and broad-introduction/personal-use completeness remain separate judgments. These are assistant adjudications of selected cases and local OCR, not independent human gold. Raw scores stay immutable, including the two identical-answer/identical-review-prompt disagreements among17identical-answer pairs.

### Next useful zero-call experiment: B2 dependency-aware swaps

Use the same48primary development questions and frozen candidate pools. First annotate source-only structural dependency spans (procedure predecessors/continuations, row+header+unit, claim+condition/cap) and exact offsets; keep those annotations evaluation-only, separate from the generic selector. GM349 motivates predecessor preservation but must not become a case-ID rule. Do not inspect the597confirmation cases to tune this rule.

Compare three cached representations: (1) current packing; (2) a generic dependency bundle that swaps out redundant/lower-priority evidence within the same source/UTF-8 byte ceilings, with explicit displacement provenance; (3) a diagnostic bundle with relaxed bytes to distinguish genuine budget constraints from selection defects, reported as an unequal-budget upper-bound diagnostic rather than a fair performance gain. Freeze one proposed rule before measuring it. Evaluate required dependency retention, original relevant-facet loss, exact source provenance, OCR uncertainty, bytes, and no-op/fallback rates separately by corpus. No model calls or claim of downstream answer improvement. Reject inferred table relations and candidates that merely gain by dropping another required facet.

If B2 improves source-reviewed dependency coverage without material losses, preserve that mechanism for a later authorized fresh answer test. D0 can then be compared expansion-off/on with packing and original-query span extraction frozen. D0 already changes8/24NH and7/24GM contexts after byte fallbacks, but candidate novelty is not required-evidence gain. Measure newly retained dependencies and displaced useful originals before any new paid expansion experiment. This sequence refines useful mechanisms rather than dismissing dependency bundles or expansion from A1/C1's scores.

### Paid authority remaining

The direct user instruction was to **resume the116unstarted paid ablation jobs within the existing$200cumulative limit**. That action is fully fulfilled. It does not authorize additional calls merely because$78.01896055remains. No new paid job, retry of the three interrupted outcomes, D test, combination, leave-one-out matrix or confirmation run is initiated by this summary request. Further paid scope requires a new direct instruction or otherwise recognized authorization. The shared ledger is closed with zero open reservations; no push, upload or deployment.
