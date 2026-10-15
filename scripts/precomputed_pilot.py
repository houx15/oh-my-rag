"""Offline source extraction and flat/graph comparison; private artifact paths only."""
import argparse,copy,hashlib,json,re,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.precomputed_evidence import answer,digest,validate

def build(sources):
    facts={}
    for rid,raw in sources.items():
        start=raw.index('第十四条') if '第十四条' in raw else 0
        stop=raw.index('第十五条') if '第十五条' in raw else raw.rfind('—')
        # Ignore source footer, preserve each complete enumerated clause.
        part=raw[start:stop];marks=list(re.finditer(r'（([一二三四五六七])）',part))
        for i,m in enumerate(marks):
            a=start+m.start();b=start+marks[i+1].start() if i+1<len(marks) else stop
            value=raw[a:b];footer=re.search(r'\n—\s*\d',value)
            if footer:b=a+footer.start()
            while b>a and raw[b-1].isspace():b-=1
            num='一二三四五六七'.index(m[1])+1
            facts['step'+str(num)]={'source_id':rid,'start':a,'end':b,'text':raw[a:b]}
        if '第十五条' in raw:
            a=raw.index('第十五条');b=raw.index('第十六条')
            while raw[b-1].isspace():b-=1
            facts['caps']={'source_id':rid,'start':a,'end':b,'text':raw[a:b]}
    steps=['step'+str(i) for i in range(1,8)]
    bundle={'source_hashes':{rid:digest(raw)for rid,raw in sources.items()},'facts':facts,'ordered_steps':steps,
            'next':dict(zip(steps,steps[1:])),'signing':'step6',
            'intent_facts':{'before_signing':steps[:5],'subsidy_start':['step7'],'subsidy_caps':['caps']},
            'scope':'Source-reviewed D01 procedure family, manually assigned intent semantics; source-derived development pilot only.'}
    validate(bundle,sources);return bundle

def run(pool_path,directory):
    jobs=json.loads(pool_path.read_text());j=next(x for x in jobs if x['case_id']=='GM:GM-349')
    sources={rid:j['candidate_records'][rid]for rid in ['D01:6:01','D01:7:01']}
    probes=json.loads((directory/'probes.json').read_text())
    t=time.perf_counter();bundle=build(sources);build_ms=(time.perf_counter()-t)*1000
    (directory/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    (directory/'bundle.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    results=[]
    for p in probes+[{'id':'GM:GM-349','question':j['question'],'expected':['step1','step2','step3','step4','step5','step7']}]:
        a=answer(p['question'],bundle,sources,'flat');b=answer(p['question'],bundle,sources,'graph')
        actual=[f['id']for f in a['facts']]
        results.append({**p,'flat':a,'graph':b,'parity':a==b,'expected_match':actual==p['expected'],'baseline_exact_fact_coverage':[fid for fid in p['expected']if bundle['facts'][fid]['text']in j['baseline'].get(bundle['facts'][fid]['source_id'],'')] if p['id']=='GM:GM-349'else None})
    # Exposed 68-case routing coverage only; no labels for newly routed cases.
    coverage=[]
    for q in jobs:
        a=answer(q['question'],bundle,sources,'flat');b=answer(q['question'],bundle,sources,'graph')
        coverage.append({'case_id':q['case_id'],'corpus':q['corpus'],'status':a['status'],'parity':a==b,'selected_facts':[f['id']for f in a['facts']]})
    times={}
    for mode in ['flat','graph']:
        ts=[]
        for _ in range(100):
            for p in probes:
                t=time.perf_counter_ns();answer(p['question'],bundle,sources,mode);ts.append((time.perf_counter_ns()-t)/1e6)
        ts.sort();times[mode]={'calls':len(ts),'p50_ms':statistics.median(ts),'p95_ms':ts[int(.95*(len(ts)-1))],'max_ms':max(ts)}
    report={'paid_calls':0,'source_extract_build_ms':build_ms,'source_review_time':'not measured; manual preparation excluded','warm_in_memory_local_timing':times,'probes':results,'coverage_68':coverage,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [pool_path,directory/'probes.json',Path(__file__),Path(__file__).resolve().parents[1]/'newdomain/precomputed_evidence.py']},'limits':['8 synthetic development probes + known GM349; no held-out answer quality claim.','Warm local lookup/render includes source hash and graph validation, excludes disk load, ingestion review and client delivery.','Both arms have identical prepared facts; graph storage alone is not an efficacy gain.','Router is narrow and heuristic; untested paraphrases or unsupported mixed intents may be misrouted.']}
    (directory/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'probe_passes':sum(r['expected_match']for r in results),'probes':len(results),'parity':all(r['parity']for r in results+coverage),'routed_68':[r for r in coverage if r['status']=='answered'],'times':times,'build_ms':build_ms},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pool',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);a=p.parse_args();run(a.pool,a.directory)
