"""Private, frozen two-arm evaluation; no provider calls without explicit --live.

Repository-owned orchestration. Existing read-only corpus adapter is an explicit
path, never discovered from reference answers. All paid requests use the existing
screening, journal, sole ledger and bounded approved transport.
"""
import argparse,hashlib,importlib.util,json,os,random,sys,threading,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from decimal import Decimal
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
from scripts.keyword_experiment import read,write,lines,H,start_ctx
from newdomain.grounded_prose import build_messages,render,catalog
from newdomain.keyword_control import select
from newdomain.journal import DispatchJournal
from scripts.optimization_full_rerun_v3 import RUBRIC,parse_score

class Runtime:
 def __init__(self,base_runtime,redaction_names_path,institution_policy_path):
  from scripts.grounded_prose_benchmark import Runtime as OriginalRuntime
  self.original=OriginalRuntime(base_runtime,redaction_names_path,institution_policy_path)
  self.base=self.original.base;self.redactor=self.original.redactor
 def prepare(self,j,arm):
  if arm not in ('baseline','A1_schema','C1_original'):raise ValueError('unknown isolated arm')
  ctx,msg,tr=self.original.prepare(j,'baseline')
  if arm=='A1_schema':
   from newdomain.component_contract import messages
   msg=messages(msg,j['corpus']);tr={**tr,'component':'A1 prompt reminder only; unchanged parser/context'}
  if arm=='C1_original' and j['corpus']!='regression':
   original,_,_=self.base.prepare(j['corpus'],j['question'],'baseline')
   original=self.redactor.value(original)
   # Strict byte ceiling parity: do not truncate or displace original text to fit.
   if sum(len(t.encode())for t in original.values())<=sum(len(t.encode())for t in ctx.values()) and len(original)<=len(ctx):
    ctx=original
    if j['corpus']=='niuhuang':
     from newdomain.citation_contract_v3 import messages
     msg=messages(self.base.nh_messages(j['question'],ctx))
    else:
     from newdomain.candidate import build_messages as gm_messages
     meta=self.base.gm['candidate'][3]
     msg=gm_messages(j['question'],[{**meta.get(k,{}),'id':k,'text':v,'title':meta.get(k,{}).get('title','来源清单的可复算统计'),'locator':meta.get(k,{}).get('locator','derived-counts')}for k,v in ctx.items()])
     msg=self.base.pipelines['baseline'].prepare_gm(j['question'],ctx,msg,meta)['messages']
    tr={**tr,'component':'C1 all-original protected under unchanged source and byte ceilings','fallback':False}
   else:tr={**tr,'component':'C1 all-original protected','fallback':True,'reason':'original exceeds frozen byte/source ceiling'}
  return self.redactor.value(ctx),self.redactor.value(msg),tr
 def canonical(self,j,raw):
  return self.original.canonical({**j,'arm':'baseline'},raw)

def append_locked(path,value,lock):
 with lock:
  with path.open('a')as f:f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def prepare(args):
 n=args.directory;n.mkdir(exist_ok=True);cfg=read(n/'configuration.json');rt=Runtime(cfg['base_runtime'],cfg['redaction_names_path'],cfg['institution_policy_path'])
 rows=read(cfg['roster']);selected=set(cfg.get('case_ids',[]));jobs=[];refs=[];failures=[]
 for row in rows:
  if selected and row['qid']not in selected:continue
  j={k:row[k]for k in ['corpus','question','origin']};j['case_id']=row['qid'];j['outbound_question']=rt.redactor.text(j['question'])
  if j['corpus']=='regression':j.update(regression_context=row['prepared']['context'],regression_messages=row['prepared']['messages'])
  refs.append(rt.redactor.value({k:row[k]for k in ['qid','question','provided_reference','reference_sources','source_status']}))
  for arm in cfg['arms']:
   job={**j,'arm':arm,'qid':j['case_id']+'/'+arm}
   try:
    t=time.perf_counter();ctx,msg,tr=rt.prepare(j,arm);job.update(context=ctx,messages=msg,trace=tr,offline_preparation_ms=(time.perf_counter()-t)*1000)
    assert len(json.dumps(msg,ensure_ascii=False).encode())<=30000
   except Exception as ex:job.update(preparation_failure=type(ex).__name__+':'+str(ex));failures.append({'qid':job['qid'],'error':job['preparation_failure']})
   jobs.append(job)
  if len(refs)%50==0:print('PREPARED',len(refs),flush=True)
 random.Random(212026).shuffle(jobs)
 write(n/'answer-jobs.json',jobs);write(n/'evaluation-only.json',refs);write(n/'preparation-failures.json',failures)
 write(n/'roster-summary.json',{'distinct_cases':len(refs),'arms':len(cfg['arms']),'outputs_scheduled':len(jobs),'origins':dict(Counter(j['corpus']+'/'+j['origin']for j in jobs if j['arm']=='baseline')),'generation_reused':0,'historically_exposed':True,'preparation_failures':failures})
 print('PREPARED TOTAL',len(refs),'failures',len(failures),flush=True)

