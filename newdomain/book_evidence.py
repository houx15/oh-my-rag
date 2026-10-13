"""Exact quoted-book retrieval with topic matching inside that book.

Independent CPU selector. No reference answers, source labels or case IDs enter
selection. Similar title prefixes are never treated as the requested book.
"""
import re
from newdomain.evidence_pool import EvidencePool, grams

class BookEvidence:
    def __init__(self, records):
        self.index=EvidencePool(records)
        self.books={rid:set(re.findall(r'《([^》]+)》',text.split('\n',1)[0])) for rid,text in records.items()}
        self.body={rid:grams(text.split('\n',1)[-1]) for rid,text in records.items()}
    def select(self, question, baseline, k=4):
        if k!=4:raise ValueError('only measured four-source budget supported')
        titles=set(re.findall(r'《([^》]+)》',question))
        topic=grams(re.sub(r'《[^》]+》','',question))
        ranked=[]
        for rid,book in self.books.items():
            overlap=topic & self.body[rid]
            if not titles & book or len(overlap)<2:continue
            score=sum(self.index.idf.get(g,0)for g in overlap)
            ranked.append((score,rid))
        ranked.sort(key=lambda x:(-x[0],x[1]))
        proposed=[rid for score,rid in ranked[:2]]
        promoted=[rid for rid in proposed if rid not in baseline]
        if not promoted:return dict(baseline),{'promoted':[],'exact_titles':sorted(titles)}
        ids=(promoted+list(baseline))[:k]
        return {rid:self.index.records[rid][:900] if rid in promoted else baseline[rid] for rid in ids},{'promoted':promoted,'exact_titles':sorted(titles),'ranked':ranked[:4]}
