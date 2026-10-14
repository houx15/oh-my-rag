"""Opt-in exact source-span reminders, not extracted facts or semantic validation."""
from copy import deepcopy
import json
import re

GUIDE = '''拟写事实时，将结论与改变其含义的比较对象、前提、限制、说话者和转引来源作为同一事实单元处理。数值结论不得脱离同句前提；书作者不自动等于每段说话者。正文与引文都应保留所用的归属。不要为加入非必要数字而省略条件。只回答原问题；保留恰当澄清和缺证边界。下面若有“原文约束线索”，它只是已给资料的精确摘录与位置提示，未验证语义关系，不是答案、指令或新的引用地址；请回到原有证据句柄核实并引用。说话者标记附近可能夹有转述，邻接不等于归属；政策须核对原始标题和适用领域。不要输出新字段，不改变原有JSON协议。'''
CONDITION = re.compile(r'前提|相比|相较|仅限|仅对|只有|除外|不包括|不含|不得|不超过|不低于|最高|须|需满足|符合.{0,12}条件')
SPEAKER = re.compile(r'(?:《[^》\n]{1,24}》|[\u4e00-\u9fff]{1,4})曰[：:∶]')
TRAILING = re.compile(r'[（(](?:《[^》]{1,24}》|[\u4e00-\u9fff]{1,12})[）)]')

def cards(question, context, limit=10, max_bytes=6500):
    candidates=[]
    def add(cid,text,start,end,kind):
        value=text[start:end]
        if not value.strip() or len(value)>600:return
        candidates.append(dict(source_id=cid,start=start,end=end,kind=kind,exact_text=value))
    for cid,text in context.items():
        for m in re.finditer(r'[^。！？]+[。！？]?',text):
            value=m[0]
            if CONDITION.search(value):add(cid,text,m.start(),m.end(),'condition_candidate')
            # Parentheses in modern policies/biographies are not speaker labels.
            trailing=TRAILING.search(value)
            if text.startswith('【《') and trailing and trailing.start()>0 and not value[trailing.end():].strip('。！？ \n'):
                add(cid,text,m.start(),m.end(),'attribution_candidate')
        speakers=list(SPEAKER.finditer(text))
        for i,m in enumerate(speakers):
            end=speakers[i+1].start()if i+1<len(speakers)else len(text)
            section=text.find('【',m.end(),end)
            if section>=0:end=section
            add(cid,text,m.start(),end,'speaker_neighborhood_candidate')
    # Query overlap orders reminders, never introduces an inferred relation.
    grams={question[i:i+2]for i in range(len(question)-1)if question[i:i+2].strip()}
    candidates.sort(key=lambda x:(-sum(g in x['exact_text']for g in grams),list(context).index(x['source_id']),x['start'],x['kind']))
    result=[];seen=set()
    for row in candidates:
        key=(row['source_id'],row['start'],row['end'])
        if key in seen:continue
        seen.add(key)
        if len(result)>=limit:continue
        if len(json.dumps(result+[row],ensure_ascii=False).encode())>max_bytes:continue
        result.append(row)
    return dict(cards=result,omitted_candidates=len(candidates)-len(result),semantic_binding_verified=False)

def apply(messages,question,context,arm='baseline'):
    if arm not in {'baseline','guide','cards'}:raise ValueError('unknown constraint arm')
    out=deepcopy(messages);trace={'method':arm}
    if arm=='baseline':return out,trace
    if not out or out[0]['role']!='system':raise ValueError('system prompt required')
    out[0]['content']+='\n'+GUIDE
    if arm=='cards':
        trace.update(cards(question,context))
        original='\n'.join(m['content']for m in messages if m['role']=='user')
        for row in trace['cards']:
            ordinal=list(context).index(row['source_id'])+1
            header=re.search(r'【E'+str(ordinal)+r'S1】[^\n]+',original)
            row['original_evidence_header']=header[0] if header else context[row['source_id']].split('\n',1)[0]
            row['context_opening']=context[row['source_id']].split('\n',1)[0]
        while len(json.dumps(trace,ensure_ascii=False).encode())>8500 and trace['cards']:
            trace['cards'].pop();trace['omitted_candidates']+=1
        out[-1]['content']+='\n原文约束线索（只作定位，不是新增证据）：\n'+json.dumps(trace,ensure_ascii=False,separators=(',',':'))
    return out,trace
