"""Sequential, journaled frozen jobs for bounded optimization experiments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import ExperimentContext, sha
from newdomain.profile import load_profile, verify_profile
from newdomain.transport import chat, screen
from newdomain.journal import DispatchJournal
from newdomain.generation import _reconcile_resume, _verify_or_write_header
from newdomain.paths import _ensure_outside_repo


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--jobs', type=Path, required=True)
    p.add_argument('--freeze', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--budget-root', type=Path, required=True)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--stage', choices=['dev','final'], required=True)
    p.add_argument('--model', choices=['deepseek-flash','deepseek-v4-pro'], required=True)
    p.add_argument('--live', action='store_true')
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    output = _ensure_outside_repo(args.output, 'Private job output')
    frozen = json.loads(args.freeze.read_text())['hashes']
    required = [args.jobs.resolve(), Path(__file__).resolve()]
    for path in required:
        if str(path) not in frozen:
            raise ValueError('jobs and runner must be frozen')
    for path,h in frozen.items():
        if sha(path) != h:
            raise ValueError('frozen job input changed')
    jobs = json.loads(args.jobs.read_text())
    if not jobs or len({j['qid'] for j in jobs}) != len(jobs):
        raise ValueError('empty or duplicated jobs')
    paths = verify_profile(load_profile(args.profile), args.stage)
    for j in jobs:
        if set(j) != {'qid','messages'} or not isinstance(j['qid'],str) or '|' in j['qid']:
            raise ValueError('bad inference job schema')
        screen(j['messages'], paths['redaction_names_path'])
    if not args.live:
        print(json.dumps({'screened_jobs':len(jobs),'live':False}));return
    ctx = ExperimentContext(experiment_root=args.budget_root, manifest_path=paths['manifest_path'],
        redaction_names_path=paths['redaction_names_path'], stage=args.stage, expected_ledger_path=paths['ledger_path'])
    identity = {'jobs':sha(args.jobs),'freeze':sha(args.freeze),'model':args.model,'stage':args.stage,
                'code':{str(x):sha(x) for x in sorted((Path(__file__).resolve().parents[1]/'newdomain').glob('*.py'))}}
    journal_path = output.with_suffix('.journal.jsonl')
    with DispatchJournal(journal_path) as journal:
        _verify_or_write_header(output.with_suffix('.header.json'),identity,args.resume)
        if args.resume:
            _reconcile_resume(journal,output,{(j['qid'],'BLIND') for j in jobs},args.model)
        elif output.exists() or journal._entries:
            raise ValueError('existing run requires explicit resume')
        for j in jobs:
            prompt = hashlib.sha256(json.dumps(j['messages'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            if journal.check_resume(j['qid'],'BLIND',prompt,args.model)=='skip':continue
            journal.record_started(j['qid'],'BLIND',prompt,args.model)
            try:
                response = chat(ctx,j['messages'],model=args.model)
                if response.get('finish_reason')!='stop' or not response.get('stream_done'):
                    raise ValueError('incomplete model response')
                row={'qid':j['qid'],'arm':'BLIND','prompt_sha256':prompt,'response':response}
                line=json.dumps(row,ensure_ascii=False,sort_keys=True)
                with output.open('a',encoding='utf-8') as f:
                    f.write(line+'\n');f.flush();os.fsync(f.fileno())
                journal.record_terminal(j['qid'],'BLIND',prompt,args.model,True,result_sha256=hashlib.sha256(line.encode()).hexdigest())
                print(json.dumps({'completed':j['qid']}),flush=True)
            except BaseException as exc:
                journal.record_terminal(j['qid'],'BLIND',prompt,args.model,False,error=type(exc).__name__)
                raise


if __name__=='__main__':main()
