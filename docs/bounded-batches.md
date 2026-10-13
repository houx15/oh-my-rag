# Audited bounded experiment batches

A manifest's persisted 24-hour runner deadline is an administrative execution
limit, not evidence that provider credentials or user permission expired. An
explicitly recorded continuation under the user's sustained optimization scope
can run a new bounded batch without rewriting that deadline or resetting spend.
Ordinary contexts still refuse dispatch after their original deadline.

`newdomain.batch` and `scripts/optimization_batch.py` implement this opt-in path.
Each activation appends a hash-chained renewal event to the existing canonical
final ledger and writes an immutable private receipt. The event preserves the
original deadline, pins the manifest, denylist, questions and generation jobs,
and records the reason and existing reservation-prefix hash. Existing spending,
reservations, manifest fingerprints, historical ledger checks, stage allowances,
provider route and privacy screening remain in force.

Each batch permits at most 48 `deepseek-flash` generation calls and 24
`deepseek-v4-pro` paired review calls, no retries, one hour, and $4 total charged
plus outstanding reserved cost. Admission is checked under the canonical ledger
lock; open and conservatively settled calls count. The original cumulative $100
cap and the existing experiment allocation remain enforced as well. Provider
workers receive the same batch receipt and their wall timeout is shortened to
stay inside its execution window. Full-context conservative reservations remain
unchanged; a reviewer call temporarily reserves about $2.77, explaining why the
batch cap exceeds its roughly $0.24 expected settled cost.

Review jobs bind once to their predetermined private path, model and question IDs.
Changed bindings or frozen inputs fail closed. Successful result/journal records
remain reusable by explicit resume; failed or ambiguous outcomes are not retried.
No new source/provider permission is inferred from a receipt.

Closure appends a separate hash-chained record with the completed reservation
hash, call count, charge and reason. It requires all batch reservations settled,
blocks further dispatch through that batch, and permits a separately recorded
next batch without waiting out an otherwise unused hour. All past grants, reasons,
closures, original deadlines and spending records remain intact. This is an
auditable local history, not a defense against an administrator rewriting all
trusted files and hashes.

Fifteen synthetic tests cover original-history preservation, receipt/ledger
agreement, changed inputs/deadlines/history, missing bindings, model/retry/expiry
rejection, open and conservative charges, persisted 72-call limits, concurrent
admission, premature closure, append-only next-batch lineage, removed accounting
tags, and worker timeout bounds. Full normal and optimized Python suites passed
299 tests before activation. No external code or provider was added; C1 answer
and retrieval defaults are unchanged.
