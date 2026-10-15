"""R02: source-only dependency expansion around immutable baseline retrieval.
No gold, references, case IDs, answer history, model rewriting or derived facts.
"""
import re
from .baseline import Index as BaselineIndex,messages,validate as common_validate
class Index:
 def __init__(self,records):
  self.records=dict(records);self.base=BaselineIndex(records);self.doc={};self.pages={}
  for rid in records:
   m=re.fullmatch(r'(D\d+):(\d+):(\d+)',rid)
   if m:
    d,page,part=m.group(1),int(m.group(2)),m.group(3);self.doc.setdefault(d,[]).append(rid);self.pages[(d,page,part)]=rid
 def search(self,q,k=5):
  seeds=self.base.search(q,k);out=[];seen=set();chars=0
  def add(rid,start=0,end=None):
   nonlocal chars
   text=self.records[rid];end=min(len(text),end if end is not None else len(text));key=(rid,start,end)
   if key in seen or not text[start:end].strip() or chars+end-start>9000:return
   seen.add(key);out.append({'id':f'{rid}@{start}:{end}','source_id':rid,'start':start,'end':end,'text':text[start:end]});chars+=end-start
  # Preserve all original top5 source windows before expanding dependencies.
  for s in seeds:add(s['source_id'],s['start'],s['end'])
  seedids=list(dict.fromkeys(s['source_id']for s in seeds))
  for rid in seedids:
   if len(self.records[rid])<=1800:add(rid)
  # Page adjacency is a source-ID relation, not a question-specific answer rule.
  for rid in seedids[:3]:
   m=re.fullmatch(r'(D\d+):(\d+):(\d+)',rid)
   if not m:continue
   d,page,part=m.group(1),int(m.group(2)),m.group(3)
   for delta in [1,-1]:
    near=self.pages.get((d,page+delta,part))
    if near and near not in seedids:add(near)
  # Same-document validity and numerical-boundary clauses accompany policy queries.
  if re.search('申请|补贴|奖励|办法|政策|扶持|资助|申报|有效|门槛',q):
   docs=list(dict.fromkeys(rid.split(':')[0]for rid in seedids if rid.split(':')[0]in self.doc))
   for d in docs[:2]:
    for rid in sorted(self.doc[d]):
     text=self.records[rid]
     if re.search(r'有效期|有效期限|自.{0,35}施行|以上.{0,25}本数|本数.{0,25}以下',text,re.S):add(rid)
  return out

def validate(raw,chunks):
 v=common_validate(raw.get('content',''),chunks)
 if raw.get('stream_done')is not True or raw.get('finish_reason')!='stop':v['valid']=False;v['errors'].append('incomplete envelope')
 return v
