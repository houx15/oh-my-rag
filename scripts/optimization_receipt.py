"""Reconcile private continuous-experiment outputs without provider dispatch."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from newdomain.generation import _reconcile_resume
from newdomain.journal import DispatchJournal
from newdomain.paths import _ensure_outside_repo


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--baseline-cumulative', type=Decimal, required=True)
    a = p.parse_args()
    root = _ensure_outside_repo(a.root, 'Private receipt')
    manifest = json.loads(a.manifest.read_text())
    runs = []; total = Decimal(0)
    for path in sorted(root.glob('*-results.jsonl')):
        header = json.loads(path.with_suffix('.header.json').read_text())
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        jobs_path = path.with_name(path.name.replace('-results.jsonl', '-jobs.json'))
        jobs = json.loads(jobs_path.read_text())
        if hashlib.sha256(jobs_path.read_bytes()).hexdigest() != header['jobs']:
            raise ValueError('jobs changed after dispatch')
        expected = {(j['qid'], 'BLIND') for j in jobs}
        if {(r['qid'], 'BLIND') for r in rows} != expected or len(rows) != len(jobs):
            raise ValueError('incomplete or duplicated run')
        model = rows[0]['response']['requested_model']
        with DispatchJournal(path.with_suffix('.journal.jsonl')) as journal:
            _reconcile_resume(journal, path, expected, model)
        rate = manifest['models'][model]; cost = Decimal(0)
        for row in rows:
            response = row['response']
            if response['actual_model'] != model or response['finish_reason'] != 'stop' or not response['stream_done']:
                raise ValueError('incomplete or unexpected provider output')
            usage = response['usage']
            cost += (Decimal(usage['input_tokens']) * Decimal(str(rate['input_per_1m'])) + Decimal(usage['output_tokens']) * Decimal(str(rate['output_per_1m']))) / 1000000
        total += cost
        runs.append({'file':path.name,'n':len(rows),'model':model,'usd':str(cost),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'journal_reconciled':True})
    ledgers = [json.loads((a.manifest.parent / f'ledger.{stage}.json').read_text()) for stage in ('dev','final')]
    if any(x['totals']['open_reservations'] for x in ledgers):
        raise ValueError('outstanding reservations; wait for completion')
    prior = Decimal(str(manifest['prior_spend_usd']))
    cumulative = prior + sum(Decimal(str(x['totals']['charged_cost_usd'])) for x in ledgers)
    delta = cumulative - a.baseline_cumulative
    if abs(delta-total) > Decimal('0.00000001'):
        raise ValueError(f'ledger/output mismatch: {delta} versus {total}')
    historical = []
    for row in manifest['prior_runs']:
        path=Path(row['path']); actual=hashlib.sha256(path.read_bytes()).hexdigest()
        historical.append({'path':str(path),'matches_manifest':actual==row['sha256']})
    receipt={'runs':runs,'provider_calls':sum(x['n'] for x in runs),'continuous_cost_usd':str(total),'cumulative_cost_usd':str(cumulative),'ledger_delta_usd':str(delta),'open_reservations':0,'prior_ledger_hashes':historical,'limitation':'Pinned conservative tariffs, not an invoice. Derived replays and local routing are not counted as provider calls.'}
    out=root/'continuous-accounting.json'
    with out.open('x') as f: json.dump(receipt,f,indent=2)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('runs','prior_ledger_hashes')},indent=2))


if __name__ == '__main__': main()
