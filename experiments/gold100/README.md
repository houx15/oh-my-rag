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
R05 generation and review are complete:54/100semantic passes, mean6811.646ms
including query embeddings. It does not meet the quality/latency target.
`embedding_artifact.py` refuses incomplete journals, changed response hashes or
unclosed ledgers and preserves each fresh query embedding latency.

Run all current offline tests:

```sh
.venv/bin/python -m unittest tests.test_gold100_candidates tests.test_gold100_prompt tests.test_gold100_embeddings tests.test_gold100_hybrid tests.test_gold100_embedding_artifact tests.test_gold100_composed tests.test_gold100_compact tests.test_gold100_ordered
```

R06 is complete:78/100semantic passes versus54baseline;85mechanical and68combined.
It composes hybrid seeds, catalog counts, record/page/policy dependencies and the
R04prompt within6000characters.100unique dispatches produced99answers and1connection
failure, retained as failure with no retry. Actual cached mean is8902.935ms over99;
estimated uncached mean9494.244ms adds prior measured query embedding. Missing
failure latency is not zero. Both quality and latency miss the target. No new
embedding charges; round cost2.879544USD includes2.0064conservative unknown-usage
settlement. All20offline tests pass; private ledgers retain full evidence.

R07 is complete:73/100semantic,97mechanical,70combined; baseline remains54semantic.
All100calls returned, with zero retries; three unknown evidence handles fail validation.
Actual cached mean4781.143ms; estimated uncached mean5372.197ms adds prior query
embedding timing. Quality misses80, so this is not a promoted result. Round cost
1.005198USD; campaign spent7.62784625of200USD, history separately retained.
Retrieval text/order
match R06for all100cases. Compact answer/evidence pairs resolve to exact original
quotes before the common validator. Personal-use queries withhold dosage/procedure
clauses before span splitting;7of100cases activate this source-only filter.
All exposed handles verified;24offline tests pass. Reused-vector timing remains
explicitly estimated for uncached comparison; no new embedding charges.

R08 is complete:77/100semantic,100mechanical,77combined; baseline54semantic.
All100calls returned with zero retries/truncations/open reservations. Cached mean
4681.465ms, estimated uncached5272.520ms; quality remains below80.
Cost0.988956USD; campaign8.61680225USD with191.38319775USD remaining.
All R06
source spans remain; small catalog groups, source-era metadata and same-document
lexical matches supplement them. Physical page order is restored inside documents.
Personal-use omissions are explicit; exact handles and the common validator remain.
100/100 requests rebuild exactly with verified source intervals and member hashes.
All27offline tests pass. Context cap8500characters and serialized message cap29500bytes;
only supplemental spans are removed to meet the unchanged30000byte transport screen.
Initial offline preparation hit that screen before any API call; bounded revision
is frozen. No new vectors; cached and estimated uncached timing remain separate.
