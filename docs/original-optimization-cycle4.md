# Original-question continuation and provider interruption (2026-10-13)

The last complete coherent report remains **Guangming223/330 and Niuhuang155/315**.
The later unified candidate is incomplete and must not replace these results.
All corpus questions and fixed rubrics were preserved. No production default,
deployment, upload, GitHub push, new provider or filtered-field restoration occurred.

## Completed experiments

| Change | Scope | Result | Calls | Recorded cost USD |
|---|---|---|---:|---:|
| Catalogue-to-detail bridge, paired replication |4 original questions ×3 repeats ×2 arms|6/12 baseline vs12/12 bridge; two question clusters improve, two remain passed|48|0.05443860|
| Explicit valid citation addresses in prompt |10 prior mechanical failures +20 hash-selected valid controls|9/30→14/30;6 gains,1 loss; invalid10→2|60|0.06192090|

The bridge is an independently written, bounded exact-name source join; count
routing takes precedence. M-RAG is acknowledged as conceptual motivation in
README, not reproduced code. Four repeated question clusters do not establish
population generalization. Citation addresses expose actual zero-based segment
ranges; no post-hoc citation repair, validator weakening or reference leakage was
introduced. Neither pilot is an untouched holdout.

Generation-stage nearest-rank p95 in the small bridge replication was
2.087s baseline and2.195s bridge (+5.2%); n=12 per arm makes this tail estimate
unstable. The citation pilot candidate p95 was2.467s (n=30). These omit upstream
retrieval and judging and do not establish a full-system latency improvement.

The academic failure-to-method mapping and date/license checks remain in
[the research matrix](research-cycle3.md). New work addresses cross-source
evidence coverage, citation-address errors, and layout-aware source extraction.
These are known research problems and local testable adaptations, not novelty
claims. The prior negative global query-planning and exact-book-selector results
remain preserved; neither is included in the candidate.

## Incomplete unified candidate

The frozen665-case scope comprises645 original corpus questions and20 separately
reported fixed-context contract regressions. NH uses focus, typed-v2 and citation
address prompts. GM uses C1 with count precedence, then the bounded bridge.
All generations and primary reviews were intended fresh. Original upstream
retrieval is replayed; no new embeddings or full retrieval rerun occurred.
Latency measures routing through answer validation, excluding frozen upstream
retrieval and judging. It cannot be compared as full end-to-end p95 to old timings.

The provider returnedHTTP402 after321 completed generation/review pairs.
There are324 saved generations,645 successful response receipts,648 dispatched
calls, three failed reviews, zero retries and zero open reservations. The failed
reviews areGM:GM-021, GM:GM-313 andNH:NH-LIVE-03. Another341 cases were not started.
A safe continuation needs341 generations and344 reviews (685 logical calls),
consumes saved generations, never repeats successful work, and preserves all
failed dispatches. Resolve the provider error externally before freezing and
allocating a continuation; do not blindly restart the original runner.
Official error documentation could not be fetched; the account balance was not
inspected and no narrower billing cause is claimed.

This run's ledger totals$2.62928250: usage-settled$0.73896570 plus three unknown-
usage conservative settlements totaling$1.89031680. Cumulative conservative
accounting is$39.77140635/$200; this is not a claim that all charges were billed.
No estimates may be reversed without invoice evidence. The task cap is not the
cause of the stopped run. All17 frozen scope hashes matched at reconciliation.

Private artifacts are under the2026-10-12 task directory:
`coherent-fresh-20261013/{coverage.json,stop-reconciliation.json,reproduction/}`.
Original results, failures, ledger, journal, inputs and source hashes are retained.
The public-facing repository contains no copied corpus or paid output artifacts.

## Source reliability and next method

All40 preselected source-diagnostic annotations (20 per corpus) are complete,
with raw scores unchanged. They are assistant diagnostics, not human adjudication.
They identify source/reference mismatch, incomplete context, ambiguity without
prior dialogue, and historical-text answers requiring scope/safety review.
Local visual inspection confirmed that OCR reading order can lose floor/tenant
row associations. A conservative geometry helper retains unambiguous numeric
floor labels and rejects ambiguous OCR; it is offline only, with no paid efficacy
claim. A three-case layout pilot is prepared but has no allocation or API calls.

Permission to restore/transmit the previously filtered institution values and
platform-total clause remains pending. Those fields were not restored. Missing
conversation context, independent human review and a fresh natural holdout remain
methodological limitations, not evidence that optimization is exhausted.

## Validation

399 offline tests pass under both normal and optimized Python using the existing
repository virtual environment. Initial system-Python/missing-dependency and
sandbox-write failures were preserved and resolved by using the existing venv
and authorized test-cache writes; no package was installed. HTML/CSV structural
QA is repeated separately; browser visual QA remains blocked by file-URL policy.
Only the complete report's results are promoted. Historical regressions remain
separate and preserve the historicalFAQ03 failure.