def allocate(args):
 from newdomain.bailian_workspace_successor import create_successor
 n=args.directory;b=n.parent;live=read(b/'LIVE-OPTIMIZATION-STATUS.json');assert live['active_paid_run']is None
 old=Path(live['latest_profile']);p=read(old);m=read(p['manifest_path']);assert read(p['final_ledger_path'])['totals']['open_reservations']==0
 # Historical manifests/ledgers remain intact. Changed code is versioned by Git
 # and gets new hashes for this new authorized scope, never reused for old runs.
 paths=set(m['scope_hashes']);paths.update(str(p)for p in [Path(__file__),R/'newdomain/grounded_prose.py',R/'newdomain/component_contract.py',R/'scripts/grounded_prose_benchmark.py',R/'tests/test_component_contract.py',R/'tests/test_grounded_prose.py',R/'tests/test_retrieval_determinism.py',R/'newdomain/outbound_redaction.py',R/'tests/test_outbound_redaction.py',n/'configuration.json',n/'answer-jobs.json',n/'evaluation-only.json',n/'plan.md',n/'roster-summary.json'])
 for name in ['evidence_pool.py','keyword_control.py','keyword_hypotheses.py','keyword_selection.py','keyword_facet_selection.py']:paths.add(str(R/'newdomain'/name))
 for filename in ['offline-verification.json','redaction-audit.json','benchmark-code-freeze.json']:
  if(n/filename).exists():paths.add(str(n/filename))
 scope={f:hashlib.sha256(Path(f).read_bytes()).hexdigest()for f in paths}
 authority=read(b/'bailian-resume-20261013/authority.json');authority['user_instruction']='User explicitly authorizes controlled component ablations, fixed common development roster, isolated A1 prompt contract and C1 original-branch protection; no promotion from development results. Sole writer, existing providers and screening, cumulative200USD cap, no push/upload/deploy. Historically exposed mixed-origin roster, preserve all failures, no retries or production promotion.'
 d=n/'answers';d.mkdir(exist_ok=True);cap=2*sum('preparation_failure'not in j for j in read(n/'answer-jobs.json'))
 profile=create_successor(old,d/'allocation',authority,cap,scope,bailian_route=True,public_source_policy_path=b/'public-source-restoration-20261013/institution-policy.json')
 live.update(active_paid_run=str(d),latest_profile=str(d/'allocation/profile.json'),status=n.name+'_active',active_expected=len(read(n/'answer-jobs.json')),active_completed=0)
 write(b/'LIVE-OPTIMIZATION-STATUS.json',live);print('ALLOCATED',cap,'calls; cumulative',read(profile['manifest_path'])['prior_spend_usd'])

