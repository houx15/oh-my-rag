"""Source-aware obligation review with answer sentence IDs, not retyped quotes."""
import argparse
import json
import random
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import write_new,sha
from optimization_review import freeze

PROMPT = '''你是匿名答案的来源核查员。检查每个独立义务，保留对象、时间基准、完成状态、否定与上限。答案按A1、A2编号；来源包括要求所依据的原文和回答实际看到的检索片段。不要因一个参考页没有某事实就忽略其他支持它的来源。输出JSON，只有checks和extra_unsupported两项。checks每项只含id、status、answer_ids、reason，id为义务id，status为present/missing/contradicted/ambiguous之一，answer_ids只能列已提供的A编号。present或contradicted须列出实际相关句子编号；missing时为空列表。extra_unsupported只列含有来源无法支持之新增事实的A编号。不要重抄引文、不要改写成答案没有的句子。
逐义务判断，不以一个数字正确代表整条合格；来源要求而答案否定时为contradicted。语义等同即可，不要求机械照抄；问题已明确给定的前提不用重复。若答案明说某条件，不得再声称缺失该条件。拒答后追加虚构金额仍须指出。正确拒答不是因为没提供无依据的事实而不合格。仅按给定材料判断，不主张现实政策效力。不给总分，只给证据化结论。'''


def validate(content, answer_ids, required_ids):
    v=json.loads(content)
    if set(v)!={'checks','extra_unsupported'} or not isinstance(v['checks'],list) or not isinstance(v['extra_unsupported'],list):raise ValueError('schema')
    if len(v['checks'])!=len(required_ids) or {c['id'] for c in v['checks']}!=set(required_ids):raise ValueError('coverage')
    for c in v['checks']:
        if set(c)!={'id','status','answer_ids','reason'} or c['status'] not in ('present','missing','contradicted','ambiguous'):raise ValueError('check schema')
        if not isinstance(c['answer_ids'],list) or any(x not in answer_ids for x in c['answer_ids']):raise ValueError('unknown answer pointer')
        if c['status'] in ('present','contradicted') and not c['answer_ids']:raise ValueError('unsupported verdict')
        if c['status']=='missing' and c['answer_ids']:raise ValueError('missing with pointer')
    if any(x not in answer_ids for x in v['extra_unsupported']):raise ValueError('unknown extra pointer')
    return v


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','report']);p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--cases',type=Path,required=True);a=p.parse_args();root=a.root;name=a.name
    cases={c['qid']:c for c in json.loads(a.cases.read_text())};assessed=json.loads((root/f'{name}-assessed.json').read_text())
    if a.action=='prepare':
        jobs=[];key=[];ordered=list(assessed);random.Random(131637).shuffle(ordered)
        for row in ordered:
            if not row['valid']:continue
            c=cases[row['qid']];body={'question':c['question'],'required_source':c['fixed_context'],'retrieved_source':row['context'],'answer':{f'A{i+1}':s['text'] for i,s in enumerate(row['answer']['sentences'])},'obligations':[{k:r[k] for k in ('id','criterion','support')} for r in c['obligations']]}
            jid=f'PTR-{len(jobs):03d}';jobs.append({'qid':jid,'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(body,ensure_ascii=False)}]});key.append({'job':jid,'qid':row['qid'],'arm':row['arm']})
        path=root/f'{name}-pointer-jobs.json';write_new(path,jobs);write_new(root/f'{name}-pointer-key.json',key);freeze(path,Path(__file__).resolve().parents[1]);f=path.with_suffix('.freeze.json');x=json.loads(f.read_text());x['hashes'].update({str(p.resolve()):sha(p) for p in (Path(__file__),a.cases,root/f'{name}-assessed.json')});f.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'jobs':len(jobs)}));return
    jobs={j['qid']:json.loads(j['messages'][1]['content']) for j in json.loads((root/f'{name}-pointer-jobs.json').read_text())};keys={k['job']:k for k in json.loads((root/f'{name}-pointer-key.json').read_text())};verdict={};invalid=[]
    rows=[json.loads(l) for l in (root/f'{name}-pointer-results.jsonl').read_text().splitlines()]
    if len(rows)!=len(keys) or {r['qid'] for r in rows}!=set(keys):raise ValueError('coverage')
    for row in rows:
        k=keys[row['qid']];body=jobs[row['qid']]
        try:
            v=validate(row['response']['content'],body['answer'],[o['id'] for o in body['obligations']]);v['adequate']=not v['extra_unsupported'] and all(c['status']=='present' for c in v['checks']);v['schema_valid']=True
        except Exception as e:v={'adequate':None,'schema_valid':False,'error':str(e)};invalid.append(k)
        verdict[k['qid'],k['arm']]=v
    detail=[];metrics={}
    for row in assessed:
        v=verdict.get((row['qid'],row['arm']),{'adequate':False,'schema_valid':False,'error':'invalid generation'})
        detail.append({'qid':row['qid'],'arm':row['arm'],'group':row['group'],'valid':row['valid'],'verdict':v,'latency_ms':row['response']['parent_observed_timings']['full_ms'],'usage':row['response']['usage']})
    for arm in sorted({r['arm'] for r in detail}):
        ds=[x for x in detail if x['arm']==arm];ms=[x['latency_ms'] for x in ds]
        metrics[arm]={'n':len(ds),'valid':sum(x['valid'] for x in ds),'adequate':sum(x['verdict']['adequate'] is True for x in ds),'unresolved':sum(x['verdict']['adequate'] is None for x in ds),'p50_ms':float(np.percentile(ms,50)),'p95_ms':float(np.percentile(ms,95)),'generation_usd':sum((x['usage']['input_tokens']*.3+x['usage']['output_tokens']*1.2)/1e6 for x in ds)}
    result={'metrics':metrics,'detail':detail,'invalid_reviews':invalid,'limitation':'Same-provider model review plus assistant-source obligations; no human gold. Unresolved evaluation outputs are not candidate losses. Transport timings exclude retrieval.'};write_new(root/f'{name}-pointer-comparison.json',result);print(json.dumps(metrics,indent=2))


if __name__=='__main__':main()
