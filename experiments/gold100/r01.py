import json,re
from .baseline import Index,validate as common_validate
# Keep exact baseline chunks/retrieval. Sentence/line spans are source-only.
def spans(chunks):
 out={}
 for i,c in enumerate(chunks,1):
  start=0;n=0
  for m in re.finditer(r'.{1,140}(?:[。！？；\n]|$)|.{140}',c['text'],re.S):
   text=m.group(0)
   if text.strip():
    n+=1;out[f'E{i}S{n}']={'id':c['id'],'quote':text}
 return out
SYSTEM='你是资料问答助手。当前日期2026-10-15。只根据给定资料作事实回答，引用原文编号。输出完整JSON：{"sentences":[{"text":"回答句","evidence":["E1S1"]}]}。资料编号只能填已有编号，不抄写长引文。澄清、资料不足声明、无法执行界面操作和安全提醒允许evidence为空，不要求固定话术。简洁直接，完整回答所有子问题，不以无关信息填充。内部检查：金额的基数、比例、封顶、必要资格/期限；比较的双方对象和各自条件；数字单位与差额；汇总只可基于全量清点，不能把top检索结果当全部；历史政策说明原版本与当前资格待核实，期限明确时按当前日期判断；计划不证明当前状态，损坏单位不能猜补。名称不确定要条件式匹配或澄清；可答部分仍回答。文献主张不等于现代疗效或个人安全结论。个人服药问题不要复述剂量和配制步骤；突发严重症状建议立即专业急救，其他个人用药建议咨询医生药师核对具体产品，不能据古籍自行用药。书籍介绍无需重复无关方剂或药量。连续引文即使末尾截断仍可为连续片段，区别于完整句。输出最多6个简短句对象，不输出思考过程。'
def messages(q,chunks):
 return [{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'question':q,'evidence':[dict(handle=h,**v)for h,v in spans(chunks).items()]},ensure_ascii=False)}]
def validate(raw,chunks):
 meta={'ok':False,'errors':[]};canonical=raw.get('content','')
 try:
  assert raw.get('stream_done')is True and raw.get('finish_reason')=='stop','incomplete envelope'
  obj=json.loads(canonical);assert set(obj)=={'sentences'};mapping=spans(chunks);out=[]
  assert isinstance(obj['sentences'],list)and obj['sentences']
  for s in obj['sentences']:
   assert set(s)=={'text','evidence'} and isinstance(s['evidence'],list)
   assert all(isinstance(h,str)and h in mapping for h in s['evidence']),'unknown evidence handle'
   out.append({'text':s['text'],'citations':[mapping[h]for h in s['evidence']]})
  canonical=json.dumps({'sentences':out},ensure_ascii=False);meta['ok']=True
 except (ValueError,TypeError,AssertionError,KeyError)as ex:meta['errors'].append(str(ex))
 v=common_validate(canonical,chunks);v.update(canonicalization=meta,canonical_content=canonical)
 if not meta['ok']:v['valid']=False;v['errors']+=meta['errors']
 return v
