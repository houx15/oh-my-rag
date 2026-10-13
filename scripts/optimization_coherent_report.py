"""Private four-column report for one deterministic, opt-in candidate.

No inference. Replays route selection independently of scores and requires a
saved result with the exact selected context for every original case.
"""
import argparse,csv,hashlib,html,json,math
from pathlib import Path
from newdomain.coherent_candidate_v2 import select as select_v2
from newdomain.coherent_candidate import select
from newdomain.ordered_context import from_retrieval
from newdomain.paths import _ensure_outside_repo

COLUMNS=['Question','Our answer','Score','Response time']
AXES=['correctness','support','relevance','completeness']
def read(path):return json.loads(Path(path).read_text())
def rows(path):return [json.loads(x)for x in Path(path).read_text().splitlines()]
def indexed(path):
    rs=rows(path);out={r['qid']:r for r in rs}
    if len(out)!=len(rs):raise ValueError('duplicate case ID')
    return out

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def score_text(record):
    s=record['score']
    if s is None:return '评分缺失；保留在分母中'
    return ('通过' if s['adequate'] else '未通过')+'；'+ ' / '.join(str(s[k])+'/2' for k in AXES)+'（正确性/证据支持/相关性/完整性）；引文支持='+str(s['citation_entailment'])+'；覆盖完整='+str(s['reference_complete'])+'。'+s.get('issue','')
def percentile(values,p):
    values=sorted(values)
    return values[math.ceil(p*len(values))-1] if values else None

