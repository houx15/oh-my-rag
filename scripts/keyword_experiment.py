"""Local Cycle12 runner. Explicit artifact path; staged serial ledger ownership.

Uses existing local corpus/cache/runtime through --runtime; never uploads files,
installs dependencies, retries calls, or exposes reference answers to retrieval.
"""
import argparse,hashlib,importlib.util,json,os,random,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from newdomain.keyword_hypotheses import KeywordSearch,parse
from newdomain.profile import load_profile,verify_profile
from newdomain.transport import LiveContext
from newdomain.journal import DispatchJournal
H=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def lines(p):return [json.loads(s)for s in p.read_text().splitlines()]if p.exists()else[]
def append(p,x):
 with p.open('a')as f:f.write(json.dumps(x,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def runtime(path):
 spec=importlib.util.spec_from_file_location('keyword_runtime',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.Runtime()
def searches(e):
 from pipeline.tokenize import tokenize
 return {c:KeywordSearch(v,tokenize)for c,v in {'niuhuang':{k:r['text']for k,r in e.original.items()},'guangming':e.gm['candidate'][4]}.items()}
def start_ctx(d):
 p=verify_profile(load_profile(d/'allocation/profile.json'),'final')
 for path,h in read(p['manifest_path'])['scope_hashes'].items():
  if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=h:raise ValueError('scope changed:'+path)
 return LiveContext(manifest_path=p['manifest_path'],redaction_names_path=p['redaction_names_path'],stage='final',expected_ledger_path=p['ledger_path'])
def caller(d,ctx,transport,journal):
 def call(q,kind,messages):
  h=H(messages);model=transport.MODEL
  # Completed outcomes are loaded by the outer loop. No retry/cache aliasing here.
  if journal.check_resume(q,kind,h,model)is not None:raise ValueError('prior dispatch exists; reconcile before continuation')
  journal.record_started(q,kind,h,model)
  try:
   start=time.perf_counter();response=transport.chat(ctx,messages);elapsed=(time.perf_counter()-start)*1000
   if response['actual_model']!=model:raise ValueError('returned model mismatch')
   append(d/'responses.jsonl',dict(qid=q,kind=kind,prompt_sha256=h,response=response,response_sha256=H(response),wall_ms=elapsed))
   journal.record_terminal(q,kind,h,model,True,result_sha256=H(response));return response,elapsed
  except Exception as ex:
   journal.record_terminal(q,kind,h,model,False,error=type(ex).__name__+':'+str(ex));raise
 return call

def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['inventory','prepare','allocate','expand','answers','run','close']);a.add_argument('--directory',type=Path,required=True);a.add_argument('--runtime',type=Path);a.add_argument('--stage',choices=['expansion','answers']);args=a.parse_args();n=args.directory;b=n.parent;n.mkdir(exist_ok=True)
 if args.action=='inventory':
  e=runtime(args.runtime);s=searches(e);write(n/'source-vocabulary-inventory.json',{c:dict(records=len(v.records),terms=len(v.terms),platform_terms={t:v.terms[t]for t in v.terms if t.lower()in ('pad','livepad')},sample=v.vocabulary('资料展示'))for c,v in s.items()});return
 if args.action=='prepare':
  e=runtime(args.runtime);ss=searches(e);selection=read(n/'selection.json');rows={x['case_id']:x for x in read(b/'broad-original-cycle7-20261014/jobs.json')};jobs=[];evaluation=[]
  for entry in selection:
   r=rows[entry['case_id']];q=r['question'];c=r['corpus'];v=ss[c];t=time.perf_counter();ctx,msg,tr=e.prepare(c,q,'baseline');ms=(time.perf_counter()-t)*1000
   t=time.perf_counter();vocabulary=v.vocabulary(q);vq=v.deterministic(q);em=v.messages(q);hms=(time.perf_counter()-t)*1000
   jobs.append(dict(case_id=r['case_id'],corpus=c,question=q,cohort=entry['cohort'],baseline_context=ctx,baseline_messages=msg,baseline_trace=tr,baseline_preparation_ms=ms,vocabulary=vocabulary,vocabulary_queries=vq,expansion_messages=em,hypothesis_preparation_ms=hms))
   evaluation.append({k:r[k]for k in ['case_id','question','provided_reference','reference_sources','reference_status']})
  write(n/'inference.json',jobs);write(n/'evaluation-only.json',evaluation);return
 if args.action=='allocate':
  live=read(b/'LIVE-OPTIMIZATION-STATUS.json');assert not live.get('active_paid_run'),'another run active'
  old=Path(live['latest_profile']);stage=args.stage;d=n/stage;d.mkdir(exist_ok=True)
  from newdomain.bailian_qwen_successor import create_successor as qwen
  from newdomain.bailian_workspace_successor import create_successor as deepseek
  paths=set(read(read(old)['manifest_path'])['scope_hashes']);paths.update(str(p)for p in [Path(__file__),R/'newdomain/keyword_hypotheses.py',R/'tests/test_keyword_hypotheses.py',n/'inference.json',n/'evaluation-only.json',n/'selection.json',n/'plan.md',args.runtime])
  if stage=='answers':paths.add(str(n/'answer-jobs.json'))
  scope={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in paths};authority=read(b/'bailian-resume-20261013/authority.json');authority['user_instruction']='User explicitly authorizes source-vocabulary and unrestricted small-model keyword hypotheses in both public corpora, existing approved Bailian models, sole writer,200USD cumulative cap; no push/upload/deploy; serial ledger stages, no retries.'
  cap=len(read(n/'inference.json'))if stage=='expansion'else 2*len(read(n/'answer-jobs.json'))
  p=(qwen if stage=='expansion'else deepseek)(old,d/'allocation',authority,cap,scope,bailian_route=True,public_source_policy_path=b/'public-source-restoration-20261013/institution-policy.json')
  live.update(status='cycle12_'+stage+'_active',active_paid_run=str(d),latest_profile=str(d/'allocation/profile.json'));write(b/'LIVE-OPTIMIZATION-STATUS.json',live);print('carried',read(p['manifest_path'])['prior_spend_usd'],'cap',cap);return
 if args.action=='expand':
  from newdomain import bailian_qwen_transport as transport
  d=n/'expansion';ctx=start_ctx(d);done={x['case_id']for x in lines(d/'results.jsonl')}
  with DispatchJournal(d/'calls.journal.jsonl')as journal:
   call=caller(d,ctx,transport,journal)
   for j in read(n/'inference.json'):
    if j['case_id']in done:continue
    response,ms=call(j['case_id'],'keywords',j['expansion_messages']);failure=None
    try:queries=parse(response)
    except (ValueError,KeyError,TypeError)as ex:queries=[];failure=str(ex)
    append(d/'results.jsonl',dict(case_id=j['case_id'],queries=queries,parse_failure=failure,response=response,expansion_wall_ms=ms));print('EXPANDED',j['case_id'],queries,round(ms),flush=True)
  return
 if args.action=='answers':
  e=runtime(args.runtime);ss=searches(e);ex={x['case_id']:x for x in lines(n/'expansion/results.jsonl')};jobs=[]
  from newdomain.citation_contract_v3 import messages as contract
  from newdomain.candidate import build_messages
  for j in read(n/'inference.json'):
   for arm in ['baseline','vocabulary','small_model']:
    t=time.perf_counter();q=j['question'];c=j['corpus'];base=j['baseline_context'];queries=[]if arm=='baseline'else j['vocabulary_queries']if arm=='vocabulary'else ex[j['case_id']]['queries']
    context,trace=ss[c].select(q,queries,base,len(base));msg=j['baseline_messages']
    if context!=base:
     if c=='niuhuang':msg=contract(e.nh_messages(q,context))
     else:
      meta=e.gm['candidate'][3];msg=build_messages(q,[{**meta.get(k,{}),'id':k,'text':v,'title':meta.get(k,{}).get('title','来源清单的可复算统计'),'locator':meta.get(k,{}).get('locator','derived-counts')}for k,v in context.items()]);msg=e.pipelines['baseline'].prepare_gm(q,context,msg,meta)['messages']
    prep=(time.perf_counter()-t)*1000
    jobs.append(dict(case_id=j['case_id'],qid=j['case_id']+'/'+arm,corpus=c,question=q,cohort=j['cohort'],arm=arm,context=context,messages=msg,trace=trace,baseline_preparation_ms=j['baseline_preparation_ms'],expansion_wall_ms=ex[j['case_id']]['expansion_wall_ms']if arm=='small_model'else 0,merge_rerank_ms=prep,hypothesis_preparation_ms=j['hypothesis_preparation_ms']if arm!='baseline'else 0,same_prompt=msg==j['baseline_messages']))
  random.Random(1214).shuffle(jobs);write(n/'answer-jobs.json',jobs);return
 if args.action=='run':
  from newdomain import bailian_bounded_transport as transport
  e=runtime(args.runtime)
  from optimization_full_rerun_v3 import RUBRIC,parse_score
  d=n/'answers';ctx=start_ctx(d);done={x['qid']for x in lines(d/'results.jsonl')};refs={x['case_id']:x for x in read(n/'evaluation-only.json')}
  with DispatchJournal(d/'calls.journal.jsonl')as journal:
   call=caller(d,ctx,transport,journal)
   for j in read(n/'answer-jobs.json'):
    if j['qid']in done:continue
    response,ms=call(j['qid'],'generation',j['messages']);t=time.perf_counter()
    try:answer,valid,gate=e.canonical(j['corpus'],response,j['context'],'baseline')
    except (ValueError,KeyError,TypeError)as ex:answer=None;valid=False;gate={'failure':str(ex)}
    cm=(time.perf_counter()-t)*1000
    item={**j,'generation':response,'answer':answer,'valid':valid,'gate':gate,'generation_wall_ms':ms,'canonicalization_ms':cm,'pipeline_component_sum_ms':j['baseline_preparation_ms']+j['hypothesis_preparation_ms']+j['expansion_wall_ms']+j['merge_rerank_ms']+ms+cm,'latency_scope':'Measured serial critical-path component sum across staged expansion/generation; cached original-query embeddings; excludes initialization, evaluation and stage idle time, not a single contiguous request.'};append(d/'generations.jsonl',item)
    ref=refs[j['case_id']];payload={**ref,'answer':answer,'raw_answer_if_invalid':None if valid else response['content'],'cited_sources':j['context'],'mechanically_valid':valid};payload.pop('case_id');payload['reference_sources']=dict(payload['reference_sources']);omitted=[]
    while len(json.dumps(payload,ensure_ascii=False).encode())>27000:
     if not payload['reference_sources']:raise ValueError('review too large')
     k=next(reversed(payload['reference_sources']));omitted.append(k);payload['reference_sources'].pop(k)
    review,_=call(j['qid'],'review',[{'role':'system','content':RUBRIC},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]);item.update(review=review,judge_input=payload,reference_sources_omitted=omitted)
    try:item['score']=parse_score(review,valid)
    except (ValueError,KeyError,TypeError)as ex:item.update(score=None,score_error=str(ex))
    append(d/'results.jsonl',item);done.add(j['qid']);print('DONE',len(done),j['qid'],'valid',valid,'adequate',(item['score']or{}).get('adequate'),'pipeline_ms',round(item['pipeline_component_sum_ms']),flush=True)
  return
 if args.action=='close':
  d=n/args.stage;p=read(d/'allocation/profile.json');m=read(p['manifest_path']);totals=read(p['final_ledger_path'])['totals'];assert not totals['open_reservations'];ev=lines(d/'calls.journal.jsonl');assert len([x for x in ev if x['status']=='started'])==len([x for x in ev if x['status']=='terminal'])==totals['requests_dispatched'];assert len(lines(d/'results.jsonl'))==(len(read(n/'inference.json'))if args.stage=='expansion'else len(read(n/'answer-jobs.json')))
  from decimal import Decimal
  cost=str(Decimal(str(m['prior_spend_usd']))+Decimal(str(totals['charged_cost_usd'])));live=read(b/'LIVE-OPTIMIZATION-STATUS.json');live.update(status='cycle12_'+args.stage+'_complete',active_paid_run=None,cumulative_spend_usd=cost,cumulative_conservative_spend_usd=float(cost),open_reservations=0);write(b/'LIVE-OPTIMIZATION-STATUS.json',live);write(d/'settlement.json',{'cumulative_conservative_usd':cost,'totals':totals});print(cost,totals)
if __name__=='__main__':main()
