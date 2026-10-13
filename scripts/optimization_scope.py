"""Offline C9S preparation: preserve the question's explicit requested scope."""
import argparse
import json
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.candidate import MAX_REQUEST_BYTES
from newdomain.experiment import sha,write_new
from newdomain.paths import _ensure_outside_repo
from optimization_review import freeze

INSTRUCTION = ('先确定本题要求判断的范围，并忠实保留问题已经明确给出的事实、对象角色、期间和数值。'
 '问题仅问某一项或几项条件时，先回答这些条件是否满足；不要因为其他未问条件未知，就否定或拒绝这个局部结论。'
 '问题明确说其他条件符合时，在该假设下回答所问测算，不要声称已给出的年度、身份或状态没有说明。'
 '逐一对应比较对象及其角色，不能把参与换成主导、把修订换成制定、把某年度换成多年合计。'
 '局部符合不等于整体获批，规则测算不等于实际到账；如需提示这一边界，保持简短且不推翻已回答的局部结论。'
 '保持原JSON、证据及句数长度约束，不输出核对过程。')


def paired_jobs(base, metadata):
    lookup={m['job']:m for m in metadata}
    if len(lookup)!=len(metadata) or {j['qid'] for j in base}!=set(lookup):raise ValueError('baseline coverage')
    jobs=[];out=[];rng=random.Random(20261014)
    for job in base:
        m=lookup[job['qid']]
        if m['arm']!='C1':raise ValueError('C1-only baseline required')
        pair=[]
        for arm in ('C1','C9S'):
            messages=[dict(x) for x in job['messages']]
            if not messages or messages[0]['role']!='system':raise ValueError('system message required')
            if arm=='C9S':messages[0]['content']+=INSTRUCTION
            if len(json.dumps(messages,ensure_ascii=False).encode())>MAX_REQUEST_BYTES:raise ValueError('request cap')
            jid=m['qid']+'-'+arm;pair.append(({'qid':jid,'messages':messages},dict(m,job=jid,arm=arm)))
        rng.shuffle(pair)
        for j,m in pair:jobs.append(j);out.append(m)
    return jobs,out


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--baseline',required=True);p.add_argument('--name',required=True);a=p.parse_args();root=_ensure_outside_repo(a.root,'Private scope experiment')
    base=root/f'{a.baseline}-jobs.json';metadata=root/f'{a.baseline}-metadata.json';jobs,ms=paired_jobs(json.loads(base.read_text()),json.loads(metadata.read_text()));path=root/f'{a.name}-jobs.json';write_new(path,jobs);write_new(root/f'{a.name}-metadata.json',ms);freeze(path,Path(__file__).resolve().parents[1]);fp=path.with_suffix('.freeze.json');f=json.loads(fp.read_text());f['hashes'].update({str(x.resolve()):sha(x) for x in (Path(__file__),base,metadata,root/f'{a.name}-metadata.json')});fp.write_text(json.dumps(f,indent=2)+'\n');print(json.dumps({'jobs':len(jobs),'live':False}))


if __name__=='__main__':main()
