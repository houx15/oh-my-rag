"""Create arm-masked assistant/source review packets; mapping remains private."""
import argparse
import json
import random
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--cases',type=Path,required=True);a=p.parse_args()
    root=a.root.resolve();repo=Path(__file__).resolve().parents[1]
    if root==repo or repo in root.parents:raise ValueError('private output outside repo required')
    cases=json.loads(a.cases.read_text());answers=json.loads((root/f'{a.name}-assessed.json').read_text());rng=random.Random(131701);packet=[];mapping=[]
    for case in cases:
        order=[r for r in answers if r['qid']==case['qid']];rng.shuffle(order);items=[]
        for row in order:
            mask=f'REVIEW-{len(mapping):03d}';mapping.append({'mask':mask,'qid':row['qid'],'arm':row['arm']})
            items.append({'mask':mask,'valid':row['valid'],'answer':row['answer']})
        packet.append({'qid':case['qid'],'question':case['question'],'obligations':case['obligations'],'required_source':case['fixed_context'],'answers':items})
    for suffix,data in [('blind-audit',packet),('blind-audit-private-key',mapping)]:
        with (root/f'{a.name}-{suffix}.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps({'questions':len(packet),'masked_answers':len(mapping),'status':'arm-masked assistant review; not fully independent human gold'}))


if __name__=='__main__':main()
