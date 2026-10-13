"""Isolated qualifier-prompt and adjacent-page retrieval ablations."""
import argparse
import json
import random
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain import candidate
from newdomain.experiment import sha, write_new
from newdomain.paths import _ensure_outside_repo
from optimization_review import freeze, REVIEW_PROMPT

QUALIFIER_INSTRUCTION = ('最终核对：所述支持是否仍绑定原文的对象、实施期间、完成或投产状态？'
 '金额是否保留基数、比例、单项/年度上限及否定或例外？不要只把限制藏在引用里。'
 '只保留会改变本题结论的条件，已由问题明确给出的前提无需重复；不要增加无关条款。'
 '资料不足时限定不足范围，拒答后不得追加推测事实。数字推导须保留单位并应用上限。'
 '保持原有最多3句、每句160字和证据JSON约束，不输出核对过程。')


def neighbors(index, selected):
    """Same eight-chunk cap, replacing low-ranked chunks with anchor neighbors."""
    if not selected:return selected
    anchor=selected[0]
    try:page=int(anchor['locator'])
    except (ValueError,TypeError):return selected
    adjacent=[]
    for delta in (1,-1):
        options=[c for c in index.chunks if c['doc_id']==anchor['doc_id'] and str(c['locator'])==str(page+delta)]
        if options:adjacent.append(min(options,key=lambda c:c['start']))
    chosen=[];seen=set()
    for c in selected[:6]+adjacent+selected[6:]:
        if c['id'] not in seen:chosen.append(c);seen.add(c['id'])
        if len(chosen)==8:break
    return chosen


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','assess'])
    p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True)
    p.add_argument('--questions',type=Path);p.add_argument('--corpus',type=Path)
    p.add_argument('--cases',type=Path);p.add_argument('--arms',nargs='+',choices=['C1','C4Q','C4N'],default=['C1','C4Q','C4N'])
    a=p.parse_args();root=_ensure_outside_repo(a.root,'Private ablation');repo=Path(__file__).resolve().parents[1]
    if a.action=='prepare':
        cases=json.loads(a.questions.read_text());index=candidate.create_index(a.corpus)
        if any(set(c)!={'qid','question','group','origin'} for c in cases):raise ValueError('inference question fields only')
        jobs=[];metadata=[];rng=random.Random(20261013)
        for c in cases:
            start=time.perf_counter();selected=index.retrieval(c['question'])['results'];retrieval_ms=(time.perf_counter()-start)*1000
            arms=list(a.arms);rng.shuffle(arms)
            for arm in arms:
                chosen=neighbors(index,selected) if arm=='C4N' else selected
                messages=candidate.build_messages(c['question'],chosen)
                if arm=='C4Q':messages[0]['content']+=QUALIFIER_INSTRUCTION
                if len(json.dumps(messages,ensure_ascii=False).encode())>candidate.MAX_REQUEST_BYTES:raise ValueError('unchanged request cap exceeded')
                qid=f'{c["qid"]}-{arm}';jobs.append({'qid':qid,'messages':messages})
                metadata.append({'job':qid,'qid':c['qid'],'arm':arm,'context':index.contexts_map(chosen),'retrieval_ms':retrieval_ms,'group':c['group']})
        path=root/f'{a.name}-jobs.json';write_new(path,jobs);write_new(root/f'{a.name}-metadata.json',metadata);freeze(path,repo)
        f=path.with_suffix('.freeze.json');payload=json.loads(f.read_text());payload['hashes'].update({str(x.resolve()):sha(x) for x in (a.questions,a.corpus,Path(__file__),root/f'{a.name}-metadata.json')});f.write_text(json.dumps(payload,indent=2)+'\n')
        print(json.dumps({'jobs':len(jobs),'arms':a.arms}));return
    metadata={m['job']:m for m in json.loads((root/f'{a.name}-metadata.json').read_text())}
    cases={c['qid']:c for c in json.loads(a.cases.read_text())}
    rows=[json.loads(l) for l in (root/f'{a.name}-results.jsonl').read_text().splitlines()]
    if {r['qid'] for r in rows}!=set(metadata) or len(rows)!=len(metadata):raise ValueError('incomplete generation')
    jobs=[];assessed=[];key=[]
    for r in rows:
        m=metadata[r['qid']];response,canon=candidate.canonicalize(r['response'],m['context']);validation=candidate.validate(response,m['context'])
        answer=validation.get('answer') or (json.loads(response['content']) if canon.get('ok') else None)
        valid=bool(canon.get('ok') and validation.get('ok'))
        assessed.append(dict(m,valid=valid,validation=validation,answer=answer,response=r['response']))
        if not valid:continue
        c=cases[m['qid']];text='\n'.join(s['text'] for s in answer['sentences']);jid=f'ANON-{len(jobs):04d}'
        payload={'question':c['question'],'source':c['fixed_context'],'answer':text}
        jobs.append({'qid':jid,'messages':[{'role':'system','content':REVIEW_PROMPT},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]});key.append({'job':jid,'qid':m['qid'],'arm':m['arm']})
    write_new(root/f'{a.name}-assessed.json',assessed);write_new(root/f'{a.name}-review-key.json',key)
    path=root/f'{a.name}-review-jobs.json';write_new(path,jobs);freeze(path,repo)
    print(json.dumps({'generation':len(rows),'valid':sum(x['valid'] for x in assessed),'review_jobs':len(jobs)}))


if __name__=='__main__':main()
