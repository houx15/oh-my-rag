"""Expand catalogue hits into source evidence through exact corpus entity names.

No query rewriting, reference answers, fuzzy assertions or paid calls. This is a
small independent key-to-evidence bridge, not an M-RAG reproduction.
"""
import re


def compact(text):return re.sub(r'\s+','',text)

def bridge(question, results, corpus, limit=2):
    if type(limit) is not int or not 0<=limit<=2:raise ValueError('limit must be 0..2')
    old=list(results);query=compact(question)
    names={}
    for row in old:
        for name in re.findall(r'(?:成果名称|项目名称|产品名称)[：:]([^\n]{2,60})',row['text']):
            name=compact(name)
            grams={name[i:i+2]for i in range(len(name)-1)}-{'科技','成果','项目','产品','技术'}
            overlap=sum(g in query for g in grams)
            if overlap:names[name]=overlap
    trace={'entity_candidates':names,'added':[]}
    if not names or not limit:return old,trace
    existing={r['id']for r in old};matches=[]
    for row in corpus:
        if row['id']in existing:continue
        text=compact(row['text'])
        if re.match(r'(成果名称|项目名称|产品名称)[：:]',text):continue
        hits=[(overlap,name)for name,overlap in names.items()if name in text]
        if hits and len(text)>120:
            overlap,name=max(hits);matches.append((-overlap,len(text),row['id'],name,row))
    matches.sort(key=lambda x:x[:3]);added=[dict(x[4])for x in matches[:min(limit,len(old))]]
    trace['added']=[{'id':x[2],'entity':x[3]} for x in matches[:len(added)]]
    # Keep the initial result, then linked evidence; retain the total context count.
    merged=old[:1]+added+old[1:]
    return merged[:len(old)],trace
