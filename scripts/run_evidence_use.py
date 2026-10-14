"""Serial prompt-only experiment; actual contiguous warm pipeline timing."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.keyword_experiment import read,write,lines,append,runtime,start_ctx,caller
from newdomain.evidence_use_prompt import apply
from newdomain.journal import DispatchJournal
from newdomain import bailian_bounded_transport as transport

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();n=a.directory;e=runtime(a.runtime)
 from optimization_full_rerun_v3 import RUBRIC,parse_score
 d=n/'answers';ctx=start_ctx(d);done={x['qid']for x in lines(d/'results.jsonl')};refs={x['case_id']:x for x in read(n/'evaluation-only.json')}
 with DispatchJournal(d/'calls.journal.jsonl')as journal:
  call=caller(d,ctx,transport,journal)
  for j in read(n/'answer-jobs.json'):
   if j['qid']in done:continue
   start=time.perf_counter();contexts,messages,trace=e.prepare(j['corpus'],j['question'],'baseline');messages=apply(messages,j['arm']=='use_check')
   if contexts!=j['context']or messages!=j['messages']:raise ValueError('frozen evidence or prompt changed')
   prep_ms=(time.perf_counter()-start)*1000;response,gms=call(j['qid'],'generation',messages);t=time.perf_counter()
   try:answer,valid,gate=e.canonical(j['corpus'],response,contexts,'baseline')
   except (ValueError,KeyError,TypeError)as ex:answer=None;valid=False;gate={'failure':str(ex)}
   cms=(time.perf_counter()-t)*1000;elapsed=(time.perf_counter()-start)*1000
   item={**j,'generation':response,'answer':answer,'valid':valid,'gate':gate,'actual_preparation_ms':prep_ms,'generation_wall_ms':gms,'canonicalization_ms':cms,'end_to_end_ms':elapsed,'pipeline_component_sum_ms':elapsed,'latency_scope':'Actual contiguous warm retrieval, prompt construction, journal/provider generation and canonical validation; cached original embeddings; excludes cold initialization, uncached embedding network and grading.'};append(d/'generations.jsonl',item)
   ref=refs[j['case_id']];payload={**ref,'answer':answer,'raw_answer_if_invalid':None if valid else response['content'],'cited_sources':contexts,'mechanically_valid':valid};payload.pop('case_id');payload['reference_sources']=dict(payload['reference_sources']);omitted=[]
   while len(json.dumps(payload,ensure_ascii=False).encode())>27000:
    if not payload['reference_sources']:raise ValueError('review too large')
    key=next(reversed(payload['reference_sources']));omitted.append(key);payload['reference_sources'].pop(key)
   review,_=call(j['qid'],'review',[{'role':'system','content':RUBRIC},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]);item.update(review=review,judge_input=payload,reference_sources_omitted=omitted)
   try:item['score']=parse_score(review,valid)
   except (ValueError,KeyError,TypeError)as ex:item.update(score=None,score_error=str(ex))
   append(d/'results.jsonl',item);done.add(j['qid']);print('DONE',len(done),j['qid'],'valid',valid,'adequate',(item['score']or{}).get('adequate'),'e2e',round(elapsed),flush=True)
if __name__=='__main__':main()
