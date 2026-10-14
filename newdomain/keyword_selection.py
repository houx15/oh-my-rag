"""Selection-only controls over frozen retrieval hypotheses; no answer labels."""
import math,re
from collections import Counter
from newdomain.evidence_pool import grams, weighted_overlap

STOP=set('的了是在有和与及或吗呢啊呀我你他它这那就都也还把被请给说一下什么怎么多少')

def select(search,question,queries,baseline,k,mode,tokenize):
    if mode not in ('equal_rrf','token_coverage'):raise ValueError('unknown selector')
    if k<1:raise ValueError('positive context budget required')
    if not queries:return dict(list(baseline.items())[:k]),{'selected':list(baseline)[:k],'fallback':True}
    views=[]
    for q in [question]+queries:
        pool,_=search.pool.build(q,{},k=20);views.append(list(pool))
    scores={}
    for view in views:
        for rank,rid in enumerate(view):scores[rid]=scores.get(rid,0)+1/(61+rank)
    selected=list(baseline)[:max(1,k//2)]
    # Preserve original windows; new windows use the same bigram rule in both
    # arms. Thus the ablation changes ranking, not span extraction or generation.
    context={rid:baseline[rid]for rid in selected};windows={}
    qg=set().union(*(grams(q)for q in [question]+queries))
    candidates={}
    for rid in scores:
        if rid in baseline:candidates[rid]=baseline[rid];continue
        text=search.records[rid]
        offsets=list(range(0,max(1,len(text)-899),450))+[max(0,len(text)-900)]
        start=max(offsets,key=lambda a:(weighted_overlap(search.pool.idf, grams(text[a:a+900])&qg),-a))
        candidates[rid]=text[start:start+900];windows[rid]=[start,min(len(text),start+900)]
    terms={t for q in [question]+queries for t in tokenize(q)if re.search(r'[\u4e00-\u9fffA-Za-z0-9]',t)and t not in STOP}
    # Document frequency comes only from the corpus. Literal single-character
    # attributes survive tokenization; unknown hypotheses receive no weight.
    df={t:sum(t in body for body in search.records.values())for t in terms}
    weights={t:math.log(1+len(search.records)/(1+n))for t,n in df.items()if n}
    covered={t for t in weights if any(t in body for body in context.values())}
    while len(selected)<k:
        remaining=[rid for rid in scores if rid not in selected]
        if not remaining:break
        def key(rid):
            gain=weighted_overlap(weights, {t for t in weights if t not in covered and t in candidates[rid]}) if mode=='token_coverage'else 0
            return (-gain,-scores[rid],rid)
        rid=min(remaining,key=key);selected.append(rid);context[rid]=candidates[rid]
        covered.update(t for t in weights if t in candidates[rid])
    return context,{'mode':mode,'views':views,'selected':selected,'original_retained':list(baseline)[:max(1,k//2)],'new_source_windows':{rid:windows[rid]for rid in selected if rid in windows},'query_terms':sorted(weights),'hypothesis_status':'retrieval guesses only, not facts'}
