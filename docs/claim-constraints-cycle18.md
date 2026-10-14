# Cycle18: source-span reminders do not preserve claim constraints reliably

Do not adopt this candidate. Exact source-span reminders fail to repair the two diagnosed condition omissions, introduce an attribution regression, and break a valid clarification control. The count-scope improvement also occurs with guide-only, so it does not establish an annotation benefit. No further paid cycle is allocated for this candidate; C1 remains default.

## Diagnosis and isolated change

Cycle17 exposed a gap between exact citation and correct claim: the flexible-computing statement loses its equal-workload premise, policy summaries lose domain restrictions, and historical attribution can drift from a quoted speaker to a book's compiler. Inspection of `citation_contract_v3.py` and the canonical output path confirms that validators enforce root schema, boundary forms, citation addresses and quotes—not semantic preservation of all conditions or speaker bindings. Delivery does not repair factual prose. Cycles14/15 had already tested generic and task-focused reminders without sufficient gains.

The new independently written `newdomain/claim_constraints.py` is opt-in. It adds deterministic exact spans from selected evidence containing condition cues, parenthetical historical attribution, or a bounded speaker neighborhood. Spans include offsets, original evidence headers/context openings, and explicit `semantic_binding_verified=false`; no inferred facts, new retrieval, posthoc prose rewriting or stricter rejection gate. It omits overlong spans rather than cutting conditions. Same selected evidence remains available in full to every arm.

An offline source audit caught ordinary parentheses falsely treated as speakers and policy excerpts detached from their domain. The former rule was narrowed; original headers were retained; speaker neighborhoods were explicitly marked unverified. All53 remaining spans and headers passed exact-presence checks. Residual risks were frozen: damaged R034 speaker transitions, nested policy scopes, and irrelevant reminders. These warnings correctly predict failure modes; exact offsets do not establish semantic ownership.

## Frozen comparison

Eight actual original questions, four per corpus, with three arms: baseline; concise general preservation guide; same guide plus exact-span cards. Four targets: N417/R034 attribution, GM068/GM064 condition/scope. Four controls: N288 current price, R095 missing referent, GM169 count, GM126 bounded candidate-name introduction. Retrieval snapshots are frozen from completed Cycles16/17; choice of snapshot is experimental cohort setup, not a case-specific inference rule. All24 prompt/context reconstructions verified, same evidence across arms, same approved `deepseek-v4.1-flash` generator/judge, same output schema and validators, shuffled seed1814. No keyword calls.

Rubric frozen before outputs separates source-conditional adequacy, factual completion, available target facts, preserved conditions, preserved attribution, unsupported claims, and valid delivery. N417 now has selected valuation evidence, so abstaining cannot be factual completion. Current price and missing antecedent appropriately remain non-factual tasks. All24 outputs masked for assistant source review, same model family/prior project exposure—not human gold. This is an eight-question development pilot, not24 independent questions or a fresh unseen-original confirmation. Its completion labels must not be substituted into Cycle16's12/20 metric.

| Measure,8 scheduled answers per arm | Baseline | Guide only | Guide + spans |
|---|---:|---:|---:|
| Raw judge passes | 4 | 4 | 4 |
| Factual complete / partial / none-or-N/A | 1 / 4 / 3 | 2 / 3 / 3 | 2 / 3 / 3 |
| Source-conditional adequate / partial / inadequate | 2 / 4 / 2 | 2 / 2 / 4 | 2 / 2 / 4 |
| Outputs with unsupported claim | 2 | 3 | 3 |
| Mechanically valid delivery | 8 | 7 | 7 |
| Warm p50 / p95 seconds | 3.464 / 5.323 | 4.402 / 5.888 | 4.453 / 7.465 |
| Staged p50 / p95 seconds | 3.464 / 7.310 | 4.402 / 7.185 | 4.736 / 7.465 |
| Total generation input tokens | 24,634 | 25,890 | 32,670 |
| Total generation output tokens | 759 | 853 | 844 |

Warm timing is actual contiguous original warm retrieval, saved-hypothesis selection, annotation/prompt construction, generation and validation. Cold initialization, uncached embeddings and judging excluded. Staged totals add the historical Qwen call only to N417, equally in all three arms; no live whole-path keyword claim. p95 at n=8 is the maximum, a descriptive sample statistic. Preparation p50 is13.6/28.9/23.7ms. Span-arm generation input rises32.6% versus baseline; extra bytes and latency did not buy reliable preservation. Full experiment, including judges, costs0.35785 in the conservative ledger convention, not an invoice/FX claim.

