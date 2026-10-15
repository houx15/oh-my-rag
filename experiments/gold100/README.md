# Frozen Gold100 candidate algorithms

These opt-in algorithms preserve the private experiment implementations. `baseline.py`
is the immutable Simple-RAG-v1 implementation; `r01.py`, `r02.py` `r03.py` and `r04.py` expose
`Index(records).search(question)`, `messages(question, chunks)` and
`validate(raw_response, chunks)`. Only package imports differ from private snapshots;
`provenance.json` records both hashes. No credentials, questions, reference answers,
raw corpus, generation outputs or billing ledgers are included.

- R01: baseline retrieval plus source-span citation handles and a completeness prompt.
- R02: baseline seeds plus short full records, adjacent pages and policy dependencies.
- R03: baseline seeds plus original catalog relationships and recomputable record counts.
  Derived snippets retain all input source IDs and hashes. Missing catalog fields remain
  missing; counts describe dataset records, not distinct recipes or complete ancient books.

- R04: baseline retrieval and user payload unchanged; task-focused system prompt and short direct quotes.

The common source validator remains unchanged. R01 resolves handles to exact quotations
before that check; R03 aggregates are explicitly derived retrieval material whose source
membership must also be audited. Semantic correctness is reviewed separately.

Synthetic tests, with no network or paid requests:

```sh
.venv/bin/python -m unittest tests.test_gold100_candidates tests.test_gold100_prompt
```

Private frozen runners remain the authority for paid dispatch, journal deduplication,
budget reservation and all-100 evaluation. This package alone never calls an API.
See [campaign results](../../docs/gold100-optimization-results.md) for measured outcomes,
limitations and the current round's status. Do not infer results for a prepared round.

R05 preparation: `r05.py` implements exact-source dense/BM25 reciprocal-rank fusion.
It requires caller-supplied source and query vectors; it never calls an API or reads
reference answers. `embedding_transport.py` is a bounded, single-attempt transport;
private runners additionally enforce the frozen manifest, stage spending cap and
persistent dispatch journal. The user directly authorized the specific endpoint and frozen data scope.
Index construction finished with428successful calls and zero retries.
R05 generation is running; no complete-round quality result is claimed yet.
`embedding_artifact.py` refuses incomplete journals, changed response hashes or
unclosed ledgers and preserves each fresh query embedding latency.

Run all current offline tests:

```sh
.venv/bin/python -m unittest tests.test_gold100_candidates tests.test_gold100_prompt tests.test_gold100_embeddings tests.test_gold100_hybrid tests.test_gold100_embedding_artifact
```
