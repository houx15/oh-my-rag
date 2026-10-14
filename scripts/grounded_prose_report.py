"""One private four-column report with complete scheduled-case accounting."""
import argparse,csv,html,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.keyword_experiment import read,write,lines

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args();n=a.directory;jobs=read(n/'answer-jobs.json');results={r['qid']:r for r in lines(n/'answers/results.jsonl')};groups=defaultdict(list)
 started={r['key'].split('|')[0]for r in lines(n/'answers/calls.journal.jsonl')if r['status']=='started'}
 generated={r['qid']for r in lines(n/'answers/responses.jsonl')if r['kind']=='generation'}
 for j in jobs:
  groups[(j['arm'],'all')].append(j)
  if j['corpus']!='regression':groups[(j['arm'],'main_mixed_645')].append(j)
  groups[(j['arm'],j['corpus'])].append(j)
  groups[(j['arm'],j['corpus']+'/'+j['origin'])].append(j)
 metrics={}
 def quantile(vals,p):
  if not vals:return None
  vals=sorted(vals);i=(len(vals)-1)*p;lo=int(i);hi=min(lo+1,len(vals)-1);return vals[lo]+(vals[hi]-vals[lo])*(i-lo)
 for (arm,stratum),items in groups.items():
  rs=[results[j['qid']]for j in items if j['qid']in results];lat=[r['pipeline_component_sum_ms']/1000 for r in rs if 'pipeline_component_sum_ms'in r]
  metrics[arm+'/'+stratum]={'scheduled':len(items),'recorded':len(rs),'generation_completed':sum(j['qid']in generated for j in items),'review_completed':sum('review'in r for r in rs),'scored':sum(r.get('score')is not None for r in rs),'raw_passes':sum(bool((r.get('score')or{}).get('adequate'))for r in rs),'valid':sum(bool(r.get('valid'))for r in rs),'execution_failed':sum('execution_failure'in r for r in rs),'not_started':sum(j['qid']not in started and j['qid']not in results for j in items),'in_progress':sum(j['qid']in started and j['qid']not in results for j in items),'unscored_recorded':sum(r.get('score')is None for r in rs),'p50_seconds':quantile(lat,.5),'p95_seconds':quantile(lat,.95),'latency_samples':len(lat)}
 paired=[]
 for j in jobs:
  if j['arm']!='baseline':continue
  b=results.get(j['qid'],{});c=results.get(j['case_id']+'/candidate',{})
  if b.get('score')is not None and c.get('score')is not None:paired.append({'case_id':j['case_id'],'corpus':j['corpus'],'origin':j['origin'],'baseline':b['score']['adequate'],'candidate':c['score']['adequate']})
 summary={'metrics':metrics,'paired':{'scored_pairs':len(paired),'wins':sum(not x['baseline']and x['candidate']for x in paired),'losses':sum(x['baseline']and not x['candidate']for x in paired)},'generation_reused':0,'human_gold':False,'historically_exposed':True,'promotion':False}
 if(n/'answers/settlement.json').exists():summary['settlement']=read(n/'answers/settlement.json')
 write(n/'summary.json',summary);write(n/'paired-raw-results.json',paired)
 esc=lambda s:html.escape(str(s));parts=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>RAG full case report</title><style>body{font:16px system-ui;max-width:1400px;margin:32px auto;padding:0 20px;color:#17212b}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border:1px solid #ccd3dc;padding:12px;text-align:left;vertical-align:top}th{background:#eef3f8}td:nth-child(1){width:22%}td:nth-child(2){width:55%;white-space:pre-wrap}small{color:#546273}details{margin:12px 0}select{padding:8px}section{margin-bottom:36px}.fail{color:#922}</style><h1>RAG：完整问题与回答记录</h1>']
 complete=len(results)==len(jobs)
 parts.append('<p><strong>'+('运行记录已齐；请同时查看失败／未评分计数。'if complete else '运行中：以下是部分结果，不能据此判断完整性能。已记录 '+str(len(results))+' / '+str(len(jobs))+' 个计划输出。')+'</strong></p>')
 parts+=['<p>本报告保留所有计划问题及失败／未运行项。问题均有历史暴露，不是未见测试集；模型评分不是人工金标准。候选未推广。基线为Cycle10适配器加确定性词法融合，不是历史C1的精确重跑。回归集使用固定历史证据，其余问题本地重跑检索并使用缓存向量。</p>','<p>延迟：热检索／提示构建＋生成＋校验的阶段耗时之和；不含排队、评分、冷启动及未缓存向量请求。所有评分标准保持冻结。四列正文默认展示基线；可切换整套候选，绝不逐题挑最好答案。</p>','<label>回答版本 <select id="arm"><option value="baseline">基线（未推广候选）</option><option value="candidate">候选：普通正文＋完整条款</option></select></label>','<h2>完整分母与结果</h2><table><tr><th>版本／来源</th><th>原始评分通过／计划</th><th>有效／已评分／未运行</th><th>P50／P95 秒</th></tr>']
 for key,m in metrics.items():
  f=lambda v:'—'if v is None else f'{v:.3f}'
  parts.append('<tr><td>'+esc(key)+'</td><td>'+str(m['raw_passes'])+'/'+str(m['scheduled'])+'</td><td>'+f"{m['valid']} / {m['scored']} / {m['not_started']}"+'</td><td>'+f(m['p50_seconds'])+' / '+f(m['p95_seconds'])+'</td></tr>')
 parts+=['</table><p>配对得分变化：'+esc(summary['paired'])+'。失败与未评分并未被删除，也未改写为有效失败评分。</p>']
 if 'settlement'in summary:parts.append('<p>保守累计账本：'+esc(summary['settlement']['cumulative_conservative_usd'])+' / 200 USD；本阶段 '+esc(summary['settlement']['totals']['charged_cost_usd'])+'。此为保守计费上界记账，不是发票／汇率换算。</p>')
 csvrows=[]
 for arm in ['baseline','candidate']:
  parts.append('<div data-arm="'+arm+'"'+(' hidden'if arm=='candidate'else '')+'>')
  for corpus in ['guangming','niuhuang','regression']:
   subset=sorted((j for j in jobs if j['arm']==arm and j['corpus']==corpus),key=lambda j:j['case_id'])
   if not subset:continue
   parts.append('<section><h2>'+esc(corpus)+' · '+str(len(subset))+' questions</h2><table><tr><th>问题</th><th>回答</th><th>评分</th><th>延迟</th></tr>')
   for j in subset:
    r=results.get(j['qid'],{});answer=r.get('answer');text='\n'.join(s['text']for s in answer['sentences'])if answer and r.get('valid')else '未交付有效回答：'+str(r.get('execution_failure')or r.get('gate')or j.get('preparation_failure')or '尚未运行')
    score=r.get('score');grade=('通过'if score['adequate']else '未通过')+' · '+score.get('issue','')if score is not None else '未评分'
    latency=r.get('pipeline_component_sum_ms');lat='—'if latency is None else f'{latency/1000:.3f}s'
    parts.append('<tr><td>'+esc(j['question'])+'<br><small>'+esc(j['case_id']+' · '+j['origin'])+'</small></td><td>'+esc(text)+'</td><td>'+esc(grade)+'</td><td>'+lat+'</td></tr>')
    csvrows.append({'case_id':j['case_id'],'corpus':corpus,'origin':j['origin'],'arm':arm,'question':j['question'],'answer':text,'score':grade,'latency_seconds':lat})
   parts.append('</table></section>')
  parts.append('</div>')
 parts.append('<details><summary>审计与运行明细</summary><p>相邻文件：summary.json、roster-summary.json、paired-raw-results.json、answers/results.jsonl、answers/settlement.json。完整原始响应、引用、失败和账本保留在本地；不上传或发布。</p></details><script>document.querySelector("#arm").addEventListener("change",e=>document.querySelectorAll("[data-arm]").forEach(x=>x.hidden=x.dataset.arm!==e.target.value));</script></html>')
 (n/'report.html').write_text(''.join(parts))
 with(n/'cases.csv').open('w')as f:
  writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
 print(json.dumps({'baseline':metrics.get('baseline/all'),'candidate':metrics.get('candidate/all'),'paired':summary['paired']},indent=2))
if __name__=='__main__':main()
