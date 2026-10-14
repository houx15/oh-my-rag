"""Prepare Cycle13 using frozen Cycle12 inference; no provider call."""
import argparse,hashlib,json,random,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.keyword_experiment import read,write,lines,runtime,searches
from newdomain.keyword_selection import select
from newdomain.citation_contract_v3 import messages as contract
from newdomain.candidate import build_messages
from pipeline.tokenize import tokenize

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();n=a.directory;n.mkdir(exist_ok=True)
 e=runtime(a.runtime);ss=searches(e);ex={x['case_id']:x for x in lines(a.source/'expansion/results.jsonl')};jobs=[]
 for f in ['inference.json','evaluation-only.json','selection.json']:(n/f).write_bytes((a.source/f).read_bytes())
 write(n/'input-provenance.json',{str(a.source/f):hashlib.sha256((a.source/f).read_bytes()).hexdigest()for f in ['inference.json','evaluation-only.json','selection.json','expansion/results.jsonl']})
 for j in read(n/'inference.json'):
  for arm in ['equal_rrf','token_coverage']:
   t=time.perf_counter();q=j['question'];c=j['corpus'];base=j['baseline_context'];queries=ex[j['case_id']]['queries'];ctx,tr=select(ss[c],q,queries,base,len(base),arm,tokenize);msg=j['baseline_messages']
   if ctx!=base:
    if c=='niuhuang':msg=contract(e.nh_messages(q,ctx))
    else:
     meta=e.gm['candidate'][3];msg=build_messages(q,[{**meta.get(k,{}),'id':k,'text':v,'title':meta.get(k,{}).get('title','来源清单的可复算统计'),'locator':meta.get(k,{}).get('locator','derived-counts')}for k,v in ctx.items()]);msg=e.pipelines['baseline'].prepare_gm(q,ctx,msg,meta)['messages']
   jobs.append(dict(case_id=j['case_id'],qid=j['case_id']+'/'+arm,corpus=c,question=q,cohort=j['cohort'],arm=arm,context=ctx,messages=msg,trace=tr,baseline_preparation_ms=j['baseline_preparation_ms'],expansion_wall_ms=ex[j['case_id']]['expansion_wall_ms'],merge_rerank_ms=(time.perf_counter()-t)*1000,hypothesis_preparation_ms=j['hypothesis_preparation_ms'],same_prompt=msg==j['baseline_messages']))
 random.Random(1314).shuffle(jobs);write(n/'answer-jobs.json',jobs)
if __name__=='__main__':main()
