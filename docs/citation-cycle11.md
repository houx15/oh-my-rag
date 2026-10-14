# Cycle11: bounded citation completion and its limits

C1 remains the default. Cycle10's opt-in deterministic protocol repair is preserved; it repaired the three final Cycle9 delivery failures (34/37 → 37/37 mechanical validity) without changing previously valid answers. Neither the retrieval experiments nor the citation completion helper is promoted. This cycle spends nothing on providers and does not claim a new adequacy score.

## Research question and frozen comparison

Can a bounded extension of an existing exact quotation repair claim-to-citation alignment while preserving the complete answer? This isolates evidence selection from retrieval, generation and answer deletion. It addresses the exact-span/coverage problem discussed in the [literature matrix](research-cycle3.md), with evaluation validity treated separately from judge agreement. These are independently engineered deterministic heuristics, not reproductions of S2G-RAG, CompSelect or any downloaded repository. No new paper, code dependency or external implementation was used, and there is no novelty claim.

`newdomain/citation_completion.py` compares the unchanged quote, one punctuation-delimited neighbor on either side, and completion of the current sentence plus an immediately trailing parenthetical attribution. Both treatments require a unique exact quote occurrence, preserve source IDs and every original quoted character, prohibit additions containing a section heading, and reject expansions over 400 characters. They return an audit trace with `semantic_support_verified: false`. They do not certify entailment, resolve missing source metadata, regenerate an answer, or silently alter a false claim. The helper is opt-in and is not wired into the default answering path.

The implementation and five focused tests were hashed before evaluation and before the separate reviewer returned eight synthetic fixtures. No implementation tuning followed. Prior Cycle8 frozen follow-ons, Cycle9 F01–F06 and Cycle10 independently authored checks retain their frozen hashes. Synthetic fixtures are entirely fictitious. They are source-selection unit cases, not fresh end-to-end retrieval questions.

## Mechanical replay and resources

| Cohort (output records, not unique questions) | Records per arm | Neighbor changed | Sentence changed | Valid in each arm |
|---|---:|---:|---:|---:|
| Original Cycle9 outputs after protocol replay | 328 | 212 | 16 | 320 |
| Cycle10 original factorial outputs | 68 | 50 | 14 | 66 |
| Frozen Cycle10 outputs | 24 | 14 | 0 | 24 |
| Frozen Cycle9 outputs | 12 | 5 | 2 | 12 |
| Total, descriptive replay only | 432 | 281 | 32 | 422 |

There are 1,296 comparison rows, plus 24 rows for the eight new synthetic fixtures. Repeated cases and cached/shared answers are not independent observations. All answer texts and citation source IDs are preserved. All expanded quotes remain exact source substrings, and no prior mechanically valid output becomes invalid. The original raw judge scores are displayed only as historical metadata; they were neither revised nor reused as evidence that completion improves adequacy.

Neighbor expansion changes 602 citations and adds 25,046 quotation characters; sentence completion changes 87 citations and adds 7,168. Local replay processing p50/p95/max is 0.074/0.129/0.311 ms for neighbor and 0.014/0.057/0.137 ms for sentence. This single offline measurement includes deepcopy, assertions and mechanical validation for changed Niuhuang outputs; it excludes retrieval, provider/network latency and downstream consumption of longer quotes. It is not an end-to-end latency improvement. Baseline is essentially pass-through (p95 0.002 ms).

All 473 offline regression tests and five focused Python-O tests pass using imported unittest discovery. Zero new paid requests, retries or reservations were made. The last settled ledger remains **$82.03191625/$200**, a conservative accounting ceiling, not a currency-converted invoice. No push, upload or deployment occurred.

## Review design and scope

The separate read-only assistant received 53 deduplicated outputs in shuffled order with arm labels, original scores and lineage removed. Coverage comprises eight distinct original questions (two known citation issues plus deterministic hash sampling), all 19 affected prior frozen output groups, and all eight new synthetic cases. Identical question/source/answer combinations were deduplicated across arms. Selection is diagnostic, not a random estimate of accuracy across the corpus.

