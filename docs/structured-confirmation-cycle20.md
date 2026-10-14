# Cycle20: structured-candidate confirmation fails the promotion gate

Keep C1 default and stop further paid optimization of this candidate. On16 mixed-origin questions excluded from Cycles16–19 (8 live/real-user,5 pre-existing GM simulated,3 pre-existing NH evaluation), source-reviewed factual completion rises5→7, but one ordinary successful case becomes undeliverable, valid delivery falls16→14, and source-conditional adequacy falls8→7. Two of three completion gains are borderline coverage judgments. Accepting those baseline answers as sufficient yields7→7, with one remaining win and one ordinary-case loss. This sensitivity is diagnostic, not a change to frozen primary ratings.

**Provenance limit:** all16 questions had historical generations. This is a fresh
32-output comparison on an exposed mixed-origin subset, not an original-only or
truly unseen confirmation, and it does not establish full-benchmark performance.
See the [cumulative denominator history](technical-report.md#current-evidence-and-denominator-summary--2026-10-14).

## Frozen candidate and selection

No changes to candidate code b80bf48, prompts,300-character unit/900-character rendered limits, attachment validation or deterministic rendering. Cycle19 primary/secondary dimensions and scoring rules are copied verbatim. Case-specific source obligations were frozen before calls. No candidate fixes after offline audit or outputs, no replacement of difficult cases, no new keyword calls, and no reference rewriting. A uniform original lexical-fusion preparation supplies identical evidence to both arms; unlike the diagnostic Cycle19 cohort, no percase Qwen/facet route is selected.

The16cases comprise eight per corpus: two ordinary historical successes, two condition questions, two attribution/entity-ownership questions and two ambiguity/intent cases. Fixed SHA256 order selects within question-feature strata; historical raw success is used only for ordinary controls. Question-only routing rules were corrected before context inspection because broad “that”/“says” patterns misclassified ordinary questions; no candidate answers or source suitability informed those corrections. Final rules and input hashes are retained. NH ambiguity includes one missing referent and one UI request; GM ambiguity covers UI/intent boundaries. Attribution includes identity and ownership, not exclusively nested quotation. No claim that this is a representative random sample.

Exact/normalized-close Cycle16–19 questions and explicit overlapping semantic families are excluded. All16already have historical generation records in the earlier665case full rerun. N265 also appeared in Cycle14 and GM124 in Cycles14/15; the exposure audit lists earlier input memberships, including broad Cycle7. Eight questions originate in live/real-user data, five are pre-existing simulated GM questions and three pre-existing NH evalset questions. These are **held out from this iteration, not truly unseen**; these pre-existing questions were not newly synthesized for this test.

### Exact selected questions

| Case | Stratum | Supplied question |
|---|---|---|
| NH:N049 | ordinary_success | 嗯，讲黄帝内经。 |
| NH:N468 | ordinary_success | 从来没有听说伏羲是做这个，是这个有什么医学的认知吗？我我我没这么不觉得呀，伏羲是做这个的吗？ |
| NH:N389 | conditions | 嗯，那个牛黄吃多了会伤身体吗？ |
| NH:NH-NB-04 | conditions | 安宫牛黄丸能和降压药一起吃吗？ |
| NH:NH-HOP-04 | attribution | 王怀隐所著的《太平圣惠方》里，这套资料收了多少条与牛黄相关的记录？举两条方名。 |
| NH:N411 | attribution | 呃，我想看看扁鹊，你给我介绍一下扁鹊。 |
| NH:N265 | ambiguity | 它是不是很贵啊？ |
| NH:NH-LIVE-06 | ambiguity | 打开《本草纲目》，我想看硫黄。 |
| GM:GM-388 | ordinary_success | 优合集创的医疗传感器里，体外检测和心电监测算同一类吗？ |
| GM:GM-177 | ordinary_success | 小光，小光。 给我讲一下表面超快动力学。 实验站。 |
| GM:GM-201 | conditions | 在光明做新型显示材料，关键材料项目和补薄弱环节的项目，投资补贴有什么区别？ |
| GM:GM-330 | conditions | 企业出钱发榜解决技术难题，光明的揭榜挂帅资助按出榜的钱算，还是按研发团队投入算？ |
| GM:GM-410 | attribution | 做光伏器件时，HTM空穴传输材料能解决哪些问题？是哪家机构的成果？ |
| GM:GM-235 | attribution | 在光明零租孵化器里换办公室，要向谁申请？换的面积不一样会更麻烦吗？ |
| GM:GM-124 | ambiguity | 呃，我们还有一页的科技成果是安全连锁保护系统给我们切换到那一页开始讲解。 |
| GM:GM-120 | ambiguity | 好的。 嗯，咱们今天现场还有一些。 呃，人想要了解一下光明区，他们第一次来，你给我们。呃，切换到光明，光明区的介绍那个 Pad 给我们讲解一下吧。 |

## Offline audit and execution limits

The audit retained real capability losses: GM388's direct IVD-versus-ECG chart is longer than the frozen selectable-unit limit, so no directly answering unit remains; GM120 loses optional infrastructure-overview breadth. NH-HOP04 lacks the requested dataset-record count and two formula names in selected evidence; the book-level near400formulas is a different quantity. All11overlong exclusions were audited and retained.32matched-input and743single-unit rendering checks pass. The unchanged candidate previously passed527normal and14optimized tests; these are prior code-regression results, not newly claimed Cycle20 test executions.

Offline retrieval reconstruction changed NH-HOP04 from MD-023-0004 to MD-023-0002 across process restarts. Cause is unestablished; diagnostic inputs are saved. To isolate generation with genuinely matched evidence, the already-frozen contexts are served to both arms. No evidence was refreshed after the audit. Thus timing below is **frozen-context catalog/prompt + generation + validation/rendering only**, excluding retrieval/cold setup/grading. This does not establish live retrieval stability or end-to-end performance. The candidate and selection remained frozen; the runtime serving change and initial freeze revision are recorded before calls.

A first launcher failed before dispatch because private select.py shadowed Python's standard-library select. Isolated Python launch resolved it without source changes. This is a pre-dispatch harness failure, not a provider retry. Subsequent64dispatches completed without timeouts or retries.233inherited/new scope hashes verified;73citations across30valid outputs exact,26structured citations visibly rendered. Exactness is not semantic entailment.

## Matched results

| Measure,16 scheduled outputs per arm | Baseline | Structured |
|---|---:|---:|
| Raw judge passes | 12 | 5 |
| Factual complete / partial / none-or-N/A | 5 / 6 / 5 | 7 / 3 / 6 |
| Source-conditional adequate / partial / inadequate | 8 / 7 / 1 | 7 / 7 / 2 |
| Factual complete, NH / GM | 3 / 2 | 3 / 4 |
| Valid delivery under respective declared contract | 16 | 14 |
| Outputs with unsupported assertions | 3 | 0 |
| Clear / usable with noise / obstructive | 14 / 2 / 0 | 5 / 9 / 2 |
| Answer-only p50 / p95 seconds | 4.102 / 6.082 | 4.048 / 6.372 |
| Generation input / output tokens | 50,880 / 1,724 | 61,811 / 755 |
| Delivered character median / maximum | 94 / 179 | 180.5 / 413 (14valid) |

At n16p95=max; one draw per arm cannot support stable tail latency conclusions. Inputtokens+21.5%, outputtokens−56.2%; fewer generated IDs do not guarantee lower latency. Candidate text roughly doubles in median length and becomes noisier. Do not compare this answer-only timing directly to earlier whole-pipeline timings.

### Paired successes, failures and unchanged gaps

- **GM330 partial→complete:** genuine preservation of offered benefit eligibility: district leading enterprise, reviewed major project, issuer actual contribution,20% and500万元 cap remain together. This does not avoid the numeric claim. Repeated OCR-damaged clauses add noise.
- **GM410 partial→complete:** derivative-specific HTM benefits and named institution are retained together. The baseline already has correct institution and broad mechanisms; completeness of subtype detail is borderline, not a new entity-disambiguation rescue.
- **GM177 partial→complete:** catalyst-design purpose becomes visible in delivered quotation; baseline already covers techniques and institute. This is a borderline completeness gain, not newly retrieved evidence.
- **GM388 complete→undelivered:** ordinary classification control regresses. Required chart has no selectable unit; model emits S1/U1 although U1belongsS2 and concerns an incubator operator. Both representation coverage and raw relevance fail; fixing the ID alone would not answer the question.
- **GM120 undelivered candidate:** S7/U7 mismatches U7's S1. Baseline is a valid but inadequate blanket refusal; no semantic rescue claimed for either.
- **GM201 partial→partial:** baseline loses eligibility in prose. Candidate keeps rates/caps and built-operating conditions but detaches the second policy category from its number. Syntactic attachments do not establish the requested comparison.
- **GM235 complete→complete:** both preserve operator responsibility and area-change approval branches. A retained success, not a repair.
- **GM124 partial→partial:** candidate avoids baseline's unsupported page-switching assurance but quotes unresolved “我院” under a generic source label. This trades one limitation for another, not an attribution rescue.
- **N049,N468,N411 complete→complete:** ordinary historical introductions/identity retained. N468 source-labelled tradition must not be read as independently verified modern history.
- **N265 adequate clarification→generic absence:** no invented referent, but candidate fails to ask what “它” means. Intent regression, not a factual-completion change.
- **N389,NH-NB04 adequate boundary→partial boundary:** generic absence removes the baseline's specific explanation of missing modern overdose/coadministration evidence. Neither is a factual medical answer; human calibration is needed on helpfulness versus minimal safety.
- **NH-HOP04 partial→partial:** both omit dataset count/formula names. Candidate repeats near400book-level formulas without clearly marking the mismatch; safe/source-exact contextual text cannot complete the requested aggregation.
- **NH-LIVE06 partial boundary→partial boundary:** neither provides absent sulfur content or explicitly addresses UI limitation; no fabricated opening action.

The frozen confirmation gate required noninferior completion overall/bycorpus, no new material ordinary-control loss, no worse delivery/unsupported claims, and required-content condition/ownership successes. The ordinary-control and delivery clauses fail regardless of borderline scoring. Lower unsupported-assertion count does not compensate for lost delivery and helpfulness.

## Judge disagreement and human calibration

All32raw grades and masked source judgments remain unchanged. The raw judge rejects N049 for missing authorship/formation though the frozen introductory obligation permits its directly supported book nature/components/content. It rejects N468 despite a concise attributed documentary tradition answering the medical association. Those are coverage-standard disagreements, not automatic proof the source assistant is right. Conversely, both methods recognize genuine GM388 failure; raw graders miss several eligibility/identity subtleties credited in broad answers.

Primary source ratings give5→7complete. A posthoc sensitivity that treats baseline GM177's introductory purpose omission and GM410's subtype detail omission as acceptable gives7→7; remaining complete win GM330 balances loss GM388. Do not replace primary ratings or report a new tuned score. Human reviewers should calibrate these exact obligations, whether volunteered subsidy terms require complete eligibility, whether source-labelled historical quotations adequately answer doubt, and whether generic absence is sufficiently helpful. Same-model, prior-exposed source review is not human gold, even with arm/score masking.

## Cost and stopping decision

64calls, no provider failure/retry/unscored result. Increment0.456762; cumulative conservative ledger**92.72868945/200USD**, zero open reservations, no active allocation. Conservative tariff accounting is not actual billed USD/FX. All32exact questions, delivered/raw answers, scores, contexts and timings are retained in the private four-column report. No push, upload, deployment or default change. No new external paper/repository implementation adopted; existing acknowledgments retain actual-use scope.

Stop this candidate rather than tune another reminder or cap on this cohort. The concrete bottlenecks are representation coverage for long tables, cross-sentence condition/entity relationships, specific clarification/absence behavior, missing aggregation evidence, and retrieval reproducibility. A future approach needs evidence-preserving semantic records and human-calibrated evaluation before another performance claim; that is an unimplemented engineering hypothesis, not asserted novelty. This confirmation does not justify promotion.
