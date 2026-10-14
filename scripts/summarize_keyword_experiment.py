"""Read-only evaluation/report builder for the explicitly supplied local run."""
import argparse,collections,hashlib,html,json,math,random
from pathlib import Path
H=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();n=a.directory
 rows=[json.loads(s)for s in(n/'answers/results.jsonl').read_text().splitlines()];assert len(rows)==len(json.load(open(n/'answer-jobs.json'))),'run incomplete'
 by={}
 for r in rows:by.setdefault(r['case_id'],{})[r['arm']]=r
 def ok(r):return bool((r.get('score')or{}).get('adequate'))
 out=[]
 for corpus in ['all','niuhuang','guangming']:
  for arm in ['baseline','vocabulary','small_model']:
   rr=[r for r in rows if r['arm']==arm and(corpus=='all'or r['corpus']==corpus)];ts=sorted(r['pipeline_component_sum_ms']for r in rr)
   out.append(dict(corpus=corpus,arm=arm,n=len(rr),raw_pass=sum(map(ok,rr)),unscored=sum(r.get('score')is None for r in rr),mechanically_valid=sum(r['valid']for r in rr),raw_gains=[r['case_id']for r in rr if ok(r)and not ok(by[r['case_id']]['baseline'])],raw_losses=[r['case_id']for r in rr if r.get('score')is not None and not ok(r)and ok(by[r['case_id']]['baseline'])],unscored_comparisons=[r['case_id']for r in rr if r.get('score')is None],p50_ms=ts[math.ceil(.5*len(ts))-1],p95_ms=ts[math.ceil(.95*len(ts))-1],max_ms=ts[-1]))
 (n/'summary.json').write_text(json.dumps(out,indent=2))
 masked=[];lineage={}
 for r in rows:
  rid='K-'+H([r['qid'],'keyword-review'])[:10];lineage[rid]=r['qid'];masked.append(dict(review_id=rid,question=r['question'],selected_sources=r['context'],answer=r['answer'],raw_if_invalid=None if r['answer']else r['generation']['content']))
 random.Random(1412).shuffle(masked);(n/'masked-review.json').write_text(json.dumps(masked,ensure_ascii=False,indent=2));(n/'private-review-lineage.json').write_text(json.dumps(lineage,indent=2))
 esc=lambda x:html.escape(str(x));body=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Keyword hypothesis pilot</title><style>body{font:16px system-ui;margin:32px;color:#172c37;line-height:1.5}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{border:1px solid #b8c9d0;padding:12px;vertical-align:top;overflow-wrap:anywhere}th:first-child{width:24%}th:nth-child(2){width:52%}pre{white-space:pre-wrap}details{margin:10px 0}</style><h1>Keyword hypotheses: controlled pilot</h1><p>20 exposed original questions,10 per domain; fresh current-route generation in every arm. Historical composite records are not the comparator. Raw judge scores require source review. Response time is measured serial critical-path component sum including keyword expansion, not a contiguous live request; cold initialization and uncached query embeddings are excluded.</p><p><a href="documentation.md">Methods and findings</a> · <a href="source-review.md">Masked source review</a> · <a href="summary.json">Metrics</a></p><table><tr><th>Question</th><th>Answer</th><th>Score</th><th>Response time</th></tr>']
 for cid,g in sorted(by.items()):
  for arm in ['baseline','vocabulary','small_model']:
   r=g[arm];answer='\n'.join(s.get('text',str(s))for s in(r['answer']or{}).get('sentences',[]))or r['generation']['content'];body.append('<tr><td><b>'+esc(cid+' / '+arm)+'</b><p>'+esc(r['question'])+'</p><small>'+esc(r['cohort'])+'</small></td><td>'+esc(answer)+'<details><summary>Quotations and source evidence</summary><pre>'+esc(json.dumps({'answer':r['answer'],'selected_sources':r['context']},ensure_ascii=False,indent=2))+'</pre></details><details><summary>Retrieval hypotheses (not facts)</summary>'+esc(r['trace']['hypotheses'])+'</details></td><td>'+('Unscored: preflight blocked'if r.get('score')is None else'1 / 1'if ok(r)else'0 / 1')+'<br><small>Raw model judge; valid='+str(r['valid'])+'</small><details><summary>Judge rationale</summary>'+esc(json.dumps(r.get('score'),ensure_ascii=False))+'</details></td><td>'+format(r['pipeline_component_sum_ms']/1000,'.3f')+' s<br><small>Expansion '+format(r['expansion_wall_ms']/1000,'.3f')+' s</small></td></tr>')
 body.append('</table></html>');s=''.join(body);assert s.count('<tr>')==61 and s.count('<td>')==240;(n/'report.html').write_text(s);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