The reviewer shares the model family, has prior related context, and authored the eight fixtures. Label masking reduces treatment-label bias but does not create human gold or independent human adjudication. Quotation length can make an arm inferable. Claims must be supported by the selected quote, not merely somewhere in the larger supplied source.

## Clear negative cases and bounded positives

On the fresh synthetic cases, sentence completion includes the missing trailing work title in CA01; the neighbor baseline is blocked by the section boundary. Neighbor expansion restores the preceding speaker on a separate line in CA02, which sentence completion misses. Neither approach fixes repeated-anchor ambiguity (CA04), an unsupported author/date claim (CA06), or distant attribution (CA08). In CA03 and CA05, sentence completion exposes a misquotation/wrong-entity problem but leaves the false fixed claim false. This is useful diagnostic context, not an answer repair. Already sufficient CA07 remains unchanged.

The next section records the masked reviewer findings before the promotion decision. No new judge call is needed to prove substring exactness or to repeat existing judge-validity limitations. Future work should use offset-bearing citations with explicit claim/entity/speaker links and a small human-adjudicated set, rather than expanding more text or optimizing the exposed frozen cases.

## Masked findings and decision

After decoding labels, the two clearest synthetic gains split between methods: sentence completion fixes CA01's missing work title; neighbor expansion fixes CA02's missing speaker. Neighbor also improves answer-wide speaker/classification linkage in the prior S02 outputs, adds the opposing 吴普 position to R039's local disagreement citation, and finishes F05's truncated underground-parking phrase. S02 still needs multiple quotations to establish the speaker link. These are narrow source-verified improvements, not a measured net adequacy gain.

Neither method repairs S05's missing 《圣惠方》 citation, N390's local “味苦气凉”/“味苦气平” mismatch, R090's unsupported negative relationship, or F06's incorrect floors5–8 vacancy assertion. The latter remains contradicted by the floor8 tenant list despite unchanged passing historical judge scores. Expansions often include unrelated historical administration, theory, attribution fragments or property details. Sentence completion changes none of the 24 prior Cycle10 frozen outputs, and does not outperform the simple baseline across the reviewed problem types.

**Decision: stop this line of tuning at a documented plateau.** Preserve the opt-in helper as a reproducible negative experiment, retain Cycle10 protocol repair, and leave C1/default retrieval unchanged. There are local attribution gains but no demonstrated net source-verified quality advantage after usefulness is considered. This small diagnostic review does not prove the absence of a benefit on every unseen case; it does justify declining promotion and further low-value paid trials now. No answer was removed to improve validity.

A useful next experiment requires an offset-bearing citation representation and explicit claim/speaker/entity alignment, with separately authored questions and human adjudication frozen before evaluation. That is a new hypothesis and evaluation investment, not an implemented gain or a promised improvement. The current source/section adapter remains experimental. The best established result is the deterministic delivery repair; the strongest source-level finding remains the documented missing speaker marker in the local transcription and its versioned public-source amendment.

## Artifacts and reproducibility

Private experiment directory: `citation-cycle11-20261014` under the local task workspace. It contains code/fixture freezes, the offline evaluator and review-selection script, all432×3 replay rows, eight×three synthetic rows, shuffled masked review inputs, private label lineage, a condensed record covering all53 review IDs, cohort statistics, verification and the four-column HTML report. The replay requires the preserved Cycle9/10 local artifacts and existing environment; it is not a standalone corpus benchmark. No corpus or artifact was uploaded.

For the helper tests in the repository, use `python -m unittest discover -s tests -p test_citation_completion.py` (also with `-O`). Full regression uses `python -m unittest discover -s tests`. No additional dependencies or provider requests are needed. All historical reference tables in the unified local report are preserved byte-for-byte; HTML checks are structural, not browser visual QA.
