"""Offline deadline analysis of frozen component results; never dispatches calls."""
import argparse, collections, hashlib, json, math
from pathlib import Path

CAP_MS = 4700

def measured(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0

def summarize(rows, cap_ms=CAP_MS):
    if not measured(cap_ms) or cap_ms <= 0:
        raise ValueError('cap must be finite and positive')
    result = {}
    for group in sorted({r['corpus']+'/'+r['arm'] for r in rows}):
        cohort = [r for r in rows if r['corpus']+'/'+r['arm'] == group]
        times = [r['pipeline_component_sum_ms'] for r in cohort if measured(r.get('pipeline_component_sum_ms'))]
        ontime = [r for r in cohort if measured(r.get('pipeline_component_sum_ms')) and r['pipeline_component_sum_ms'] <= cap_ms]
        quality = lambda r: r.get('valid') is True and (r.get('score') or {}).get('adequate') is True
        medians = {}
        def median(xs):
            xs=sorted(xs); n=len(xs)
            return (xs[(n-1)//2]+xs[n//2])/2 if n else None
        for field in ('preparation_ms','generation_wall_ms','canonicalization_ms'):
            medians[field] = median([r[field] for r in cohort if measured(r.get(field))])
        ttft = [r.get('generation',{}).get('timings',{}).get('ttft_ms') for r in cohort]
        ttft = [x for x in ttft if measured(x)]
        result[group] = {'scheduled':len(cohort),'timing_observed':len(times), 'timing_unknown':len(cohort)-len(times),
                         'within_cap':len(ontime),'over_cap':sum(t>cap_ms for t in times),
                         'valid_and_adequate':sum(quality(r) for r in cohort),
                         'valid_adequate_within_cap':sum(quality(r) for r in ontime),
                         'median_component_sum_ms':median(times),'component_medians_ms':medians,
                         'ttft_observed':len(ttft),'median_ttft_ms':median(ttft),'ttft_over_cap':sum(t>cap_ms for t in ttft)}
    return {'cap_ms':cap_ms,'groups':result,'paid_calls':0,
            'scope':'Historical warm component sum excludes queue/cold startup/network delivery; optimistic necessary check, not end-to-end SLA certification.',
            'unknown_policy':'Missing timings and missing/invalid quality scores cannot count as deadline-qualified success.',
            'runtime_cancellation_enforced':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--cap-ms',type=float,default=CAP_MS);a=p.parse_args()
    rows=[json.loads(l) for l in a.results.read_text().splitlines() if l.strip()]
    ids=[r['qid'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate results')
    result=summarize(rows,a.cap_ms);result['input_sha256']=hashlib.sha256(a.results.read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result,indent=2)+'\n')