## Actual answers and causal interpretation

| Case | Baseline → guide → spans | Interpretation |
|---|---|---|
| N417, 陶弘景牛黄价值 | complete → complete → complete | All three use explicit弘景 attribution and a speaker-containing quote. Guide additionally names《本草纲目》transmission. Baseline already resolves the target in this fresh run; no new rescue. |
| R034, 李时珍评价 | partial → partial with unsupported attribution → partial with unsupported attribution | Baseline uses marked龙胆 opinion and avoids the damaged牛病 passage; optional王氏方 provenance remains weak. Both interventions attribute牛病 to李时珍 without sufficient binding. |
| GM068, 实验室成果 | partial → partial → partial | All emit40%+ without the equal-business-scale premise in prose. Guide preserves comparator; spans do not. The full condition appearing in quotations is insufficient. |
| GM064, 区科研成果 | partial → partial → partial | All give supported carbon result then broaden20%/500万元 beyond new-materials policy. Header preservation did not repair generated policy scope. No unavailable flexible-computing result required here. |
| GM169, 材料类成果数量 | partial → complete → complete |44 is correct throughout; guide and spans explicitly state the source collection/381-row scope. Shared non-target gain, not a unique card benefit. |
| GM126, uncertain park name/introduction | none → none → none | Blanket no-evidence response despite candidate park-management content; no focused clarification or conditional introduction. |
| N288, 当前每斤报价 | no factual answer → same → same | Safe absence preserved; all remain generic rather than identifying seller/current-price information. No recoverable price fact exists in selection. |
| R095, “它有什么影响？” | valid clarification → invalid → invalid | Guide emits uncited free clarification; spans mix free text with a clarify boundary. Both violate the existing exclusive typed-boundary protocol. Appropriate raw intent is not valid delivery. |

Concrete GM068 span-arm prose: “柔性计算是光明实验室与华为云联合研发的新一代算力服务架构，可节省40%+算力资源…” The selected source, reminder and quote contain “相比业界主流的弹性计算架构…在承载等量业务规模前提下”; the model still drops them from prose. This is generation use, not a newly missing retrieval.

Concrete R034 span-arm prose: “李时珍认为牛黄因牛病在心及肝胆之间凝结成黄，故还能治心及肝胆之病。” The neighborhood is not verified as his speech; the audit warned about the damaged transition. A nearby exact passage cannot certify personal attribution.

R095 span-arm raw output combines an uncited explanatory sentence with `{"boundary":"clarify"}`. The contract requires clarification to be the only object, so it is rejected. No response was rewritten into a plausible success. Across22valid outputs,43 raw factual sentences remain unchanged through delivery;48/48 cited strings are exact, not proof of entailment.

## Decision and next boundary

Frozen gate: at least two material target repairs across both domains, no new material control failure, and distinguishable benefit over guide-only. Observed target rescues: zero; R095 control regresses; no unique card gain. Gate fails. Preserve the negative result and stop this reminder candidate. Do not promote the guide because its count-scope gain coexists with attribution and delivery regressions.

The next defensible design question is whether to move from free prose plus reminders to explicit claim/condition/attribution fields with deterministic rendering and source-binding checks. That would change answer style and requires an offline design plus validation of damaged/ambiguous source ownership before another paid comparison. It is not implemented, scheduled, or assumed solved here. Additional prompt repetition or extra retrieved text is not justified by this result. Human/source-OCR calibration and unseen-original confirmation remain outstanding.

## Reproducibility and closure

513 offline tests and8 focused optimized-Python tests pass;202 scope hashes verified.48terminal dispatches,24outcomes,24masked reviews; no transport failures or retries, two protocol failures retained. All ledgers closed with zero open reservations. Increment0.35785; cumulative91.92431945/200. Code commits8f25199 and2c9dd38; private plan, frozen rubric, offline audit, jobs, runtime, raw generations/results, per-case source reviews, decision.json and settlement preserve the experiment. report.html/cases.csv include all24 outputs. Prior report tables remain unchanged.

No new upstream paper/code/prompt/assets used or installed; existing README academic acknowledgments retain their actual conceptual-use scope. This is an engineering ablation of known constraint-preservation and attribution problems, not a novelty claim. No push, deployment, upload, new provider, or additional code writer.
