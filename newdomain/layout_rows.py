"""Conservative row association from screened local OCR geometry.

Only literal numeric F labels are paired. Ambiguous OCR (e.g. I6F), ambiguous
nearest neighbours and distant labels remain unpaired. No case/reference lookup.
"""
import re

def associate(observations, source_id, page):
    floors=[];labels=[]
    for i,o in enumerate(observations):
        t=o['text'].strip();box={k:float(o[k])for k in ('x','y','width','height')}
        if any(not 0<=v<=1 for v in box.values()):raise ValueError('normalized box required')
        item=dict(box,text=t,index=i,center=box['y']+box['height']/2)
        (floors if re.fullmatch(r'\d{1,3}(?:-\d{1,3})?F',t)else labels).append(item)
    paired=[]
    for f in floors:
        candidates=[o for o in labels if 0<=o['x']-(f['x']+f['width'])<=.13 and abs(o['center']-f['center'])<=.03 and len(o['text'])>=2]
        candidates.sort(key=lambda o:abs(o['center']-f['center']))
        if not candidates:continue
        if len(candidates)>1 and abs(candidates[1]['center']-f['center'])-abs(candidates[0]['center']-f['center'])<.01:continue
        o=candidates[0]
        if sum(abs(other['center']-o['center'])<=.03 and other['x']<o['x'] for other in floors)!=1:continue
        paired.append({'floor':f['text'],'label':o['text'],'source_id':source_id,'page':page,'observation_indices':[f['index'],o['index']],'boxes':[f,o]})
    return paired

def evidence(question, rows, document_title):
    q=re.sub(r'\s+','',question)
    if not re.search(r'哪|楼|层|位置|地址',q):return {},[]
    matched=[r for r in rows if re.sub(r'\s+','',r['label'])in q]
    if not matched:return {},[]
    source_ids={r['source_id']for r in matched}
    if len(source_ids)!=1:raise ValueError('multiple source diagrams need separate cards')
    rid='LAYOUT:'+matched[0]['source_id']
    text='图示布局对应关系（由本地OCR坐标配对得到，不是原文连续引文；未声明当前实时入驻情况）\n来源：'+document_title+'\n'+'\n'.join(r['label']+'：'+r['floor']+'（第'+str(r['page'])+'页）'for r in matched)
    return {rid:text},matched
