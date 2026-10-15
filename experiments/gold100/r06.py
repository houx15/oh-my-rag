"""R06: compose hybrid seeds, source dependencies, exact catalog and R04 prompt.

The same frozen source vectors and query vectors may be reused. The evaluation
must report actual cached latency separately and add the prior measured query
embedding latency as an explicitly labelled estimated uncached comparison.
No case IDs, reference answers or generated answers are read by this module.
"""
import re
from collections import defaultdict
from .r03 import Index as CatalogIndex, norm
from .r05 import Index as HybridIndex
from .r04 import messages, validate

MAX_CONTEXT = 6000


class Index:
    def __init__(self, records, source_vectors):
        self.records = dict(records)
        self.hybrid = HybridIndex(records, source_vectors)
        self.catalog = CatalogIndex(records)
        self.pages = {}; self.documents = defaultdict(list)
        for rid in sorted(records):
            m = re.fullmatch(r'(D\d+):(\d+):(\d+)', rid)
            if m:
                doc, page, part = m.group(1), int(m.group(2)), m.group(3)
                self.pages[(doc, page, part)] = rid
                self.documents[doc].append(rid)

    def search(self, question, query_vector, k=8):
        seeds = self.hybrid.search(question, query_vector, k)
        catalog = self.catalog
        aggregates = []; preferred = []
        nq = norm(question)
        books = [b for b in catalog.books if len(b) >= 3 and b in nq]
        books = sorted([b for b in books if not any(b != other and b in other for other in books)], key=lambda b: (-len(b), b))
        catalog_intent = bool(re.search('多少|几首|几条|哪几|收录|这套|相关|论述|方剂|不同|对比|几种', question))
        for book in books[:3]:
            preferred.append(catalog.books[book])
            if catalog_intent and ('book', book) in catalog.aggregates:
                aggregates.append(catalog.aggregates[('book', book)])
        titles = [t for t in catalog.titles if len(t) >= 3 and t in nq]
        titles = sorted([t for t in titles if not any(t != other and t in other for other in titles)], key=lambda t: (-len(t), t))
        if re.search('多少|几首|几条|同名|区别|不同|比较|对比|有何|出处|哪本|哪部|哪些|形成|炮制', question):
            for title in titles[:2]:
                aggregates.append(catalog.aggregates[('title', title)])
                distinct = {}
                for rid in catalog.titles[title]:
                    distinct.setdefault(catalog.meta[rid]['出处典籍'], rid)
                preferred.extend(list(distinct.values())[:6])
        for author, ids in sorted(catalog.authors.items()):
            if len(author) >= 2 and author in question:
                preferred.extend(ids[:4])

        out = []; used = 0; intervals = defaultdict(list); seen_derived = set()

        def derived(chunk):
            nonlocal used
            if chunk['id'] in seen_derived or used + len(chunk['text']) > MAX_CONTEXT:
                return
            seen_derived.add(chunk['id']); out.append(chunk); used += len(chunk['text'])

        def source(rid, start=0, end=None):
            nonlocal used
            text = self.records[rid]; end = min(len(text), end if end is not None else len(text))
            # Emit only uncovered exact source intervals; never concatenate disjoint text.
            pending = [(start, end)]
            for lo, hi in intervals[rid]:
                remaining = []
                for a, b in pending:
                    if b <= lo or a >= hi:
                        remaining.append((a, b))
                    else:
                        if a < lo:remaining.append((a, lo))
                        if b > hi:remaining.append((hi, b))
                pending = remaining
            for a, b in pending:
                if b <= a or not text[a:b].strip() or used + b - a > MAX_CONTEXT:
                    continue
                out.append({'id': f'{rid}@{a}:{b}', 'source_id': rid, 'start': a, 'end': b, 'text': text[a:b]})
                intervals[rid].append((a, b)); used += b - a

        # Exact counts are placed before examples, to avoid local-hit counts masquerading as totals.
        for chunk in aggregates[:3]:derived(chunk)
        for rid in dict.fromkeys(preferred):source(rid, 0, min(len(self.records[rid]), 750))
        # Keep leading hybrid evidence, merging the original record when short enough.
        for c in seeds[:5]:
            text = self.records[c['source_id']]
            if len(text) <= 1200:source(c['source_id'])
            else:source(c['source_id'], c['start'], min(len(text), c['end'] + 180))

        policy = bool(re.search('申请|补贴|奖励|办法|政策|扶持|资助|申报|有效|门槛|认定', question))
        if policy:
            docs = list(dict.fromkeys(c['source_id'].split(':')[0] for c in seeds if c['source_id'].split(':')[0] in self.documents))
            # Attach same-document scope/validity clauses, never borrow another policy's rule.
            for doc in docs[:2]:
                matches = [rid for rid in self.documents[doc] if re.search(r'有效期|有效期限|以上.{0,25}本数|本数.{0,25}以下', self.records[rid], re.S)]
                for rid in matches[:2]:source(rid, 0, min(len(self.records[rid]), 1400))
        # Page relations recover clauses and lists that cross a physical page boundary.
        for c in seeds[:3]:
            m = re.fullmatch(r'(D\d+):(\d+):(\d+)', c['source_id'])
            if not m:continue
            doc, page, part = m.group(1), int(m.group(2)), m.group(3)
            for delta in [1, -1]:
                rid = self.pages.get((doc, page + delta, part))
                if rid:source(rid, 0, min(len(self.records[rid]), 1000))
        for c in seeds[5:]:source(c['source_id'], c['start'], c['end'])
        return out
