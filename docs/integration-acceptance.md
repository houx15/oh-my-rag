# Integration acceptance evidence

The published checkpoints are `3d5661c` (runner recovery/reporting integration),
`2522864` (opt-in C3B/numeric diagnostics) and `90e5ff2` (private frozen experiment
orchestration). Remote: `git@github.com:houx15/oh-my-rag.git`. Both original
checkpoints were verified as ancestors of origin/main; GitHub Actions returned
no runs. This is local-test evidence, not a passing CI claim.

| Prior failure | Acceptance evidence | Scope |
|---|---|---|
| C2P/C2R accepted altered saved results | `RunnerRecovery.test_tampered_results_block_all_runners`, `test_missing_result_hash_blocks_all_runners`, `test_model_mismatch_blocks_all_dispatch` call the actual generation entrypoints for B0/C1/C3B/C2P/C2R and both actual judge entrypoints; mock provider call count cannot increase after corruption. | Synthetic process/file recovery tests; no crash-at-every-instruction proof. |
| Partial/in-flight jobs could be discovered after new workers dispatched | `test_unresolved_job_blocks_all_dispatch` inserts an unresolved job and verifies global preflight rejects before new calls. Header binds inputs, code/config; run lock is held across preflight and execution. | Unknown/failed calls are not automatically retried or silently repaired. |
| Judges lacked journals/resume | Actual `judge_live_v2` and `judge_cycle2` run, persist, then resume under `test_completed_resume_calls_nothing_and_preserves_results`; same result bytes, zero additional calls. Results fsync precedes success hash. | Imported unjournaled judge outputs are report-only; legacy reuse is explicitly refused. |
| Locks leaked after malformed journal/header | `test_corrupt_journal_releases_process_lock` and post-failure lock reacquisition in actual-runner tests. `TestJournal.test_concurrent_process_rejected` uses another process. | macOS/Linux fcntl implementation; Windows unsupported. |
| Mock tests were mistaken for real end-to-end testing | Mock transport schema/failure checks remain unit tests. `tests/test_newdomain_recovery.py` separately exercises actual runner entrypoints with a patched network boundary. | Mocks do not prove provider integration. The authorized 8-question live pilot subsequently completed 16 generations, 8 paired-judge calls and 16 pointwise-judge calls without errors. |
| Report provenance was overstated | Historical replay checks 49 source-pack hashes and accepted verdict hashes, records mapping/manifest digests, distinguishes semantic audit acceptance from valid-generation-gated adequacy. | Historical mapping was not pinned in its manifest; that limitation cannot be retroactively repaired. Old results remain exposed diagnostics. New runs pin generation input hashes in judge headers and result hashes in journals. |
| Fresh allowance / reference leakage risk | `tests/test_experiment_budget.py` rejects backward spend and requests whose conservative charge plus open reservations exceed the nested allocation. Generation uses a strict four-key question view; references are separate judge files. | Same-host filesystem separation is logical access control, not a separate OS security principal. No reference fields are sent to inference. |

At completion, **254 local tests passed normally and under `python -O`**
(8.253 / 8.224 seconds). The 358 actual paid API jobs also completed with no
retries or unresolved dispatches; all ten journals and frozen artifacts were
reconciled without new network calls. These real calls cover C1/C3B and both
judges, not every legacy candidate on the provider. Legacy private-data-dependent
tests are local checks; published synthetic suites do not require the corpus.
No GitHub Actions runs were present; this remains local validation evidence.

Unreviewed legacy sources/documents remain untracked and preserved locally.
Publication uses explicit reviewed file lists; private corpora, questions,
references, ledgers, logs and result artifacts are never staged. OpenCode
remains idle; Codex is the sole implementation writer. No deployment.
