"""Private source-obligation review preparation and paired ablation reporting."""
import argparse
import json
import random
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import write_new,sha
from optimization_review import freeze
from optimization_atomic_review import PROMPT,validate_verdict


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','report']);p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--cases',type=Path,required=True);a=p.parse_args()
    root=a.root;name=a.name;cases={c['qid']:c for c in json.loads(a.cases.read_text())};assessed=json.loads((root/f'{name}-assessed.json').read_text())
    if a.action=='prepare':
        jobs=[];key=[];order=list(assessed);random.Random(131620).shuffle(order)
        for row in order:
            if not row['valid']:continue
            c=cases[row['qid']];body={'question':c['question'],'source':c['fixed_context'],'answer':'\n'.join(s['text'] for s in row['answer']['sentences']),'obligations':[{k:r[k] for k in ('id','criterion','support')} for r in c['obligations']]}
            jid=f'CASE-{len(jobs):03d}';jobs.append({'qid':jid,'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(body,ensure_ascii=False)}]});key.append({'job':jid,'qid':row['qid'],'arm':row['arm']})
        path=root/f'{name}-atomic-jobs.json';write_new(path,jobs);write_new(root/f'{name}-atomic-key.json',key);freeze(path,Path(__file__).resolve().parents[1]);f=path.with_suffix('.freeze.json');x=json.loads(f.read_text());x['hashes'].update({str(p.resolve()):sha(p) for p in (Path(__file__),a.cases,root/f'{name}-assessed.json',Path(__file__).with_name('optimization_atomic_review.py'))});f.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'review_jobs':len(jobs)}));return
    jobs={j['qid']:json.loads(j['messages'][1]['content']) for j in json.loads((root/f'{name}-atomic-jobs.json').read_text())};keys={j['job']:j for j in json.loads((root/f'{name}-atomic-key.json').read_text())};verdicts={};invalid=[]
    rows=[json.loads(l) for l in (root/f'{name}-atomic-results.jsonl').read_text().splitlines()]
    if len(rows)!=len(keys) or {r['qid'] for r in rows}!=set(keys):raise ValueError('incomplete review coverage')
    for r in rows:
        k=keys[r['qid']];body=jobs[r['qid']]
        try:
            v=validate_verdict(r['response']['content'],body['answer'],body['obligations']);v['adequate']=not v['extra_unsupported'] and all(c['status']=='present' for c in v['checks']);v['schema_valid']=True
        except Exception as e:v={'adequate':False,'schema_valid':False,'error':str(e)};invalid.append(k)
        verdicts[k['qid'],k['arm']]=v
    detail=[];report={}
    for row in assessed:
        key=(row['qid'],row['arm']);v=verdicts.get(key,{'adequate':False,'schema_valid':False,'error':'invalid generation'})
        detail.append({'qid':row['qid'],'group':row['group'],'arm':row['arm'],'valid':row['valid'],'verdict':v,'latency_ms':row['response']['parent_observed_timings']['full_ms'],'ttft_ms':row['response']['parent_observed_timings']['ttft_ms'],'usage':row['response']['usage']})
    for arm in sorted({d['arm'] for d in detail}):
        ds=[d for d in detail if d['arm']==arm];ms=[d['latency_ms'] for d in ds]
        report[arm]={'n':len(ds),'valid':sum(d['valid'] for d in ds),'atomic_adequate':sum(d['verdict']['adequate'] for d in ds),'review_schema_valid':sum(d['verdict']['schema_valid'] for d in ds),'p50_ms':float(np.percentile(ms,50)),'p95_ms':float(np.percentile(ms,95)),'generation_usd':sum((d['usage']['input_tokens']*.3+d['usage']['output_tokens']*1.2)/1e6 for d in ds)}
    pairs={};by={(d['qid'],d['arm']):d for d in detail}
    for arm in report:
        if arm=='C1':continue
        pairs[arm]={'wins':[],'losses':[]}
        for qid in cases:
            b=by[qid,'C1']['verdict']['adequate'];c=by[qid,arm]['verdict']['adequate']
            if c and not b:pairs[arm]['wins'].append(qid)
            if b and not c:pairs[arm]['losses'].append(qid)
    result={'name':name,'metrics':report,'paired':pairs,'invalid_reviews':invalid,'detail':detail,'limitation':'Assistant-source obligations and same-provider model review, not human gold. Transport timing plus process overhead, not complete retrieval end-to-end. No automatic promotion.'}
    write_new(root/f'{name}-comparison.json',result);print(json.dumps({'metrics':report,'paired':pairs,'invalid_reviews':len(invalid)},indent=2))


if __name__=='__main__':main()
