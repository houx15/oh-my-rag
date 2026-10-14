"""Evidence-only floor arithmetic plan; does not expand retrieval triggers."""
import copy,re


def plan(question, context, source_records=None):
    if '科技金融大厦' not in question or not any(x in question for x in ('多少层','层数','几层')):return None
    found=[]
    for rid,text in context.items():
        # Require the building's section/title and explicit floor-range label.
        title=(source_records or {}).get(rid,{}).get('title','')
        if '科技金融大厦' not in text[:200]+title or '楼层层数' not in text:continue
        m=re.search(r'楼层层数\s*[：:]?\s*(-[1-9]\d*)F\s*[-—–~至]\s*([1-9]\d*)F',text)
        if not m:continue
        below=-int(m[1]);above=int(m[2])
        if below>20 or above>200 or any(x in text for x in ('跳层','缺层','不设','避讳')):continue
        found.append({'source':rid,'quote':m[0],'above':above,'below':below,'total':above+below,'convention':'将1F至最高层计为地上，负层计为地下，不计0F；按连续楼层编号推算，非实测建筑层数'})
    if len({(p['above'],p['below'])for p in found})!=1:return None
    return found[0]


def messages(original, question, context, source_records=None):
    p=plan(question,context,source_records)
    if p is None:return original,{'applied':False}
    out=copy.deepcopy(original)
    out[0]['content']+='\n已核对的楼层算术计划（仍须引用该原文，不能当作独立来源）：来源'+p['source']+'原文“'+p['quote']+'”；按连续编号且不计0F，地上'+str(p['above'])+'层，地下'+str(p['below'])+'层，合计'+str(p['total'])+'层。回答须说明这是该楼层范围的计数口径；不能把最高楼层号当含地下总层数，也不能把局部入驻名单当总楼层。'
    return out,{'applied':True,**p}
