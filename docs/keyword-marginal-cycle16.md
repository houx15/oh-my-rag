# Cycle16: what keyword diffusion contributes after the missing control

The matched original-query lexical control removes the apparent aggregate benefit of always-on Qwen expansion on these20 exposed original questions. This is not a rejection of query expansion as a research direction: useful candidate records are present but dropped, and the next isolated experiment tests that specific selection defect.

## Design and validity

Ten original questions per corpus, three fresh generation/judge arms, unchanged original questions, source budgets4/8, generator/validator/judge, and frozen Cycle12 dictionary/Qwen hypotheses. The lexical-only control adds original-query lexical-top20 to original retrieval with the identical2/2/1 weighted RRF, constant60, protection and windows. Both expanded arms' contexts and messages exactly match Cycle12. Cycle12's earlier baseline lacked this lexical control, so its apparent keyword gain was confounded with added lexical retrieval/fusion. No new keyword calls in Cycle16.

All60 scheduled outcomes retained:59 returned generations and one vocabulary generation ReadTimeout, conservatively charged without retry. Four other responses fail the answer protocol. Source rubric and fallback policy frozen before outputs. All60 masked source judgments completed by an assistant with prior project context, not a human or independent model-family gold standard. Complete/partial/insufficient is distinct from binary useful. These labels are source-conditional: a bounded abstention can be complete despite a known corpus retrieval gap, as N417 shows. They are not end-to-end factual completion; retain targeted-facet recovery separately. Raw model judges and OCR references remain fallible; partial can still be binary-fail.

| Arm | Raw judge pass/20 | Source useful/20 | Complete / partial / insufficient | Valid/20 | Warm p50 / p95 s | Staged full p50 / p95 s |
|---|---:|---:|---:|---:|---:|---:|
| Original lexical + same fusion | 9 | 12 | 8 / 5 / 7 | 19 | 4.961 / 7.212 | 4.961 / 7.212 |
| Dictionary hypotheses | 8, one unscored | 11 | 5 / 7 / 8 | 18 | 4.785 / 8.260 | 4.785 / 8.260 |
| Frozen Qwen hypotheses | 9 | 12 | 6 / 8 / 6 | 18 | 4.989 / 10.287 | 8.229 / 12.841 |

Warm timing is contiguous original retrieval, saved-hypothesis selection, prompt, answer and validation. Staged full timing adds the earlier keyword-call delay only for Qwen; it is not a live end-to-end keyword measurement. Cold initialization, uncached embeddings and judging excluded. Vocabulary timing denominator19 returned responses; other arms20. These small-sample p95 values are descriptive. The one unknown end-to-end failed request is not assigned a fabricated duration or silently treated as fast.

## Marginal evidence and actual failures

Among38 newly selected Qwen case-record pairs relative to the older baseline,37 were already in the original lexical candidate pool,24 in the dictionary pool, and none outside their union. The524 Qwen-only candidate pairs yield one selected passage and zero cited passages. The selected exception GM119/D17:10:01 is irrelevant financial/rent policy; it does not resolve “这项技术”. This counts case-record pairs, not unique documents.

| Original question / issue | Actual hypotheses or source trace | Causal interpretation |
|---|---|---|
| N417: “的传承。陶弘景有没有评价过这个牛黄的价值，说它很贵呢？” | Qwen: “陶弘景 牛黄 价值”; “陶弘景 评价 牛黄”; “牛黄 传承 陶弘景”. MD-011-0004 already original lexical rank10; Qwen-only MD-038-0008 ranks17/19 and contains 弘景曰 valuation. Both dropped. | Candidate selection is a testable bottleneck; presence in pool is not answer evidence. |
| GM064: “介绍一下光明区的科研成果。” | Qwen: “光明区 科研成果”; “深圳光明 科技成果 介绍”; “光明科学城 重大成果”. Qwen-only D30:1:01 ranks2/3 but is dropped. | District inventory is optional overview, not a new technical achievement. Fresh Qwen output contains supported carbon-rating text but malformed root schema; source usefulness falls1→0 for protocol, not hallucination. |
| GM068, 光明实验室成果 | D36:241:01 flexible computing is original position5 but dropped; dynamic-baseline result remains. | Binary usefulness stays1 while complete→partial: genuine evidence-detail loss hidden by pass rate. |
| R065, ambiguous 小儿液体 | Generated “治小儿液体”, “小儿 方子”, “小儿 汤剂” miss bank terms for pediatric night crying. | Vocabulary/entity ambiguity remains unresolved; do not assert a speech correction from a guess. |
| GM001, 咽试纸 | “咽试纸 科技成果 简介”; “咽拭子 检测技术 成果”; “试纸 生物科技 研发”. Vocabulary lacks the full 比色快检试纸 entity. | Entity-preserving source vocabulary is a separate untested hypothesis; 咽拭子 can drift. |
| GM126, 流创园/留创园 | Qwen returns bounded candidate-name explanation and limited supported park content. | One borderline partial gain; no confirmed name equivalence or latest-development claim. |

Earlier R034 attribution, R095 referent clarification and GM125 partial district facts must not be called novel recall merely because usefulness changed. The current matched-control result has one binary gain GM126 and one loss GM064; GM068 also loses completeness. No population/significance claim follows20 exposed questions, single stochastic calls, and assistant adjudication.

## Frozen selective-fallback counterfactual

Trigger: valid lexical-only answer contains only exact preregistered no-evidence sentence(s), optionally the disclaimer, all uncited. No case IDs, gold, judge outcomes or known rescues used. Four triggers: GM125, GM126, GM128, N288. Counterfactual useful12→13/20, complete remains8; partial5→7, insufficient7→5. Only GM126 gains binary usefulness, and only as a partial/borderline response. N288's justified price abstention causes unnecessary work. GM125 remains failed at22.49s; GM128 remains incomplete.

Staged p50/p95 is5.431/14.174s. Triggered paths add baseline answer + historical keyword call + expanded answer. This is replay of a frozen decision rule, not a live fallback execution or evidence of population efficiency. No retrospective gate retuning.

## Resources and reproducibility

119 terminal dispatches, zero retries/open reservations. Increment2.85524; cumulative89.31009345/200 in the conservative ledger convention, including one unknown-usage timeout reservation. This is not an invoice/FX claim.151/151 delivered citations are exact substrings across55valid outputs; exactness does not establish entailment.

Private artifacts: answer-jobs.json, preparation.py, source-rubric.json, fallback-policy.json, transport-reconciliation.json, answers/settlement.json, source-reviewed-results.json, paired-source-review.json, fallback-counterfactual.json and citation-audit.json. Source snapshots and raw outputs remain private/outside Git. Code: newdomain/keyword_control.py, newdomain/keyword_marginals.py, scripts/run_keyword_control.py, scripts/audit_keyword_marginals.py. Existing paper acknowledgments cover conceptual influences; no external implementation newly copied or installed.

Next: Cycle17 crosses the same three expansion arms with control versus bounded evidence-facet selection on N417, GM064 and GM068:18 fresh answers. Seven prepared contexts change,53/60 unchanged offline. Source audit found no required evidence loss, but distinguishes valuation, optional overview and extra detail. This is development, not fresh confirmation; C1 stays default.
