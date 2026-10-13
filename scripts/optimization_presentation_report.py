"""Render an audience-facing private report from already verified case records.
No inference or scoring. Every selected answer comes from one fixed saved run.
"""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
from optimization_case_report import cohort, read, COLUMNS
from newdomain.paths import _ensure_outside_repo


def quantile(values, p):
    values=sorted(values);x=(len(values)-1)*p;i=int(x)
    return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(x-i)


def score_detail(s):
    labels={'correctness':'正确性','support':'证据支持','relevance':'相关性','completeness':'完整性'}
    return ' / '.join(labels[k]+': '+str(s[k])+'/2' for k in labels)+'；引文支持: '+str(s['citation_entailment'])+'；覆盖完整: '+str(s['reference_complete'])+'。'+s.get('issue','')


def score_cell(record):
    primary,secondary=record['primary'],record['secondary']
    a,b=primary['adequate'],secondary['adequate']
    label='通过' if a and b else '评审分歧' if a!=b else '未通过'
    css='pass' if a and b else 'mixed' if a!=b else 'fail'
    e=html.escape
    return '<span class="status '+css+'">'+label+'</span><div class="reviewers">评审一：'+('通过' if a else '未通过')+'<br>评审二：'+('通过' if b else '未通过')+'</div><details class="score-detail"><summary>评分依据</summary><p>评审一：'+e(score_detail(primary))+'</p><p>评审二：'+e(score_detail(secondary))+'</p></details>'


def table(rows):
    e=html.escape
    out=['<div class="table-wrap"><table><colgroup><col class="question-col"><col class="answer-col"><col class="score-col"><col class="time-col"></colgroup><thead><tr>'+''.join('<th scope="col">'+v+'</th>' for v in COLUMNS)+'</tr></thead><tbody>']
    for r in rows:
        out.append('<tr data-case="'+e(r['qid'],quote=True)+'"><td><span class="origin">'+e(r['origin'])+'</span><div class="question">'+e(r['question'])+'</div></td><td class="answer">'+e(r['answer'])+'</td><td>'+score_cell(r)+'</td><td class="time" data-ms="'+str(r['ms'])+'"><strong>'+format(r['ms']/1000,'.3f')+' s</strong><details><summary>原始值</summary>'+str(r['ms'])+' ms</details></td></tr>')
    return ''.join(out)+ '</tbody></table></div>'


