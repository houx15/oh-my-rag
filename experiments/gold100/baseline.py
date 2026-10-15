"""Standalone lexical baseline; no references, prior answers or existing pipeline imports."""
import re,math,json,collections

def tokens(text):
 out=[]
 for x in re.findall(r'[\u3400-\u9fff]+|[a-zA-Z0-9]+',text.lower()):
  out.extend([x[i:i+2]for i in range(len(x)-1)] if '\u3400'<=x[0]<='\u9fff' and len(x)>1 else [x])
 return out

class Index:
 def __init__(self,records,size=500,overlap=80):
  assert size>overlap>=0
  self.chunks=[];self.postings=collections.defaultdict(list);self.lengths=[]
  for rid,text in sorted(records.items()):
   for start in range(0,len(text),size-overlap):
    chunk={'id':f'{rid}@{start}','source_id':rid,'start':start,'end':min(start+size,len(text)),'text':text[start:start+size]}
    self.chunks.append(chunk)
    if start+size>=len(text):break
  for i,c in enumerate(self.chunks):
   tf=collections.Counter(tokens(c['text']));self.lengths.append(sum(tf.values()))
   for word,count in tf.items():self.postings[word].append((i,count))
  self.avg=sum(self.lengths)/max(1,len(self.lengths)) or 1
 def search(self,q,k=5):
  scores=collections.defaultdict(float);n=len(self.chunks)
  for word in sorted(set(tokens(q))):
   ps=self.postings.get(word,[]);idf=math.log(1+(n-len(ps)+.5)/(len(ps)+.5))
   for i,tf in ps:scores[i]+=idf*tf*2.2/(tf+1.2*(.25+.75*self.lengths[i]/self.avg))
  ranked=sorted(scores,key=lambda i:(-scores[i],self.chunks[i]['id']))[:k]
  return [dict(self.chunks[i],score=scores[i])for i in ranked]

def messages(question,chunks):
 return [{'role':'system','content':'你是资料问答助手。当前日期2026-10-15。仅根据给定资料回答问题；资料不足时明确说明，不编造。区分历史材料、当前事实和个人用药建议。不能操作现场界面。简洁回答，保留必要条件和上限。输出完整JSON：{"sentences":[{"text":"一句回答","citations":[{"id":"资料块ID","quote":"该块内连续原文"}]}]}。每个资料事实附原文引用。澄清、无法执行操作、资料不足声明和安全提醒允许citations为空。不要输出Markdown代码块。'}, {'role':'user','content':json.dumps({'question':question,'sources':[{k:c[k]for k in ['id','text']}for c in chunks]},ensure_ascii=False)}]

def validate(content,chunks):
 errors=[];parsed=None;context={c['id']:c['text']for c in chunks}
 try:
  parsed=json.loads(content)
  assert isinstance(parsed,dict) and isinstance(parsed.get('sentences'),list) and parsed['sentences'],'sentences required'
  for s in parsed['sentences']:
   assert isinstance(s,dict) and isinstance(s.get('text'),str) and s['text'].strip(),'sentence text required'
   assert isinstance(s.get('citations'),list),'citations list required'
   for c in s['citations']:
    assert isinstance(c,dict) and isinstance(c.get('id'),str) and c['id']in context,'unknown citation ID'
    assert isinstance(c.get('quote'),str) and c['quote'].strip() and c['quote']in context[c['id']],'not an exact quote'
 except (ValueError,AssertionError,TypeError,KeyError)as ex:errors.append(str(ex))
 return {'parsed':parsed,'valid':not errors,'errors':errors,'semantic_support_checked':False}
