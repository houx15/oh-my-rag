"""Opt-in premise-uncertainty prompt ablation, independent of reference labels."""
import argparse
import json
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import sha,write_new
from optimization_review import freeze
from newdomain.candidate import MAX_REQUEST_BYTES

INSTRUCTION=('先区分问题明确提供的事实与尚未提供的事实。不得擅自假定购置地点、首次资格、证书类别、认定状态、申请记录等会改变结论的前提。'
 '缺少关键前提时按资料给出必要的条件分支，或明确需要补充哪项信息；不能把未知当满足或不满足，也不要对可作条件回答的问题全面拒答。'
 '政策上限、理论补贴和具体企业实际到账或审批结果必须严格区分：缺少主体或记录时不得把任何政策金额替报为到账额。'
 '保持原证据编号、最多3句和每句160字的JSON合同；固定话术也必须保留evidence键并置为空数组。')


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--baseline',required=True);p.add_argument('--name',required=True);a=p.parse_args();root=a.root
    base=json.loads((root/f'{a.baseline}-jobs.json').read_text());meta={m['job']:m for m in json.loads((root/f'{a.baseline}-metadata.json').read_text())};jobs=[];ms=[];rng=random.Random(131610)
    for job in base:
        if meta[job['qid']]['arm']!='C1':raise ValueError('baseline-only preparation required')
        variants=[]
        for arm in ('C1','C8U'):
            m=meta[job['qid']];jid=m['qid']+'-'+arm;messages=[dict(x) for x in job['messages']]
            if arm=='C8U':messages[0]['content']+=INSTRUCTION
            if len(json.dumps(messages,ensure_ascii=False).encode())>MAX_REQUEST_BYTES:raise ValueError('budget')
            variants.append(({'qid':jid,'messages':messages},dict(m,job=jid,arm=arm)))
        rng.shuffle(variants)
        for j,m in variants:jobs.append(j);ms.append(m)
    path=root/f'{a.name}-jobs.json';write_new(path,jobs);write_new(root/f'{a.name}-metadata.json',ms);freeze(path,Path(__file__).resolve().parents[1]);f=path.with_suffix('.freeze.json');v=json.loads(f.read_text());v['hashes'].update({str(p.resolve()):sha(p) for p in (Path(__file__),root/f'{a.name}-metadata.json',root/f'{a.baseline}-jobs.freeze.json')});f.write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({'jobs':len(jobs)}))


if __name__=='__main__':main()
