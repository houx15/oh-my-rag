"""Prepare independent-context source review and arm-blinded calibration jobs."""
import argparse
import json
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import sha, write_new
from newdomain.paths import _ensure_outside_repo

SOURCE_PROMPT = '''Independently review the screened source for this question. You have no model answers or old reference. Return JSON only: {"required":[{"fact":"Chinese atomic obligation","source_key":"page key or question/absence","why_required":"short explanation"}],"scope_ambiguities":["..."],"answerable":true}. Include requested facts and material eligibility/time/cap constraints whose omission broadens the answer. Do not require every adjacent policy condition. Distinguish assumptions supplied in the question, derived arithmetic, and absence of records. At most 6 compact requirements. Screened OCR may be imperfect; do not claim human gold.'''
REVIEW_PROMPT = '''Evaluate the anonymous answer against the question and screened source, not another model's opinion. Return JSON only: {"material_omission":true/false,"contradiction":true/false,"unsupported_claim":true/false,"justified_abstention":true/false,"scope_ambiguity":true/false,"issues":["short Chinese issue with source key"]}. Preserve beneficiary, period, basis, cap and eligibility. A requirement explicitly given in the question need not be repeated verbatim; do flag an answer that broadens eligibility. Exact citations do not excuse omission in answer prose. Detect negated/reversed requirements, swapped beneficiaries, wrong numeric relations, and unsupported factual assertions AFTER a refusal. Do not penalize justified refusal for failing to provide absent records. Accept equivalent wording, not mere keyword presence. No chain of thought; brief evidence-based issues only.'''


def freeze(path, repo):
    hashes={str(path.resolve()):sha(path)}
    for p in [repo/'scripts/optimization_jobs.py',Path(__file__).resolve(),*sorted((repo/'newdomain').glob('*.py'))]:hashes[str(p)]=sha(p)
    write_new(path.with_suffix('.freeze.json'),{'hashes':hashes})


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--action',choices=['source','calibration'],required=True);a=p.parse_args()
    out=_ensure_outside_repo(a.output,'Private optimization');out.mkdir(exist_ok=True)
    annotations=json.loads((a.root/'repair-annotations.json').read_text())
    cases={c['qid']:c for c in json.loads((a.root/'final-judge-cases.json').read_text())}
    answers={(r['qid'],r['arm']):r for r in map(json.loads,(a.root/'final-final-results.jsonl').read_text().splitlines())}
    jobs=[];key=[];rng=random.Random(202610131519)
    for item in annotations['cases']:
        c=cases[item['qid']];payload={'question':c['question'],'source':c['fixed_context']}
        if a.action=='source':
            jobs.append({'qid':f'SOURCE-{len(jobs):03d}','messages':[{'role':'system','content':SOURCE_PROMPT},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]});key.append({'job':jobs[-1]['qid'],'qid':c['qid']})
        else:
            subjects=[]
            for arm in ('C1','C3B'):
                text='\n'.join(s['text'] for s in answers[c['qid'],arm]['answer']['sentences'])
                subjects.append((text,{'qid':c['qid'],'arm':arm,'kind':'original'}))
            for control in item['controls']+item.get('blindspot_controls',[]):
                subjects.append((control['text'],{'qid':c['qid'],'kind':'control','name':control['name'],'expected_flags':control.get('expected_flags'), 'reason':control.get('reason')}))
            rng.shuffle(subjects)
            for text,meta in subjects:
                jobid=f'BLIND-{len(jobs):03d}';body=dict(payload,answer=text)
                jobs.append({'qid':jobid,'messages':[{'role':'system','content':REVIEW_PROMPT},{'role':'user','content':json.dumps(body,ensure_ascii=False)}]});key.append(dict(meta,job=jobid))
    path=out/f'{a.action}-jobs.json';write_new(path,jobs);write_new(out/f'{a.action}-private-key.json',key)
    freeze(path,Path(__file__).resolve().parents[1]);print(json.dumps({'jobs':len(jobs),'action':a.action}))


if __name__=='__main__':main()