def review_messages(j,answer,raw,valid,ref):
 # Own exact quotations are supplied with the answer; context is not duplicated
 # a second time. Exact substring checks happen locally before review.
 payload={'question':j.get('outbound_question',j['question']),'answer':answer,'raw_answer_if_invalid':None if valid else raw.get('content'),'mechanically_valid':valid,'provided_reference':ref['provided_reference'],'reference_sources':dict(ref['reference_sources']),'source_status':ref['source_status']}
 omitted=[]
 while len(json.dumps(payload,ensure_ascii=False).encode())>27000 and payload['reference_sources']:
  key=next(reversed(payload['reference_sources']));omitted.append(key);payload['reference_sources'].pop(key)
 messages=[{'role':'system','content':RUBRIC},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
 if len(json.dumps(messages,ensure_ascii=False).encode())>30000:raise ValueError('review byte cap; no answer truncation')
 return messages,omitted

def run(args):
 if not args.live:raise ValueError('explicit --live required')
 from newdomain import bailian_bounded_transport as transport
 n=args.directory;d=n/'answers';ctx=start_ctx(d);cfg=read(n/'configuration.json');rt=Runtime(cfg['base_runtime'],cfg['redaction_names_path'],cfg['institution_policy_path']);jobs=read(n/'answer-jobs.json');refs={r['qid']:r for r in read(n/'evaluation-only.json')};done={r['qid']for r in lines(d/'results.jsonl')};lock=threading.Lock();runtime_lock=threading.Lock();stop=threading.Event()
 with DispatchJournal(d/'calls.journal.jsonl')as journal:
  def call(q,kind,messages):
   profile=read(d/'allocation/profile.json');totals=read(profile['final_ledger_path'])['totals']
   # Three workers maximum: keep worst-case headroom for all concurrent calls.
   if Decimal(str(totals['charged_cost_usd']))+Decimal('6.0192')>Decimal(str(cfg['stage_ceiling_usd'])):
    raise ValueError('exploratory ceiling reached; confirmation reserve protected')
   h=H(messages)
   if journal.check_resume(q,kind,h,transport.MODEL)is not None:raise ValueError('prior dispatch without completed result; reconcile explicitly')
   journal.record_started(q,kind,h,transport.MODEL)
   try:
    t=time.perf_counter();response=transport.chat(ctx,messages);ms=(time.perf_counter()-t)*1000
    if response['actual_model']!=transport.MODEL:raise ValueError('model mismatch')
    append_locked(d/'responses.jsonl',{'qid':q,'kind':kind,'prompt_sha256':h,'response':response,'wall_ms':ms},lock)
    journal.record_terminal(q,kind,h,transport.MODEL,True,result_sha256=H(response));return response,ms
   except Exception as ex:
    journal.record_terminal(q,kind,h,transport.MODEL,False,error=type(ex).__name__+':'+str(ex));raise
  def work(j):
   if stop.is_set():return
   item=dict(j)
   try:
    if 'preparation_failure'in j:raise ValueError(j['preparation_failure'])
    with runtime_lock:
     start=time.perf_counter();context,messages,trace=rt.prepare(j,j['arm']);prep=(time.perf_counter()-start)*1000
    if context!=j['context']or messages!=j['messages']:raise ValueError('frozen live reconstruction mismatch')
    raw,gms=call(j['qid'],'generation',messages);t=time.perf_counter()
    try:
     with runtime_lock:answer,valid,gate=rt.canonical(j,raw)
    except (ValueError,KeyError,TypeError)as ex:answer=None;valid=False;gate={'failure':str(ex)}
    cms=(time.perf_counter()-t)*1000
    if valid:
     for sentence in answer['sentences']:
      for cite in sentence['citations']:
       if cite['id']not in context or not cite['quote']or cite['quote']not in context[cite['id']]:raise ValueError('citation provenance failure')
    item.update(generation=raw,answer=answer,valid=valid,gate=gate,preparation_ms=prep,generation_wall_ms=gms,canonicalization_ms=cms,pipeline_component_sum_ms=prep+gms+cms,latency_scope='Warm retrieval/prompt + generation + validation component sum; cached embeddings, no grading/queue/cold setup. Regression fixtures have fixed historical contexts.')
    append_locked(d/'generations.jsonl',item,lock)
    messages,omitted=review_messages(j,answer,raw,valid,refs[j['case_id']]);review,rms=call(j['qid'],'review',messages);item.update(review=review,review_wall_ms=rms,reference_sources_omitted=omitted)
    try:item['score']=parse_score(review,valid)
    except (ValueError,KeyError,TypeError)as ex:item.update(score=None,score_error=str(ex))
   except Exception as ex:
    item.update(execution_failure=type(ex).__name__+':'+str(ex),score=None)
    # A provider/reconstruction failure stops admission of further jobs; already
    # in-flight calls settle. No retry or hidden replacement.
    if 'preparation_failure'not in j:stop.set()
   append_locked(d/'results.jsonl',item,lock)
   with lock:
    done.add(j['qid']);print('DONE',len(done),'/',len(jobs),j['qid'],'valid',item.get('valid'),'pass',(item.get('score')or{}).get('adequate'),'failure',item.get('execution_failure'),flush=True)
  with ThreadPoolExecutor(max_workers=args.workers)as pool:
   futures=[pool.submit(work,j)for j in jobs if j['qid']not in done]
   for f in as_completed(futures):f.result()
 print('RUN END',len(done),'/',len(jobs),'stopped',stop.is_set(),flush=True)

def close(args):
 n=args.directory;b=n.parent;d=n/'answers';p=read(d/'allocation/profile.json');m=read(p['manifest_path']);total=read(p['final_ledger_path'])['totals'];assert total['open_reservations']==0
 events=lines(d/'calls.journal.jsonl');assert sum(x['status']=='started'for x in events)==sum(x['status']=='terminal'for x in events)
 cumulative=str(Decimal(str(m['prior_spend_usd']))+Decimal(str(total['charged_cost_usd'])))
 live=read(b/'LIVE-OPTIMIZATION-STATUS.json');assert live['active_paid_run']==str(d)
 live.update(active_paid_run=None,status=n.name+'_closed',cumulative_spend_usd=cumulative,cumulative_conservative_spend_usd=float(cumulative),open_reservations=0,active_completed=len(lines(d/'results.jsonl')))
 write(b/'LIVE-OPTIMIZATION-STATUS.json',live);write(d/'settlement.json',{'totals':total,'cumulative_conservative_usd':cumulative});print('CLOSED',cumulative,total)

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','allocate','run','close']);p.add_argument('--directory',type=Path,required=True);p.add_argument('--live',action='store_true');p.add_argument('--workers',type=int,choices=[1,2,3],default=3);a=p.parse_args();globals()[a.action](a)
if __name__=='__main__':main()
