"""Build a private four-column report from explicit, complete source cohorts.

No inference, score recalculation, network, or selection by outcome. The config
lists every cohort and arm; each cohort includes every matching result row.
"""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.paths import _ensure_outside_repo

COLUMNS=['Question','Our answer','Score','Response time']

def read(path):
    p=Path(path)
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.suffix=='.jsonl' else json.loads(p.read_text())

def answer_text(response):
    raw=response['content']
    try:
        obj=json.loads(raw)
        if isinstance(obj,dict) and isinstance(obj.get('sentences'),list) and obj['sentences'] and all(isinstance(s,dict) and isinstance(s.get('text'),str) for s in obj['sentences']):
            return '\n'.join(s['text'] for s in obj['sentences'])
    except (ValueError,TypeError):pass
    return raw

def unique(rows,key):
    out={}
    for r in rows:
        k=key(r)
        if k in out:raise ValueError('duplicate source key')
        out[k]=r
    return out

def cohort(c):
    raw=read(c['results']);rows=[];evidence=[]
    if c['format']=='legacy':
        selected=[x for x in raw if x['arm']==c['arm'] and (not c.get('origin') or x['origin']==c['origin'])]
        scores=unique([x for x in read(c['scores']) if x['arm']==c['arm']],lambda x:x['qid'])
        for x in selected:
            qid=x['qid'];s=scores[qid]['scores'][c['arm']]
            score='; '.join(k+'='+str(s[k]) for k in ['correctness','support','relevance','completeness','citation_entailment','reference_complete','adequate'])
            score+='; '+s.get('issue','')
            response=x['raw_response'];text=answer_text(response)
            if x.get('answer') and '\n'.join(s['text'] for s in x['answer']['sentences'])!=text:raise ValueError('canonical answer changed raw prose')
            ms=response['parent_observed_timings']['full_ms']
            rows.append([qid+' | '+x['question'],text,score,str(ms)+' ms'])
            evidence.append({'qid':qid,'arm':c['arm'],'response_id':response.get('response_id'),'timing_field':'raw_response.parent_observed_timings.full_ms','timing_value':ms,'answer_sha256':hashlib.sha256(text.encode()).hexdigest(),'score_source':s,'events_perfcounter':response.get('events_perfcounter')})
    elif c['format']=='masked':
        cases=unique(read(c['cases']),lambda x:x['qid']);key=unique(read(c['key']),lambda x:x['mask'])
        scores={}
        for s in read(c['scores'])['rows']:
            k=key[s['mask']];t=(k['qid'],k['arm'])
            if t in scores:raise ValueError('duplicate score')
            scores[t]=s
        selected=[x for x in raw if x['qid'].endswith('-'+c['arm'])]
        if {x['qid'].rsplit('-',1)[0] for x in selected}!=set(cases):raise ValueError('cohort missing or extra outputs')
        for x in selected:
            qid=x['qid'].rsplit('-',1)[0];s=scores[qid,c['arm']];text=answer_text(x['response']);ms=x['response']['parent_observed_timings']['full_ms']
            score='assistant adequate='+str(s['adequate_on_conservative_review'])+'; excluded_primary='+str(s.get('exclude_primary',False))+'; '+s.get('notes','')
            if s.get('additional_concern'):score+='; concern: '+s['additional_concern']
            rows.append([qid+' | '+cases[qid]['question'],text,score,str(ms)+' ms'])
            evidence.append({'qid':qid,'arm':c['arm'],'response_id':x['response'].get('response_id'),'timing_field':'response.parent_observed_timings.full_ms','timing_value':ms,'answer_sha256':hashlib.sha256(text.encode()).hexdigest(),'score_source':s,'events_perfcounter':x['response'].get('events_perfcounter')})
    else:raise ValueError('unknown source format')
    if len(rows)!=c['expected_n'] or len({e['qid'] for e in evidence})!=len(rows):raise ValueError('unexpected or duplicated cohort count')
    return rows,evidence

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=_ensure_outside_repo(a.output,'Private case report');out.mkdir(parents=True,exist_ok=True);config=read(a.config)
    md=['# '+config['title'],'',config['explanation'],''];body=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>'+html.escape(config['title'])+'</title><style>body{font:16px/1.55 system-ui;margin:32px;color:#152234}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{border:1px solid #bbc7d3;padding:10px;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}th:nth-child(1){width:23%}th:nth-child(2){width:38%}th:nth-child(3){width:27%}th:nth-child(4){width:12%}th{background:#e9eff5}h2{margin-top:40px}pre{white-space:pre-wrap}</style><h1>'+html.escape(config['title'])+'</h1><pre>'+html.escape(config['explanation'])+'</pre>']
    receipt={'config_sha256':hashlib.sha256(a.config.read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'columns':COLUMNS,'cohorts':[]}
    for n,c in enumerate(config['cohorts'],1):
        rows,evidence=cohort(c);csvpath=out/f'{n:02d}-cases.csv'
        with csvpath.open('x',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f);w.writerow(COLUMNS);w.writerows(rows)
        # Parse export back; verifies exact answer/score/timing strings, not
        # just row count. CSV is the lossless four-column machine export.
        with csvpath.open(encoding='utf-8-sig',newline='') as f:back=list(csv.reader(f))
        if back!=[COLUMNS]+rows:raise ValueError('CSV round trip mismatch')
        md+=['## '+c['title'],'',c['setup'],'','| '+' | '.join(COLUMNS)+' |','|---|---|---|---|']
        body+=['<section><h2>'+html.escape(c['title'])+'</h2><p>'+html.escape(c['setup'])+'</p><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in COLUMNS)+'</tr></thead><tbody>']
        for row in rows:
            body+=['<tr>'+''.join('<td>'+html.escape(x)+'</td>' for x in row)+'</tr>']
            md+=['| '+' | '.join(html.escape(x).replace('|','&#124;').replace('\n','<br>') for x in row)+' |']
        body+=['</tbody></table></section>'];md+=['']
        sources={k:{'path':c[k],'sha256':hashlib.sha256(Path(c[k]).read_bytes()).hexdigest()} for k in ['results','scores','cases','key'] if k in c}
        receipt['cohorts'].append({'title':c['title'],'n':len(rows),'sources':sources,'records':evidence,'csv_sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest()})
    body+=['</html>']
    for name,text in [('report.html','\n'.join(body)),('report.md','\n'.join(md)),('verification.json',json.dumps(receipt,ensure_ascii=False,indent=2))]:
        with (out/name).open('x',encoding='utf-8') as f:f.write(text)
    print(json.dumps({'cohorts':len(receipt['cohorts']),'rows':sum(c['n'] for c in receipt['cohorts']),'columns':COLUMNS,'csv_round_trip_verified':True,'output':str(out)}))

if __name__=='__main__':main()
