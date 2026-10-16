"""R09 unchanged candidate, measured query-embedding-to-validation confirmation.

The caller supplies an authorized single-attempt embedding function and generation
function. This module has no API credentials, case labels or scoring references.
Warm corpus indexes remain fixed; query embeddings are always supplied fresh.
"""
import time
from .r09 import messages, validate


def measure(question, index, embed, generate, record_request, clock=time.perf_counter):
    start = clock()
    vector = embed(question)
    embedded = clock()
    chunks = index.search(question, vector)
    msg = messages(question, chunks)
    prepared = clock()
    record_request(chunks, msg)
    raw = generate(msg)
    generated = clock()
    validation = validate(raw, chunks)
    end = clock()
    return dict(raw=raw, validation=validation, chunks=chunks,
                embedding_ms=(embedded-start)*1000,
                preparation_ms=(prepared-embedded)*1000,
                generation_ms=(generated-prepared)*1000,
                validation_ms=(end-generated)*1000,
                response_ms=(end-start)*1000,
                latency_basis='fresh_contiguous_query_embedding_retrieval_generation_validation',
                within_4700ms=(end-start)*1000<=4700)
