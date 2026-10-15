"""R03: exact source metadata relations and independently recomputable catalog aggregates.
Construction uses only records. No gold, test cases, reference answers or external corpus.
"""
import collections,hashlib,json,re
from .baseline import Index as BaselineIndex,messages,validate as common_validate

def norm(s):return re.sub(r'[《》\s]','',s)
class Index:
 def __init__(self,records):
  self.records=dict(records);self.base=BaselineIndex(records);self.meta={};self.books={};self.children=collections.defaultdict(list);self.titles=collections.defaultdict(list);self.authors=collections.defaultdict(list)
  for rid,text in sorted(records.items()):
   if '目录字段：' not in text:continue
   try:m=json.loads(text.rsplit('目录字段：',1)[1])
   except ValueError:continue
   self.meta[rid]=m
   if m.get('书名'):self.books[norm(m['书名'])]=rid
   if m.get('出处典籍'):
    self.children[norm(m['出处典籍'])].append(rid)
    if m.get('标题'):self.titles[norm(m['标题'])].append(rid)
   if m.get('书名') and m.get('著者'):self.authors[m['著者']].append(rid)
  self.aggregates={}
  for kind,groups in [('book',self.children),('title',self.titles)]:
   for name,ids in sorted(groups.items()):
    aid='CAT-'+kind+'-'+hashlib.sha256(name.encode()).hexdigest()[:12]
    if kind=='book':
     heading=f'冻结资料目录统计：出处典籍为《{name}》的相关条目共{len(ids)}条。'
     entries=[f"{rid}：{self.meta[rid].get('标题','[目录未载标题]')}（{self.meta[rid].get('卷次','')}）"for rid in ids]
     # A bounded view explicitly distinguishes full count from displayed examples.
     shown=[];used=0
     for e in entries:
      if used+len(e)>1700:break
      shown.append(e);used+=len(e)
     text=heading+'计数按唯一原始记录ID，非古籍全部方剂数，也未按同名合并。'+f'下列展示{len(shown)}/{len(ids)}条目录：\n'+'\n'.join(shown)
    else:
     grouped=collections.Counter(self.meta[rid]['出处典籍']for rid in ids)
     text=f'冻结资料目录统计：标题严格等于“{name}”的记录共{len(ids)}条，涉及{len(grouped)}部典籍。按记录ID计数，非去重处方数量；同名不代表组成主治相同。按典籍分组：'+ '；'.join(f'{b}{n}条'for b,n in sorted(grouped.items()))+'。'
    self.aggregates[(kind,name)]={'id':aid,'source_id':aid,'start':0,'end':len(text),'text':text,'derived':True,'derivation':{'operation':'group_unique_record_ids_by_exact_original_metadata','field':'出处典籍'if kind=='book'else'标题','value':name,'record_ids':ids,'count':len(ids),'source_sha256':{rid:hashlib.sha256(records[rid].encode()).hexdigest()for rid in ids}}}
 def search(self,q,k=5):
  seeds=self.base.search(q,k);out=[];seen=set();chars=0
  def add(c):
   nonlocal chars
   if c['id']in seen or chars+len(c['text'])>5800:return
   seen.add(c['id']);out.append(c);chars+=len(c['text'])
  def source(rid,limit=1000):
   text=self.records[rid];end=min(len(text),limit);add({'id':f'{rid}@0:{end}','source_id':rid,'start':0,'end':end,'text':text[:end]})
  # Baseline seeds retained exactly; GM and isolated fixtures naturally fall back.
  for s in seeds:add(s)
  nq=norm(q);booknames=[b for b in self.books if len(b)>=3 and b in nq]
  booknames=sorted([b for b in booknames if not any(b!=other and b in other for other in booknames)],key=lambda b:(-len(b),b))
  for name in booknames[:4]:source(self.books[name],1400)
  catalog_intent=bool(re.search('多少|几首|几条|哪几|收录|这套|相关|论述|方剂|不同|对比|几种',q))
  if catalog_intent:
   for name in booknames[:2]:
    if ('book',name)in self.aggregates:add(self.aggregates[('book',name)])
  for author,ids in sorted(self.authors.items()):
   if len(author)>=2 and author in q:
    for rid in ids[:4]:source(rid,1000)
  if re.search('多少|几首|几条|同名|区别|比较|对比|出处|哪本|哪部|形成|炮制',q):
   names=[t for t in self.titles if len(t)>=3 and t in nq];names=[t for t in names if not any(t!=v and t in v for v in names)]
   for name in sorted(names,key=lambda s:(-len(s),s))[:2]:
    ids=self.titles[name];add(self.aggregates[('title',name)])
    # Distinct source books first, then remaining records. Never collapse same-name formulas.
    first={}
    for rid in ids:first.setdefault(self.meta[rid]['出处典籍'],rid)
    ordered=list(first.values())+[rid for rid in ids if rid not in first.values()]
    for rid in ordered[:4]:source(rid,650)
  return out

def validate(raw,chunks):
 v=common_validate(raw.get('content',''),chunks)
 if raw.get('stream_done')is not True or raw.get('finish_reason')!='stop':v['valid']=False;v['errors'].append('incomplete envelope')
 return v
