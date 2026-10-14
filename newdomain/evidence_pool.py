"""Corpus-wide lexical rescue with separate identity and body channels.

Original retrieval remains in the pool; this module only creates candidates for
an evidence selector. No answer references or per-case rules are accepted.
"""
import math,re
from collections import Counter


def grams(text):
    text=re.sub(r'\s+','',text)
    return {text[i:i+2]for i in range(len(text)-1) if re.search(r'[\w\u4e00-\u9fff]',text[i:i+2])}


def weighted_overlap(weights, terms):
    """Canonical accurate sum: set/hash/insertion order cannot break rank ties.

    Do not round or introduce an epsilon: genuine unequal scores still rank by
    weight. Callers retain record-ID and earliest-offset tie breakers.
    """
    return math.fsum(weights.get(term, 0.0) for term in sorted(terms))


class EvidencePool:
    def __init__(self,records):
        self.records=dict(records)
        self.keys={rid:grams(text.split('\n',1)[0]) for rid,text in self.records.items()}
        self.bodies={rid:grams(text) for rid,text in self.records.items()}
        counts=Counter(g for gs in self.bodies.values() for g in gs)
        self.idf={g:math.log(1+len(records)/(1+n))for g,n in counts.items()}
    def build(self,question,baseline,k=20):
        if not 1<=k<=20:raise ValueError('pool bound')
        q=grams(question)
        def rank(channel):
            scores=[(weighted_overlap(self.idf, q & gs),rid)for rid,gs in channel.items()]
            return [rid for s,rid in sorted(scores,key=lambda x:(-x[0],x[1])) if s>0]
        key=rank(self.keys);body=rank(self.bodies)
        ids=[]
        # Preserve initial evidence then interleave distinct identity/body hits.
        for rid in list(baseline)[:4]+[x for pair in zip(key[:20],body[:20])for x in pair]+key+body:
            if rid in self.records and rid not in ids:ids.append(rid)
            if len(ids)==k:break
        return {rid:self.records[rid]for rid in ids},{'key_top20':key[:20],'body_top20':body[:20],'pool_ids':ids,'baseline_retained':list(baseline)[:4]}
