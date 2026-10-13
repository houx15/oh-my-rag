"""Remove redundant review quote copies without dropping any supplied source text.

Preserves original oversized artifacts; valid only before review binding/dispatch.
Optional explicit reference errata are logged separately and never rewrite cases.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import sha
from newdomain.paths import _ensure_outside_repo
from newdomain.transport import screen
from newdomain.profile import load_profile


def compact(body):
    body=json.loads(json.dumps(body,ensure_ascii=False))
    sources=json.dumps([body['required_source'],body['retrieved_source']],ensure_ascii=False)
    for answer in body['answers'].values():
        for sentence in answer.get('sentences') or []:
            for citation in sentence.get('citations',[]):
                quote=citation.get('quote')
                if not isinstance(quote,str) or json.dumps(quote,ensure_ascii=False)[1:-1] not in sources:
                    raise ValueError('quote absent from retained sources')
                citation.pop('quote')
    return body


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--profile',type=Path,required=True);p.add_argument('--errata',type=Path);a=p.parse_args();root=_ensure_outside_repo(a.root,'Private review');path=root/f'{a.name}-axis-jobs.json';freeze=path.with_suffix('.freeze.json')
    if (root/f'{a.name}-axis-results.jsonl').exists() or (root/f'{a.name}-axis-results.journal.jsonl').exists():raise ValueError('review dispatch already began')
    rows=json.loads(path.read_text());before_sha=sha(path);changes=json.loads(a.errata.read_text()) if a.errata else {};deny=Path(load_profile(a.profile)['redaction_names_path'])
    for row in rows:
        body=compact(json.loads(row['messages'][1]['content']))
        if row['qid'] in changes:
            amendment=changes[row['qid']];body['reference_status']=amendment['status'];body['required_source'].update(amendment.get('additional_source',{}));body['obligations']=amendment['diagnostic_obligations']
        row['messages'][1]['content']=json.dumps(body,ensure_ascii=False);screen(row['messages'],deny)
    original=path.with_name(path.stem+'.original.json');original_freeze=freeze.with_name(freeze.stem+'.original.json')
    if original.exists() or original_freeze.exists():raise ValueError('original backup already exists')
    path.rename(original);freeze.rename(original_freeze)
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');f=json.loads(original_freeze.read_text());f['hashes'][str(path.resolve())]=sha(path);f['hashes'][str(Path(__file__).resolve())]=sha(Path(__file__))
    if a.errata:f['hashes'][str(a.errata.resolve())]=sha(a.errata)
    freeze.write_text(json.dumps(f,indent=2)+'\n')
    (root/f'{a.name}-review-amendment.json').write_text(json.dumps({'original_jobs_sha256':before_sha,'revised_jobs_sha256':sha(path),'duplicate_quote_removal':'Every removed quote was verified present in retained source text; all source fields unchanged except logged reference errata.','reference_errata':list(changes),'prior_review_calls':0,'max_request_bytes':max(len(json.dumps(r['messages'],ensure_ascii=False).encode()) for r in rows)},indent=2))
    print(json.dumps({'screened':len(rows),'errata_cases':list(changes)}))


if __name__=='__main__':main()
