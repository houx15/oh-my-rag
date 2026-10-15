# Frozen Gold100 candidate algorithms

These opt-in algorithms preserve the private experiment implementations. `baseline.py`
is the immutable Simple-RAG-v1 implementation; `r01.py`, `r02.py` and `r03.py` expose
`Index(records).search(question)`, `messages(question, chunks)` and
`validate(raw_response, chunks)`. Only package imports differ from private snapshots;
`provenance.json` records both hashes. No credentials, questions, reference answers,
raw corpus, generation outputs or billing ledgers are included.

- R01: baseline retrieval plus source-span citation handles and a completeness prompt.
- R02: baseline seeds plus short full records, adjacent pages and policy dependencies.
- R03: baseline seeds plus original catalog relationships and recomputable record counts.
  Derived snippets retain all input source IDs and hashes. Missing catalog fields remain
  missing; counts describe dataset records, not distinct recipes or complete ancient books.

The common source validator remains unchanged. R01 resolves handles to exact quotations
before that check; R03 aggregates are explicitly derived retrieval material whose source
membership must also be audited. Semantic correctness is reviewed separately.

Synthetic tests, with no network or paid requests:

```sh
.venv/bin/python -m unittest tests.test_gold100_candidates
```

Private frozen runners remain the authority for paid dispatch, journal deduplication,
budget reservation and all-100 evaluation. This package alone never calls an API.
See [campaign results](../../docs/gold100-optimization-results.md) for measured outcomes,
limitations and the current round's status. Do not infer results for a prepared round.
