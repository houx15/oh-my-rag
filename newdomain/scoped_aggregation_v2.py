"""Opt-in source-row operations; no world-total or contemporary validity claims."""
import re

def evidence(question, aggregates):
    if '成果' not in question or any(x in question for x in ('上线','实时','全市所有','全国所有')):
        return {}, {'applied':False,'reason':'outside source-row scope'}
    mode = 'mode' if ('应用领域' in question and any(x in question for x in ('最集中','最多','占比最高','最大'))) else None
    category_compare = '生命' in question and '材料' in question and any(x in question for x in ('多多少','差多少','相差','比较','哪个多'))
    alias = '光明实验' in question and any(x in question for x in ('多少','几项','数量'))
    if not (mode or category_compare or alias):return {}, {'applied':False,'reason':'no supported operator'}
    contexts={};traces={}
    for doc,a in aggregates.items():
        if a['record_count']<=0:continue
        scope='以下为来源清单逐行计算结果，不是原文引文，不代表机构全部成果或实时上线数。'
        if mode:
            field='应用领域';counts=a['dimensions'].get(field,{})
            if not counts:continue
            n=max(counts.values());winners=sorted(k for k,v in counts.items()if v==n)
            lines=[scope,'统计分母：'+str(a['record_count'])+'条来源记录；字段：完整应用领域字符串；缺失'+str(a['missing'][field])+'条。',
                   ('已知字段中最多：'if len(winners)==1 else'已知字段中并列最高：')+'；'.join(winners)+'；各'+str(n)+'条；各占全部来源行'+format(100*n/a['record_count'],'.2f')+'%。']
            if a['missing'][field]:lines.append('有未标注行，最高仅指已知分类，不推测缺失行归属。')
            trace={'operation':'mode','field':field,'winners':winners,'value':n,'denominator':a['record_count']}
        elif category_compare:
            counts=a['dimensions'].get('分类',{})
            if not all(k in counts for k in ('生命类','材料类')):continue
            left,right=counts['生命类'],counts['材料类']
            lines=[scope,f'生命类={left}条；材料类={right}条；生命类减材料类={left-right}条。分类缺失{a["missing"]["分类"]}条。']
            trace={'operation':'subtract','operands':[left,right],'result':left-right,'unit':'source rows'}
        else:
            matches=[(k,v)for k,v in a['dimensions'].get('单位名称',{}).items()if '光明实验室' in k]
            if len(matches)!=1:continue
            name,n=matches[0];lines=[scope,'口语“光明实验”实体未确定；如果指“'+name+'”，清单记有'+str(n)+'条；不能把其他机构替代为该机构。'];trace={'operation':'conditional_entity_count','source_entity':name,'value':n}
        rid='CALC:'+doc+':scoped-operation';contexts[rid]='\n'.join(lines);traces[rid]={**trace,'source_provenance':a['provenance']}
    return contexts,{'applied':bool(contexts),'operations':traces}
