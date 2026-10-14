"""Audit saved keyword results without retrieval changes or provider access."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.keyword_marginals import analyze

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directory', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    inputs = [args.directory / 'inference.json', args.directory / 'answers/results.jsonl']
    originals = json.loads(inputs[0].read_text())
    rows = {r['qid']: r for r in map(json.loads, inputs[1].read_text().splitlines())}
    records = []
    for original in originals:
        key = original['case_id']
        pair = {a: rows[key + '/' + a] for a in ['vocabulary', 'small_model']}
        data = analyze(original['baseline_context'], pair['vocabulary']['trace'], pair['small_model']['trace'])
        data.update(case_id=key, question=original['question'], corpus=original['corpus'], cohort=original['cohort'],
                    expansion_wall_ms=pair['small_model']['expansion_wall_ms'])
        records.append(data)
    payload = {'measurement': 'Record identity/rank only, not semantic relevance, novel facts or accuracy.',
               'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, 'records': records}
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print('Audited', len(records), 'original questions; no provider calls')

if __name__ == '__main__':
    main()
