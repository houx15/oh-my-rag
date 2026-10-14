"""Fixed packing with optional source-vocabulary candidate admission.

Independent local implementation. Expansion changes candidate views only;
original-query spans, fusion weights and protected-prefix policy remain fixed.
"""
from newdomain.evidence_pool import grams,weighted_overlap

def select(search,question,queries,baseline,k):
 if k<1:raise ValueError('positive budget')
 if len(queries)>3:raise ValueError('bounded queries')
 views=[list(baseline)]
 for q in [question]+queries:
  pool,_=search.pool.build(q,{},k=20);views.append(list(pool))
 scores={}
 for i,view in enumerate(views):
  for rank,rid in enumerate(view):scores[rid]=scores.get(rid,0)+(2 if i<2 else 1)/(61+rank)
 selected=list(baseline)[:max(1,k//2)]
 for rid in sorted(scores,key=lambda x:(-scores[x],x)):
  if len(selected)==k:break
  if rid not in selected:selected.append(rid)
 qg=grams(question);context={};windows={}
 for rid in selected:
  if rid in baseline:context[rid]=baseline[rid];continue
  text=search.records[rid];offsets=list(range(0,max(1,len(text)-899),450))+[max(0,len(text)-900)]
  start=max(offsets,key=lambda a:(weighted_overlap(search.pool.idf,grams(text[a:a+900])&qg),-a))
  context[rid]=text[start:start+900];windows[rid]=[start,min(len(text),start+900)]
 return context,{'views':views,'hypotheses':list(queries),'selected':selected,'original_retained':list(baseline)[:max(1,k//2)],'new_source_windows':windows,'span_query':'original only','hypotheses_are_evidence':False}
