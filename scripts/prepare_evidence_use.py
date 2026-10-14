"""Freeze prompt-only paired jobs from current baseline contexts."""
import argparse,random,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.keyword_experiment import read,write,runtime
from newdomain.evidence_use_prompt import apply

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();n=a.directory;b=n.parent;e=runtime(a.runtime)
 originals={x['case_id']:x for x in read(b/'broad-original-cycle7-20261014/jobs.json')};jobs=[];inference=[];evaluation=[]
 for selection in read(n/'selection.json'):
  x=originals[selection['case_id']];t=time.perf_counter();ctx,msg,tr=e.prepare(x['corpus'],x['question'],'baseline');base_ms=(time.perf_counter()-t)*1000
  inference.append(dict(case_id=x['case_id'],question=x['question'],context=ctx,messages=msg,trace=tr))
  evaluation.append({k:x[k]for k in ['case_id','question','provided_reference','reference_sources','reference_status']})
  for arm in ['baseline','use_check']:
   t=time.perf_counter();messages=apply(msg,arm=='use_check');ms=(time.perf_counter()-t)*1000
   jobs.append(dict(case_id=x['case_id'],qid=x['case_id']+'/'+arm,question=x['question'],corpus=x['corpus'],cohort=selection['cohort'],arm=arm,context=ctx,messages=messages,trace=tr,baseline_preparation_ms=base_ms,hypothesis_preparation_ms=0,expansion_wall_ms=0,merge_rerank_ms=ms,same_prompt=arm=='baseline'))
 random.Random(1415).shuffle(jobs);write(n/'inference.json',inference);write(n/'evaluation-only.json',evaluation);write(n/'answer-jobs.json',jobs)
if __name__=='__main__':main()
