"""Summarize paired assistant adjudications separately from raw model review."""
import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.paths import _ensure_outside_repo


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--name',default='replication');p.add_argument('--candidate',default='C8U');a=p.parse_args();root=_ensure_outside_repo(a.root,'Private report')
    assessed=json.loads((root/f'{a.name}-assessed.json').read_text());masked=json.loads((root/'assistant-adjudication-masked.json').read_text())['rows'];key={k['mask']:k for k in json.loads((root/f'{a.name}-blind-audit-private-key.json').read_text())};cases={c['qid']:c for c in json.loads((root/f'{a.name}-cases.json').read_text())};rates=json.loads(a.manifest.read_text())['models'];scores={};metrics={}
    excluded=sorted({row['qid'] for row in masked if row.get('exclude_primary')})
    cases={qid:c for qid,c in cases.items() if qid not in excluded}
    for row in masked:scores[row['qid'],key[row['mask']]['arm']]=row
    for arm in ('C1',a.candidate):
        rows=[r for r in assessed if r['arm']==arm];review=[scores[r['qid'],arm] for r in rows if r['qid'] not in excluded];times=[r['response']['parent_observed_timings']['full_ms'] for r in rows];cost=Decimal(0)
        for r in rows:
            rate=rates[r['response']['requested_model']];u=r['response']['usage'];cost+=(Decimal(u['input_tokens'])*Decimal(str(rate['input_per_1m']))+Decimal(u['output_tokens'])*Decimal(str(rate['output_per_1m'])))/1000000
        metrics[arm]={'n':len(rows),'primary_n':len(review),'valid':sum(r['valid'] for r in rows),'assistant_conservative_adequate':sum(r['adequate_on_conservative_review'] for r in review),'error_axes':dict(Counter(k for r in review for k,v in r['axes'].items() if v)),'additional_concerns':sum(bool(r['additional_concern']) for r in review),'p50_transport_ms':float(np.percentile(times,50)),'p95_transport_ms':float(np.percentile(times,95)),'generation_usd':str(cost)}
    families=sorted({c['group'] for c in cases.values()});deltas=[];pairs=[]
    for qid in cases:
        delta=int(scores[qid,a.candidate]['adequate_on_conservative_review'])-int(scores[qid,'C1']['adequate_on_conservative_review']);pairs.append({'qid':qid,'group':cases[qid]['group'],'delta':delta})
    for group in families:deltas.append(float(np.mean([p['delta'] for p in pairs if p['group']==group])))
    group_sums=np.array([sum(p['delta'] for p in pairs if p['group']==g) for g in families])
    group_counts=np.array([sum(p['group']==g for p in pairs) for g in families])
    rng=np.random.default_rng(20261013);indices=rng.integers(0,len(families),size=(20000,len(families)));samples=group_sums[indices].sum(axis=1)/group_counts[indices].sum(axis=1)
    report={'excluded_primary':excluded,'metrics':metrics,'paired_wins':sum(p['delta']==1 for p in pairs),'paired_losses':sum(p['delta']==-1 for p in pairs),'adequacy_delta':float(np.mean([p['delta'] for p in pairs])),'unweighted_family_mean_delta':float(np.mean(deltas)),'source_family_bootstrap_95_percentile':np.percentile(samples,[2.5,97.5]).tolist(),'bootstrap_seed':20261013,'bootstrap_draws':20000,'families':len(families),'pairs':pairs,'limitations':['Assistant source annotations are not human gold.','Conservative clear errors and borderline concerns are separate.',f'Only {len(families)} source families; bootstrap interval is descriptive and has limited coverage guarantees.','Transport timings exclude retrieval and do not establish production p95.','Raw paired model review is separate and not a promotion score.','Quality excludes logged ambiguous cases; validity, latency and generation costs include all dispatched answers.','Corpus and related topics exposed; questions were frozen before responses.']}
    with (root/f'{a.name}-comparison.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!='pairs'},indent=2))


if __name__=='__main__':main()
