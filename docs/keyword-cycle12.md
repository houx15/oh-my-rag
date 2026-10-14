# Cycle12: free keyword hypotheses with source vocabulary

The user requested a fast-model keyword stage for false abstentions, with no phonetic-similarity requirement. This implementation preserves original-query retrieval, merges additional lexical views, and grounds generation in source text. Hypotheses are never answer evidence. No default is changed before results and source review justify it.

## What was already tried

The earlier `query_plan.py` experiment used DeepSeek Flash, at most two uncertain queries and names from the initial top20 candidate pool. It explicitly prohibited guessing missing context. On36 exposed cases, raw adequacy moved10→11/24 in Niuhuang and9→10/12 in Guangming; the extra call and mixed regressions prevented promotion. `query_variants.py` separately implements the explicit 派的→pad rule for display requests. Neither is evidence that unrestricted corpus-informed Qwen hypotheses have been tested. This experiment avoids duplicating those exact conditions.

## Implementation and provenance

`newdomain/keyword_hypotheses.py` constructs vocabulary solely from source text using existing tokenization, book-title extraction and Latin terms. It retains a source record ID for every term. The bank covers1507 Niuhuang and1174 Guangming records. Per question it presents up to90 common and lexically related terms. The original conversational question is passed unchanged. The model may propose up to3 arbitrary semantic/abbreviation/colloquial hypotheses of60characters, including terms outside the bank. No phonetic gate, reference answer or expected source ID enters the inference API.

Neither indexed source snapshot contains literal pad or LivePad. Those are included separately as user-supplied interface vocabulary, not falsely described as extracted source terms or proof that navigation is possible. The model is instructed to treat every proposed query as a hypothesis, never a confirmed answer. Generation receives the original question and selected exact source excerpts, not the generated hypotheses as facts.

Original selected contexts and source-only original-query lexical results remain candidate views. Weighted reciprocal-rank fusion reranks their union with hypothesis views; half the strongest original contexts remain protected. Context count stays4 for Niuhuang and8 for Guangming. Existing selected windows remain unchanged; newly selected records receive an exact source substring of at most900characters selected by lexical coverage. No embedding call, trained reranker, new package or imported external code is added. Malformed/truncated keyword JSON falls back to the original-only plan; transport failures stop rather than retry.

The generator/canonicalizer is the same current Cycle10 baseline adapter in all arms: Cycle8 facet handling with opt-in protocol normalization, and the restored-source Guangming pipeline. This is not an exact replay of historical C1 or of `presentation/records.json`. The latter is a historical mixed record set and is not used as a current-route comparator. All60 answers are newly generated on the same Bailian model, including cases with identical prompts; stochastic differences on identical prompts cannot be attributed to retrieval.

## Frozen pilot and evaluation

Ten original questions per domain cover confirmed historical misses, conditional speech hypotheses, noisy positive controls, clean controls, missing dialogue, unsupported current price and source restoration. The separate read-only reviewer verified source passages before paid inference. Its proposed GM419 control was absent from the original318-question roster and was excluded before outputs; clean GM169 replaced it. All earlier frozen synthetic checks remain unchanged. These20 questions are exposed diagnostic data, not a random sample or untouched population benchmark.

The current baseline already includes the previously absent source evidence for several historical cases. R004 has 定精神, N353 has 甘，凉, R021 has 除邪逐鬼, GM125 has relevant district-development facts and GM174 has the restored 超千项 sentence. They therefore test answer use and preservation, not new source recall. N417's historical valuation, GM064's broad achievements inventory and conditional R065's 夜啼 evidence remain absent from all three selected contexts. Exact-string diagnostics are only passage-presence checks, not entailment scores.

Reference answers and reference-source snapshots are stored in a separate evaluation-only file and supplied only to the unchanged downstream judge. Judge agreement is not human gold. The final masked review separately checks actual source support, appropriate uncertainty, omitted content and citation correctness, with labels and scores withheld. All raw judge outcomes remain intact; unsupported unconditional corrections are not counted as successful rescue merely because a source mentions the guessed entity.

## Provider, costs and latency