def build(config, output):
    out=_ensure_outside_repo(Path(output),'Private coherent report');out.mkdir(exist_ok=False)
    c=read(config);base=Path(c['baseline']);typed=Path(c['typed']);counts=Path(c['counts'])
    cases=read(base/'cases-prepared.json');gens=indexed(base/'generation-results.jsonl');reviews=indexed(base/'review-results.jsonl');nh=indexed(typed/'results.jsonl');gm=indexed(counts/'results.jsonl');aggregates=read(counts/'aggregate.json') if (counts/'aggregate.json').exists() else read(c['aggregate'])
    fresh=indexed(c["fresh_results"]) if c.get("fresh_results") else None
    fresh_sources={r["id"]:r["text"]for r in read(c["fresh_corpus_records"])}if fresh else {}
    if fresh is not None and set(fresh)!={x["qid"]for x in cases}:raise ValueError("fresh coverage incomplete")
    records=[];selected_counts=set();regressions=[];current_regressions=[]
    for case in cases:
        q=case['qid'];corpus=case['corpus'];g=gens[q]
        if corpus=='regression':
            regressions.append({'case':case,'generation':g,'review':reviews[q]})
            if fresh:current_regressions.append({'case':case,'generation':fresh[q],'review':{'score':fresh[q]['score']}})
            continue
        baseline_context=from_retrieval(case['prepared']['retrieval']['results'],g['context']) if corpus=='guangming' else g['context']
        route=select_v2(corpus,case['question'],baseline_context,aggregates,fresh_sources)if fresh else select(corpus,case['question'],baseline_context,aggregates)
        if fresh:
            chosen=fresh[q];score=chosen['score'];source=Path(c['fresh_results']);timing='本轮路由至答案验证；不含冻结上游检索与评分';ms=chosen['generation_ms']
            if route['route']=='gm-c1-catalogue-counts':selected_counts.add(q)
        elif route['route']=='nh-focused-typed-v2':chosen=nh[q];score=chosen['score'];source=typed/'results.jsonl';timing='生成阶段；不含检索与评分';ms=chosen['generation_ms']
        elif route['route']=='gm-c1-catalogue-counts':chosen=gm[q];score=chosen['score'];source=counts/'results.jsonl';timing='生成阶段；不含预先计算、检索与评分';ms=chosen['generation_ms'];selected_counts.add(q)
        else:chosen=g;score=reviews[q]['score'];source=base/'generation-results.jsonl';timing='原始检索至答案处理完成；不含评分';ms=g['full_ms']
        if chosen['question']!=case['question'] or chosen['context']!=route['context']:raise ValueError('saved result does not match question/route/context: '+q)
        answer=chosen.get('answer');text='\n'.join(s['text']for s in answer.get('sentences',[])) if isinstance(answer,dict) else ''
        if score and score['adequate'] and not chosen['valid']:raise ValueError('invalid answer counted as pass')
        display=('【未通过输出验证】\n' if not chosen['valid'] else '')+text if text else '未交付有效答案'
        records.append({'qid':q,'corpus':corpus,'origin':case['origin'],'question':case['question'],'answer':text,'answer_display':display,'score':score,'mechanically_valid':chosen['valid'],'ms':ms,'timing_scope':timing,'route':route['route'],'source_file':str(source),'answer_sha256':hashlib.sha256(text.encode()).hexdigest(),'reused_saved_result':not bool(fresh)})
    if selected_counts!=set(gm):raise ValueError('counting cohort mismatch')
    if len(records)!=645 or len({r['qid']for r in records})!=645:raise ValueError('original cohort incomplete')
    summaries=[]
    for corpus in ['guangming','niuhuang']:
        rr=[r for r in records if r['corpus']==corpus];by_origin={}
        for origin in sorted({r['origin']for r in rr}):
            subset=[r for r in rr if r['origin']==origin];by_origin[origin]={'n':len(subset),'pass':sum(bool(r['score'] and r['score']['adequate'])for r in subset)}
        timings={scope:{'n':len(z),'p50_ms':percentile(z,.5),'p95_ms':percentile(z,.95)} for scope in sorted({r['timing_scope']for r in rr}) if (z:=[r['ms']for r in rr if r['timing_scope']==scope])}
        summaries.append({'corpus':corpus,'n':len(rr),'pass':sum(bool(r['score']and r['score']['adequate'])for r in rr),'invalid':sum(not r['mechanically_valid']for r in rr),'unscored':sum(r['score'] is None for r in rr),'by_origin':by_origin,'timings_by_scope':timings})
        with (out/(corpus+'-full.csv')).open('w',encoding='utf-8-sig',newline='')as f:
            w=csv.writer(f);w.writerow(COLUMNS);w.writerows([[r['question'],r['answer_display'],score_text(r),str(r['ms'])+' ms；'+r['timing_scope']]for r in rr])
    e=html.escape
    def table(rr):
        s='<div class="scroll"><table><colgroup><col style="width:22%"><col style="width:44%"><col style="width:23%"><col style="width:11%"></colgroup><thead><tr>'+''.join('<th>'+x+'</th>'for x in COLUMNS)+'</tr></thead><tbody>'
        for r in rr:
            score=r['score'];passed=bool(score and score['adequate']);badge='通过' if passed else '未通过' if score else '评分缺失'
            s+='<tr data-case="'+e(r['qid'])+'"><td><small>'+e(r['origin'])+'</small><div class="question">'+e(r['question'])+'</div></td><td class="answer">'+e(r['answer_display'])+'</td><td><b class="'+('pass'if passed else'fail')+'">'+badge+'</b><details><summary>评分依据</summary>'+e(score_text(r))+'</details></td><td><b>'+format(r['ms']/1000,'.3f')+' s</b><details><summary>计时范围</summary>'+e(r['timing_scope'])+'<br>'+str(r['ms'])+' ms；复用该次原始记录</details></td></tr>'
        return s+'</tbody></table></div>'
    css='body{margin:0;background:#f6f7fb;color:#172439;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.page{max-width:1240px;margin:auto;padding:48px 28px}h1{font-size:36px;line-height:1.2;margin:10px 0 18px}h2{margin-top:38px}.eyebrow{letter-spacing:2px;color:#467367;font-size:12px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:28px 0}.card{background:white;padding:24px;border:1px solid #dfe6ea;border-radius:14px}.big{font-size:40px;font-weight:700}.note,small{color:#526274;font-size:13px}.scroll{overflow:auto;border:1px solid #dfe6ea;border-radius:10px;background:white}table{width:100%;min-width:900px;border-collapse:collapse;table-layout:fixed}th{text-align:left;background:#eaf0f3;padding:14px}td{padding:16px;vertical-align:top;border-top:1px solid #e2e8ee;overflow-wrap:anywhere}.answer,.question{white-space:pre-wrap}.pass{color:#14684e}.fail{color:#a42b34}details{font-size:13px;margin-top:10px}summary{cursor:pointer;color:#405c79}.full>summary{font-size:17px;font-weight:600;padding:14px 0}section{margin-bottom:28px}@media(max-width:700px){.page{padding:24px 14px}.cards{grid-template-columns:1fr}h1{font-size:28px}}'
    parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>知识问答系统 · 当前候选实测</title><style>'+css+'</style></head><body><main class="page"><div class="eyebrow">RAG · ORIGINAL QUESTIONS</div><h1>知识问答系统 · 当前候选实测</h1><p>同一套明确路由：牛黄采用聚焦回答与严格边界格式；光明保留 C1，仅清单计数问题加入可复算统计。</p><div class="cards">']
    for summary in summaries:
        corpus=summary['corpus'];name='光明' if corpus=='guangming' else'牛黄';live=summary['by_origin']['真实用户提问'if corpus=='guangming'else'live']
        parts.append('<div class="card"><strong>'+name+'</strong><div class="big">'+str(live['pass'])+' / '+str(live['n'])+'</div><p>原始用户提问通过 · '+format(100*live['pass']/live['n'],'.1f')+'%</p><p class="note">全部已筛选问题：'+str(summary['pass'])+'/'+str(summary['n'])+' 通过；输出验证失败 '+str(summary['invalid'])+' 条。</p></div>')
    parts+=['</div><p class="note">这是已暴露开发数据上的候选结果，未部署，也不是全新留出集。按预先明确的路由复用各实验的全部适用结果，没有逐题挑选高分答案；尚未进行此组合的全流程重跑或独立盲评。两组计时范围不同，不汇总或跨组比较 P95。</p><details><summary>覆盖、评分与未解决问题</summary><p>共645条：光明113条原始用户题＋217条模拟题；牛黄205条原始现场题＋110条评测题。隐私排除项保持排除；牛黄另合并16条完全重复题。20条历史合同回归结果单独保存在附录，未在本轮重跑。主评分为 deepseek-flash，四项语义分均需满分且引用、完整性与格式检查通过；模型评分不等于人工金标准，失败不删除。131个机构字段和一条平台总量陈述因隐私过滤缺失，未恢复；缺失对话、转写歧义和参考答案争议仍待处理。</p></details>']
    for summary in summaries:
        corpus=summary['corpus'];rr=[r for r in records if r['corpus']==corpus];live=[r for r in rr if r['origin']in('live','真实用户提问')];sample=sorted(live,key=lambda r:hashlib.sha256(('coherent-report:'+r['qid']).encode()).hexdigest())[:8]
        parts+=['<section><h2>'+('光明'if corpus=='guangming'else'牛黄')+'</h2><p>'+e('；'.join(origin+' '+str(v['pass'])+'/'+str(v['n'])+' 通过'for origin,v in summary['by_origin'].items()))+'</p>',table(sample),'<p class="note">示例按固定哈希顺序选取，不依据得分挑选。全部结果如下。</p><details class="full"><summary>查看全部 '+str(len(rr))+' 条</summary>',table(rr),'</details><details><summary>按计时范围分别查看延迟</summary>']
        for scope,t in summary['timings_by_scope'].items():parts.append('<p>'+e(scope)+'：n='+str(t['n'])+'，P50 '+format(t['p50_ms']/1000,'.3f')+'s，P95 '+format(t['p95_ms']/1000,'.3f')+'s。</p>')
        parts+=['</details></section>']
    historical=[]
    for item in regressions:
        case=item['case'];g=item['generation'];answer=g.get('answer');text='\n'.join(x['text']for x in answer.get('sentences',[])) if isinstance(answer,dict) else ''
        historical.append({'qid':case['qid'],'origin':'历史合同回归；未重跑','question':case['question'],'answer_display':(('【未通过输出验证】\n'if not g['valid']else'')+text) if text else '未交付有效答案','score':item['review']['score'],'ms':g['full_ms'],'timing_scope':'历史原始记录；非当前候选重跑'})
    failures=[r['qid']for r in historical if not(r['score']or{}).get('adequate')]
    parts+=['<section><h2>历史回归检查 · 单独核算</h2><p>首版665条 = 本页645条语料问题 + 以下20条合同回归。没有删除任何语料问题；历史回归19/20通过，未通过：'+e('、'.join(failures))+'。这些历史结果未作为当前候选的新回归验证。</p><details class="full"><summary>查看全部20条历史回归及原始失败</summary>',table(historical),'</details></section>']
    if fresh:
        current=[]
        for item in current_regressions:
            case=item['case'];g=item['generation'];text='\n'.join(x['text']for x in (g.get('answer')or{}).get('sentences',[]))
            current.append({'qid':'CURRENT:'+case['qid'],'origin':'本轮固定上下文合同检查','question':case['question'],'answer_display':(('【未通过输出验证】\n'if not g['valid']else'')+text)if text else'未交付有效答案','score':g['score'],'ms':g['generation_ms'],'timing_scope':'本轮固定上下文至答案验证；不含评分'})
        passed=sum(bool((r['score']or{}).get('adequate'))for r in current)
        parts+=['<section><h2>本轮合同检查 · 单独核算</h2><p>相同20条固定上下文检查重新生成并评分：'+str(passed)+'/20通过。这是所列合同子集，不代表完整生产安全验证。</p><details class="full"><summary>查看本轮20条检查</summary>',table(current),'</details></section>']
        rendered=''.join(parts).replace('复用该次原始记录','该次实际记录').replace('同一套明确路由：牛黄采用聚焦回答与严格边界格式；光明保留 C1，仅清单计数问题加入可复算统计。','同一套明确路由：牛黄采用聚焦回答、严格边界格式与引用段号提示；光明保留 C1，清单计数优先，其次按成果名称连接详细证据。').replace('按预先明确的路由复用各实验的全部适用结果，没有逐题挑选高分答案；尚未进行此组合的全流程重跑或独立盲评。两组计时范围不同，不汇总或跨组比较 P95。','本轮全部答案和主评分重新生成；上游检索复用冻结结果，不是重新嵌入检索或新的留出测试。没有逐题挑选高分答案；本配置尚未经过独立盲评。').replace('20条历史合同回归结果单独保存在附录，未在本轮重跑。','20条历史合同结果与本轮相同20条的重新评测结果分开呈现。')
        parts=[rendered]
    if c.get('interrupted_run'):
        stopped=Path(c['interrupted_run']);status=read(stopped/'stop-reconciliation.json')
        notice='<section><h2>后续统一配置重跑中断 · 不替换上述完整结果</h2><p>DeepSeek 返回 HTTP402，后续重跑仅完成321/665条评分，保存324条生成结果；3条待续评分，341条尚未开始。没有重试。以上主表仍为上一次完整结果，不据此不完整样本宣布总体提升。上游检索复用冻结结果。累计保守记账$39.77140635/$200，其中本次失败请求保守预留结算$1.8903168。账户问题需在提供商侧处理。</p><p>桥接重复实验：4题各重复3次，两组为6/12与12/12；引用地址提示定向试验：9/30→14/30，6增1退。均为已暴露问题的开发实验。40条预选来源诊断已完成，仍不是人工金标准。</p><p><a href="developer-appendix/interrupted-coverage.json">查看全部665条执行状态</a> · <a href="developer-appendix/interrupted-reconciliation.json">查看中断与账本核对</a></p></section>'
        if status["completed"]!=321 or status["expected"]!=665 or status["status"]!="blocked_provider_http402":raise ValueError("interruption notice needs updated verified values")
        parts[0]=parts[0].replace('<div class="cards">',notice+'<div class="cards">',1)
    parts+=['<p class="note">回答、分数与计时均来自保存的实际输出。原始来源、路由验证及限制见本地开发者附录；未上传外部网站。</p></main></body></html>']
    (out/'report.html').write_text(''.join(parts));(out/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(out/'summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2));appendix=out/'developer-appendix';appendix.mkdir();(appendix/'historical-regressions.json').write_text(json.dumps(regressions,ensure_ascii=False));(appendix/'configuration.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
    inputs=[base/'cases-prepared.json',base/'generation-results.jsonl',base/'review-results.jsonl',typed/'results.jsonl',counts/'results.jsonl',Path(c['aggregate']),Path(__file__),Path(__file__).parents[1]/'newdomain/coherent_candidate.py',Path(__file__).parents[1]/'newdomain/catalogue_counts.py']
    receipt={'source_hashes':{str(p):digest(p)for p in inputs},'report_sha256':digest(out/'report.html'),'records_sha256':digest(out/'records.json'),'columns':COLUMNS,'route_counts':{route:sum(r['route']==route for r in records)for route in sorted({r['route']for r in records})},'question_context_score_custody_verified':True,'paid_calls':0,'generalization':'exposed-development only; composite replay, not fresh end-to-end confirmation'}
    if fresh:
        receipt['fresh_results_sha256']=digest(c['fresh_results']);receipt['fresh_corpus_sha256']=digest(c['fresh_corpus_records']);receipt['generalization']='fresh generation and scoring with frozen upstream retrieval; exposed questions, not held out';receipt['source_hashes'][str(Path(__file__).parents[1]/'newdomain/coherent_candidate_v2.py')]=digest(Path(__file__).parents[1]/'newdomain/coherent_candidate_v2.py')
        (appendix/'current-contract-regressions.json').write_text(json.dumps(current_regressions,ensure_ascii=False,indent=2))
    if c.get('interrupted_run'):
        for source,destination in [('coverage.json','interrupted-coverage.json'),('stop-reconciliation.json','interrupted-reconciliation.json')]:
            (appendix/destination).write_bytes((stopped/source).read_bytes())
            receipt['source_hashes'][str(stopped/source)]=digest(stopped/source)
        receipt['incomplete_candidate_excluded_from_headlines']=True
    (out/'verification.json').write_text(json.dumps(receipt,indent=2));return summaries

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.config,a.output),ensure_ascii=False))
