# Acceptance coverage reconciliation — 2026-10-13

The earlier 301-test run used `unittest discover -s tests`, including untracked
legacy tests. The later 155-test run explicitly selected only the sixteen tracked
modules. That was an unjustified reduction in acceptance scope; tracking status
is not a reason to omit applicable local tests. No existing tests were deleted,
skipped or changed to make the count smaller.

The omitted modules contain 161 tests: `test_bounded_query_embeddings` 32,
`test_independent_acceptance` 3, `test_offline_answer_contract` 22,
`test_optimization` 50, and `test_trust` 54. They remain untracked and unchanged.
The 16 included modules contain 155 tests: axis_review 4, batch_renewal 17,
continuous_optimization 6, definitions 7, experiment_budget 1, guardrails 3,
lexical 4, newdomain 77, newdomain_recovery 8, optimization_contract 4,
predicate 2, record_boundary 4, research_criteria 5, research_methods 7,
review_compaction 2, scope_preparation 4 (each prefixed `test_`).

Since the 301-test checkpoint, 15 tests were added: definitions 7, lexical 4,
predicate 2 and batch renewal 2. Thus **301 + 15 = 316 = 155 + 161**.
At HEAD `ea05b71`, full discovery passed **316/316 normally and under `-O`**,
with zero skips. Initial restricted runs produced one failure and 45 errors due
to prohibited repository `.cache` fixture writes; retained logs distinguish these
from passing runs with approved local fixture access. No tests were modified.

The typed-condition compiler subsequently adds 14 synthetic provenance/operator/
false-join tests. Full discovery now passes **330/330 in both modes**, zero skips.
Commands (bytecode writing disabled):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests .venv/bin/python -m unittest discover -s tests -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests .venv/bin/python -O -m unittest discover -s tests -q
```

These are local offline tests, including legacy private-fixture dependencies and
mocked transport. They do not establish semantic correctness or live service
availability. Full discovery remains the applicable acceptance scope going forward.

Final checkpoint: two modal-comparator tests, three report-prose/source-key tests
and two whole-batch request-allowance tests bring 330 to **337**. Full discovery
passes 337 normally and 337 under `-O`, zero skips. A new test-placement import
error was corrected; its failed log is retained separately. No suite was excluded.
