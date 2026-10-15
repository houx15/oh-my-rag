"""R05: exact-source dense/BM25 reciprocal-rank fusion.

Vectors must be computed from the unchanged source chunk text. Query vectors are
supplied by the caller; no question IDs, references or answers enter retrieval.
The caller includes fresh query embedding latency in end-to-end measurements.
Generation uses the immutable original baseline system prompt and validator.
"""
import hashlib
import numpy as np
from .baseline import Index as BaselineIndex, messages, validate as common_validate


def text_key(text):
    return hashlib.sha256(text.encode()).hexdigest()


class Index:
    def __init__(self, records, source_vectors):
        self.base = BaselineIndex(records)
        self.chunks = self.base.chunks
        vectors = [source_vectors[text_key(c['text'])] for c in self.chunks]
        self.matrix = np.array(vectors, dtype=np.float32)
        if not self.chunks:
            self.matrix = np.empty((0, 1024), dtype=np.float32)
        if self.matrix.shape != (len(self.chunks), 1024) or not np.isfinite(self.matrix).all():
            raise ValueError('source vector shape or finiteness mismatch')
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError('zero source vector')
        self.matrix = self.matrix / np.maximum(norms, 1e-12)
        self.by_id = {c['id']: i for i, c in enumerate(self.chunks)}

    def search(self, question, query_vector, k=8):
        q = np.asarray(query_vector, dtype=np.float32)
        if q.shape != (1024,) or not np.isfinite(q).all() or np.linalg.norm(q) == 0:
            raise ValueError('invalid query vector')
        if not self.chunks:
            return []
        # Explicit reduction avoids spurious Apple BLAS floating-point warnings.
        cosine = np.einsum('ij,j->i', self.matrix, q / np.linalg.norm(q), optimize=False)
        if not np.isfinite(cosine).all():
            raise ValueError('nonfinite cosine similarity')
        dense = sorted(range(len(self.chunks)), key=lambda i: (-float(cosine[i]), self.chunks[i]['id']))[:40]
        lexical = [self.by_id[c['id']] for c in self.base.search(question, 40)]
        scores = {}
        for ranking in (lexical, dense):
            for rank, i in enumerate(ranking, 1):
                scores[i] = scores.get(i, 0.0) + 1.0 / (60 + rank)
        ranked = sorted(scores, key=lambda i: (-scores[i], self.chunks[i]['id']))
        # Avoid spending the context on overlapping windows of a single record;
        # keep at most two windows per record and at most eight original blocks.
        chosen = []; by_source = {}
        for i in ranked:
            c = self.chunks[i]; prior = by_source.setdefault(c['source_id'], [])
            if len(prior) >= 2:
                continue
            if any(max(0, min(c['end'], p['end']) - max(c['start'], p['start'])) > .5 * min(len(c['text']), len(p['text'])) for p in prior):
                continue
            prior.append(c); chosen.append(dict(c, score=scores[i]))
            if len(chosen) == k:
                break
        return chosen


def validate(raw, chunks):
    v = common_validate(raw.get('content', ''), chunks)
    if raw.get('stream_done') is not True or raw.get('finish_reason') != 'stop':
        v['valid'] = False; v['errors'].append('incomplete envelope')
    return v