The approved small/fast route is `qwen3.8-flash`, verified against Alibaba's [model documentation](https://help.aliyun.com/zh/model-studio/qwen3-8-flash) on2026-10-14. Beijing input/output list rates are CNY0.8/2.7 per million tokens. Each actual response's model name is checked. Generation and judging retain existing `deepseek-v4.1-flash`. No model-size parameter count is inferred from the Flash name.

The20 keyword calls completed with no retries or open reservations, conservative cost0.0111792, carrying cumulative spending from82.03191625 to82.04309545. This numericUSD reservation convention is a conservative ceiling, not a foreign-exchange calculation or invoice. The answer stage retires that admission and carries its complete ledger chain into a new allocation of at most120 requests. The global200USD cap is unchanged; stages do not spend concurrently.

Latency records include vocabulary preparation, original retrieval, the keyword API call, fusion/window selection, generation and canonicalization. Because ledger stages run serially, reported pipeline latency is a measured critical-path component sum across stages, not one contiguous live request. Idle time between stages and offline grading are excluded. Existing original-query embeddings are cached; cold corpus/index initialization and uncached embedding latency are not measured. No cached generation is used. All479 offline tests passed before paid inference, including six new adversarial/provenance tests.

The platform's NumPy matrix multiplication emitted runtime warnings during preparation. An independent offline check found every cached vector and every pilot similarity finite; equivalent einsum scores differ by at most1.12e-15. No numerical implementation was changed during the frozen experiment.


## Completed outcome and decision — 2026-10-14

| Arm (20questions each) | Raw judge pass | Unscored | Masked assistant source-usefulness | Valid | Pipeline-sum p50 / p95 |
|---|---:|---:|---:|---:|---|
| Baseline |8|0|9|19|4.568 /6.140s|
| Vocabulary |10|1|9|19|4.561 /7.020s|
| Small model |6|0|12|20|7.912 /11.299s|

Source review covers all60 outputs, arm labels and raw scores masked; reviewer had
related project context and is same-model-family, not human gold. Vocabulary gains
GM125 but losesGM128. Small-model gainsR034 (speaker attribution),R095 (missing
antecedent clarification),GM125 (substantive grounded district information), with
no observed source-usefulness losses on these20. This is not a population claim.
Raw small-model lossesR034/GM068 conflict with source review. Raw vocabulary gains
R021/GM420 are not useful source-grounded rescues. Preserve both measurements.

All arms failN417 historical valuation, R065 ambiguous液体, GM064 policy scope,
N001 unconditional牛磺→牛黄 and GM119 missing technology referent. All preserve
GM174 platform/subset distinction and appropriateN288 current-price abstention.
R021 retrieves除邪逐鬼 but repeats rather than explains it. Minimal conditional
clarification and useful substantive answers are not identical quality; binary
assistant ratings compress this distinction and require human calibration.

Candidate diagnosis: N417 targetMD-011-0004 appears at rank10 in original and
hypothesis views; GM064 D30:1:01 appears at ranks2/3 in two hypothesis views;
GM420 targetD31:2:01 appears at rank4 in one view. Fusion drops these. R065 target
never enters any view. Removing the duplicated/double-weighted original vote in
a postfreeze offline diagnostic changes32/40 selections and recovers some targets,
not demonstrated answer quality. Cycle13 freezes equal fusion and query-token
coverage over the existing20 keyword outputs before further paid answers. No
additional keyword calls or targeted source-ID overrides are planned.

20Qwen +119DeepSeek calls settled: incremental conservative0.8737252;
cumulative82.90564145/200,0open reservations,0retries,0unknown usage. One GM068
vocabulary judge preflight was rejected before dispatch. Its answer remains in
masked source review; raw score remains unavailable, not a failure or an observed
loss. The existing outbound screen was not weakened. All frozen scope hashes and
previous frozen test files verified.479offline tests and6focused optimized tests
passed. No push, deployment or upload.

The result is promising source-usefulness on exposed cases at material added
latency, not justification for promotion. C1 remains default. Cycle12 is independent
engineering with no external code/prompt/weights or new paper reproduction.
[Canonical narrative and next steps](technical-report.md).