def main():
    a=argparse.ArgumentParser();a.add_argument('--config',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    c=read(args.config);out=_ensure_outside_repo(args.output,'Private presentation report');out.mkdir(exist_ok=False)
    source=read(c['source_config']);all_data=[];sources={};sections=[]
    for section in c['sections']:
        data=[]
        for ix in section['cohort_indices']:
            config=source['cohorts'][ix];rows,evidence=cohort(config)
            for k in ('results','scores','independent','cases'):
                if k in config:sources[config[k]]=hashlib.sha256(Path(config[k]).read_bytes()).hexdigest()
            if config['format']=='legacy':
                other=read(section['independent']);sources[section['independent']]=hashlib.sha256(Path(section['independent']).read_bytes()).hexdigest()
            for row,ev in zip(rows,evidence):
                primary=ev['score_source']
                if config['format']=='legacy':secondary=other[ev['qid']][config['arm']]
                else:
                    oscore=ev['independent_score_source'];secondary=dict(oscore['scores'],adequate=oscore['adequate'])
                qid,question=row[0].split(' | ',1)
                r={'qid':qid,'question':question,'answer':row[1],'origin':section['origin_labels'][str(ix)],'primary':primary,'secondary':secondary,'ms':ev['timing_value'],'evidence':ev}
                assert hashlib.sha256(r['answer'].encode()).hexdigest()==ev['answer_sha256']
                data.append(r)
        lookup={r['qid']:r for r in data}
        if len(lookup)!=len(data):raise ValueError('duplicate case in main corpus')
        ids=section['sample_ids']
        if len(set(ids))!=len(ids) or not set(ids)<=set(lookup):raise ValueError('invalid representative sample')
        sample=[lookup[q] for q in ids]
        n=len(data);passed=sum(r['primary']['adequate'] and r['secondary']['adequate'] for r in data)
        summary={'name':section['name'],'n':n,'both_pass':passed,'both_pass_percent':100*passed/n,'p95_ms':quantile([r['ms'] for r in data],.95),'sample_ids':ids,'sample_selection_reason':section['selection_reason']}
        all_data.append({'summary':summary,'rows':data});sections.append((section,data,sample,summary))
        csvpath=out/(section['slug']+'-full.csv')
        with csvpath.open('x',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f);writer.writerow(COLUMNS)
            writer.writerows([[r['question'],r['answer'],'评审一: '+str(r['primary']['adequate'])+'; '+score_detail(r['primary'])+'\n评审二: '+str(r['secondary']['adequate'])+'; '+score_detail(r['secondary']),str(r['ms'])+' ms'] for r in data])
    e=html.escape
    css="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f6f8;color:#172b3a;font:16px/1.65 -apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}.page{max-width:1400px;margin:auto;padding:48px 40px 64px}header{max-width:1050px}.eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;color:#467166}h1{font-size:38px;line-height:1.2;margin:12px 0 20px;font-weight:750}header>p{font-size:18px;color:#415466;margin:0 0 26px}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:28px 0 20px}.metric{padding:24px 28px;border:1px solid #dce3e8;background:white;border-radius:12px}.metric-name{font-size:18px;font-weight:700}.numbers{display:flex;flex-wrap:wrap;gap:32px;margin:14px 0}.number{font-size:32px;line-height:1.2;font-weight:750;letter-spacing:-.02em}.number small{font-size:16px;font-weight:400;color:#5c6c78}.metric p{font-size:14px;color:#566977;margin:8px 0 0}.note{font-size:13px;color:#586775;line-height:1.7;max-width:1200px}.decision{border-left:3px solid #567d70;padding:8px 0 8px 16px;color:#344b56}section{margin-top:46px}h2{font-size:28px;margin:0 0 8px}section>.intro{margin:0 0 18px;color:#526472;max-width:1150px}.table-wrap{overflow-x:auto;background:white;border:1px solid #dce3e8;border-radius:10px}table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;line-height:1.6}th{font-size:12px;letter-spacing:.02em;text-align:left;background:#eaf0f3;padding:13px 16px;color:#365361}td{padding:18px 16px;vertical-align:top;border-top:1px solid #e4e9ec;overflow-wrap:anywhere}.question-col{width:25%}.answer-col{width:45%}.score-col{width:18%}.time-col{width:12%}.origin{display:inline-block;font-size:11px;background:#f0f3f5;color:#62727d;border-radius:4px;padding:2px 6px;margin-bottom:8px}.question{font-weight:600}.answer{white-space:pre-wrap}.status{display:inline-block;font-weight:700;border-radius:4px;padding:2px 7px;font-size:12px}.pass{color:#236549;background:#e6f2eb}.fail{color:#934437;background:#faebe7}.mixed{color:#88652b;background:#f8f0dc}.reviewers{font-size:12px;color:#647481;line-height:1.55;margin-top:8px}summary{cursor:pointer;color:#43697b}details.score-detail{font-size:12px;margin-top:8px}details.score-detail p{font-size:12px;line-height:1.5}.time strong{font-size:16px;white-space:nowrap}.time details{font-size:11px;margin-top:8px}.full{margin-top:18px}.full>summary{padding:14px 18px;background:#eaf0f3;border-radius:8px;font-weight:600}.full .table-wrap{margin-top:12px}.full>p{font-size:13px;color:#62727d}.sample-note{font-size:12px;color:#6c7984;margin:12px 0}.footer{font-size:12px;color:#778590;margin-top:36px;border-top:1px solid #dce3e8;padding-top:16px}@media(max-width:760px){.page{padding:28px 16px}h1{font-size:28px}.metrics{grid-template-columns:1fr}.metric{padding:20px}table{min-width:900px}.note{font-size:12px}section{margin-top:34px}}@media print{body{background:white}.page{padding:12px}details.full:not([open]){display:none}tr{break-inside:avoid}.metrics{break-inside:avoid}h2{break-after:avoid}}"""
    parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src &apos;none&apos;; style-src &apos;unsafe-inline&apos;"><title>'+e(c['title'])+'</title><style>'+css+'</style></head><body><main class="page"><header><div class="eyebrow">RAG · PERFORMANCE</div><h1>'+e(c['title'])+'</h1><p>'+e(c['lead'])+'</p></header><div class="metrics">']
    for sec,data,sample,summary in sections:
        parts.append('<div class="metric"><div class="metric-name">'+e(sec['name'])+'</div><div class="numbers"><div><div class="number">'+str(summary['both_pass'])+'<small> / '+str(summary['n'])+'</small></div><p>两位评审均通过 · '+format(summary['both_pass_percent'],'.1f')+'%</p></div><div><div class="number">'+format(summary['p95_ms']/1000,'.2f')+'<small> s</small></div><p>'+e(sec['latency_label'])+' · P95</p></div></div><p>'+e(sec['coverage'])+'</p></div>')
    parts+=['</div><p class="decision">'+e(c['usability'])+'</p><p class="note">'+e(c['short_note'])+'</p>']
    for sec,data,sample,summary in sections:
        parts+=['<section id="'+e(sec['slug'])+'"><h2>'+e(sec['name'])+'</h2><p class="intro">'+e(sec['intro'])+'</p>',table(sample),'<p class="sample-note">'+e(sec['selection_note'])+'</p><details class="full"><summary>查看全部 '+str(len(data))+' 条问答与评分</summary><p>按保存的测试顺序完整列出，包含未通过与评审分歧；概览指标按全量结果计算。</p>',table(data),'</details></section>']
    parts+=['<p class="footer">资料与回答保持原样。原始评分、来源与技术记录保存在随附开发者附录；本页不提供个人医疗或政策资格认定。</p></main></body></html>']
    (out/'report.html').write_text(''.join(parts))
    (out/'records.json').write_text(json.dumps(all_data,ensure_ascii=False,indent=2))
    receipt={'source_hashes':sources,'config_sha256':hashlib.sha256(args.config.read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'report_sha256':hashlib.sha256((out/'report.html').read_bytes()).hexdigest(),'columns':COLUMNS,'summaries':[x['summary'] for x in all_data],'paid_calls':0}
    (out/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps(receipt['summaries'],ensure_ascii=False))

if __name__=='__main__':main()
