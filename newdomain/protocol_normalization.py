"""Audited, opt-in presentation normalization before the unchanged validator.

Only a small declared boundary language and source-bound explicit title aliases
are accepted. No fuzzy matching, fact deletion, citation repair, or model retry.
The original provider output and a transformation trace must be retained.
"""
import copy,json,re

# These productions express evidence limitations only, never clinical facts.
_BOUNDARY_GRAMMAR={
 'no_evidence':r'本次(?:提供的)?资料不足以回答这一部分[，,]不能补写[。.]?',
 'personal':r'(?:(?:仅凭本次提供的历史文献|上述均为古籍记载)[，,])?(?:不能据此判断|无法判断)(?:您)?个人现在能否服用[；;，,]请向合格医师核实[。.]?',
}

def normalize(response, context, templates, aliases=()):
    if response.get('finish_reason')!='stop' or not response.get('stream_done'):
        raise ValueError('incomplete response')
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('duplicate key')
            d[k]=v
        return d
    obj=json.loads(response['content'],object_pairs_hook=unique);trace=[]
    if not isinstance(obj,dict)or not isinstance(obj.get('sentences'),list):
        raise ValueError('schema')
    for i,s in enumerate(obj['sentences']):
        if not isinstance(s,dict):continue
        kind=s.get('boundary')
        if isinstance(kind,str)and kind in templates and set(s)<={'boundary','text','citations'} and s.get('citations',[])==[]:
            text=s.get('text')
            if isinstance(text,str)and kind in _BOUNDARY_GRAMMAR and re.fullmatch(_BOUNDARY_GRAMMAR[kind],text):
                trace.append({'sentence':i,'kind':'declared_boundary_grammar','boundary':kind,'before':text,'after':templates[kind]})
                obj['sentences'][i]={'boundary':kind}
            continue
        if 'boundary'in s or not isinstance(s.get('text'),str)or not isinstance(s.get('citations'),list):continue
        cited=[c.get('id')for c in s['citations']if isinstance(c,dict)]
        for short in re.findall(r'《[^》]+》',s['text']):
            if any(short in context.get(rid,'')for rid in cited):continue
            matches={a['canonical']for a in aliases if a['alias']==short and a.get('evidence') and any(a['canonical']in context.get(rid,'')and rid in a['source_ids']for rid in cited)}
            if len(matches)!=1:continue
            full=matches.pop();s['text']=s['text'].replace(short,full)
            trace.append({'sentence':i,'kind':'explicit_source_title_alias','before':short,'after':full,'cited_ids':cited})
    raw=copy.deepcopy(response);raw['content']=json.dumps(obj,ensure_ascii=False)
    return raw,trace
