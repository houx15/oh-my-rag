"""Arm-masked paired-source diagnostic review; never substitutes for human gold."""
import argparse
import json
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import sha, write_new
from newdomain.paths import _ensure_outside_repo
from optimization_review import freeze

AXES = ('missing_qualifier', 'unsupported_assertion', 'false_refusal', 'premise_error', 'numeric_error')
PROMPT = '''依据问题明确前提与给定来源，分别核查两个匿名答案，勿根据长度或措辞偏好排名。两个答案可能相同或都错。来源包括问题依据与实际检索内容，不能只读参考页。逐一核查各项义务；只要求回答本题所问，问题明确给定的前提无须重复。未知不能视为真或假；明确为假的条件不得说仅未知。正确条件分支不是拒答，附带无关的缺依据话术单独说明，只有拒绝本可回答的核心问题才算false_refusal。政策上限不等于实际到账。仅按给定来源，勿主张现实政策效力。
以下精确协议话术不是新增业务事实，不得计入unsupported_assertion：“本次资料未包含回答该问题所需的依据。”“以上为资料记载的转述，不构成投资或医疗建议。”但若它导致核心问题被无理由拒答，仍计false_refusal。
输出JSON仅含reviews数组，每个答案一项，字段严格为answer_id、obligations、missing_qualifier、unsupported_assertion、false_refusal、premise_error、numeric_error、notes。obligations是每个R编号到present/missing/contradicted/ambiguous的映射；五个错误字段为布尔值；notes为简短中文说明，指出真实句子与来源，不能虚构缺失条件。信息不足以裁决时义务标ambiguous，不要自动判错误。'''


def validate(content, answer_ids, obligation_ids):
    data=json.loads(content)
    if set(data)!={'reviews'} or not isinstance(data['reviews'],list):raise ValueError('schema')
    if len(data['reviews'])!=len(answer_ids) or {r['answer_id'] for r in data['reviews']}!=set(answer_ids):raise ValueError('answer coverage')
    for row in data['reviews']:
        if set(row)!={'answer_id','obligations','notes',*AXES}:raise ValueError('review schema')
        if not isinstance(row['notes'],str) or any(type(row[a]) is not bool for a in AXES):raise ValueError('field types')
        if not isinstance(row['obligations'],dict) or set(row['obligations'])!=set(obligation_ids):raise ValueError('obligation coverage')
        if any(v not in ('present','missing','contradicted','ambiguous') for v in row['obligations'].values()):raise ValueError('obligation status')
    return data['reviews']


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','report']);p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=_ensure_outside_repo(a.root,'Private review')
    cases=json.loads((root/f'{a.name}-cases.json').read_text())
    if a.action=='prepare':
        rows=json.loads((root/f'{a.name}-assessed.json').read_text());jobs=[];keys=[];rng=random.Random(131646)
        for case in cases:
            pair=[r for r in rows if r['qid']==case['qid']];rng.shuffle(pair);answers={};sources={}
            for i,row in enumerate(pair):
                aid=f'Answer-{i+1}';answers[aid]={'valid':row['valid'],'sentences':row['answer']['sentences'] if row['answer'] else None};sources.update(row['context']);keys.append({'job':case['qid'],'answer_id':aid,'arm':row['arm']})
            body={'question':case['question'],'required_source':case['fixed_context'],'retrieved_source':sources,'obligations':case['obligations'],'answers':answers}
            jobs.append({'qid':case['qid'],'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(body,ensure_ascii=False)}]})
        path=root/f'{a.name}-axis-jobs.json';write_new(path,jobs);write_new(root/f'{a.name}-axis-key.json',keys);freeze(path,Path(__file__).resolve().parents[1]);fp=path.with_suffix('.freeze.json');f=json.loads(fp.read_text());f['hashes'].update({str(x.resolve()):sha(x) for x in (Path(__file__),root/f'{a.name}-cases.json',root/f'{a.name}-assessed.json')});fp.write_text(json.dumps(f,indent=2)+'\n');print(json.dumps({'jobs':len(jobs),'answers':len(keys)}));return
    key={(k['job'],k['answer_id']):k['arm'] for k in json.loads((root/f'{a.name}-axis-key.json').read_text())};lookup={c['qid']:c for c in cases};details=[]
    for line in (root/f'{a.name}-axis-results.jsonl').read_text().splitlines():
        row=json.loads(line);qid=row['qid']
        try:
            reviews=validate(row['response']['content'],[aid for job,aid in key if job==qid],[o['id'] for o in lookup[qid]['obligations']])
            for review in reviews:details.append(dict(review,qid=qid,arm=key[qid,review['answer_id']],schema_valid=True))
        except (ValueError,KeyError,TypeError) as exc:details.append({'qid':qid,'schema_valid':False,'error':str(exc)})
    write_new(root/f'{a.name}-axis-review.json',{'detail':details,'completed_questions':len({d['qid'] for d in details}),'expected_questions':len(cases),'limitation':'Paired arm-masked fresh-context same-provider diagnostic review, not independent human gold. Joint presentation can induce comparison bias. Incomplete coverage is unresolved.'});print(json.dumps({'completed_questions':len({d['qid'] for d in details}),'expected_questions':len(cases)}))


if __name__=='__main__':main()
