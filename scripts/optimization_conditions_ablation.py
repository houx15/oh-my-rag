"""Prepare opt-in C10D/C14T frozen jobs; never dispatch providers."""
import argparse
import json
import random
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain import candidate
from newdomain.definitions import DefinitionSelector
from newdomain.conditions import augment
from newdomain.experiment import sha, write_new
from newdomain.paths import _ensure_outside_repo
from optimization_review import freeze


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--questions',type=Path,required=True);p.add_argument('--corpus',type=Path,required=True);a=p.parse_args()
    root=_ensure_outside_repo(a.root,'Private definitions experiment');repo=Path(__file__).resolve().parents[1]
    questions=json.loads(a.questions.read_text())
    if any(set(q)!={'qid','question','group','origin'} for q in questions):raise ValueError('inference fields only')
    index=candidate.create_index(a.corpus);started=time.perf_counter();selector=DefinitionSelector(index.chunks);build_ms=(time.perf_counter()-started)*1000
    jobs=[];metadata=[];rng=random.Random(20261015)
    for q in questions:
        started=time.perf_counter();selected=index.retrieval(q['question'])['results'];retrieval_ms=(time.perf_counter()-started)*1000
        started=time.perf_counter();expanded=selector.select(selected);selection_ms=(time.perf_counter()-started)*1000
        arms=['C14E','C14T'];rng.shuffle(arms)
        for arm in arms:
            chosen=expanded;messages=candidate.build_messages(q['question'],chosen)
            ledger=None
            messages,ledger=augment(q['question'],chosen)
            if arm=='C14E':
                messages[-1]['content']=messages[-1]['content'].rsplit('\n',1)[0]+'\n'+json.dumps({'method':'typed-source-conditions-v2','question_quantities':[],'conditions':[],'omitted_conditions':0,'eligibility_verified':False},ensure_ascii=False,separators=(',',':'))
            if len(json.dumps(messages,ensure_ascii=False).encode())>candidate.MAX_REQUEST_BYTES:raise ValueError('request cap')
            jid=q['qid']+'-'+arm;jobs.append({'qid':jid,'messages':messages})
            metadata.append({'job':jid,'qid':q['qid'],'arm':arm,'context':index.contexts_map(chosen),'typed_ledger':ledger,'retrieval_ms':retrieval_ms+selection_ms,'selection_ms':selection_ms,'group':q['group'],'added':[c['id'] for c in chosen if c['id'] not in {b['id'] for b in selected}],'displaced':[c['id'] for c in selected if c['id'] not in {b['id'] for b in chosen}]})
    write_new(root/f'{a.name}-metadata.json',metadata);write_new(root/f'{a.name}-selector.json',{'build_ms':build_ms,'definitions':{d:c['id'] for d,c in selector.definitions.items()},'ambiguous_documents':sorted(selector.ambiguous_documents),'method':'same top-anchor document only; one insertion within eight chunks'})
    path=root/f'{a.name}-jobs.json';write_new(path,jobs);freeze(path,repo);fp=path.with_suffix('.freeze.json');f=json.loads(fp.read_text());f['hashes'].update({str(x.resolve()):sha(x) for x in (Path(__file__),a.questions,a.corpus,root/f'{a.name}-metadata.json')});fp.write_text(json.dumps(f,indent=2)+'\n');print(json.dumps({'jobs':len(jobs),'live':False}))


if __name__=='__main__':main()
