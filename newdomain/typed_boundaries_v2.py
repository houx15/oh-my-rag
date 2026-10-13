"""Lossless acceptance of redundant, exactly matching typed boundary fields.

A boundary carrying its exact approved text and/or an empty citation list is
semantically identical to the enum alone. Never discard a differing claim.
"""
import copy,json
from newdomain.typed_boundaries import compile_response as strict_compile


def compile_response(response,templates,citation_field):
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate key')
            out[key]=value
        return out
    data=json.loads(response['content'],object_pairs_hook=unique);normalizations=[]
    if isinstance(data,dict)and isinstance(data.get('sentences'),list):
        for i,s in enumerate(data['sentences']):
            if not isinstance(s,dict)or 'boundary'not in s:continue
            kind=s['boundary']
            if not isinstance(kind,str)or kind not in templates:continue
            if not set(s)<={'boundary','text',citation_field}:continue
            if 'text'in s and s['text']!=templates[kind]:continue
            if citation_field in s and s[citation_field]!=[]:continue
            if set(s)!={'boundary'}:
                normalizations.append({'sentence':i,'normalization':'redundant_exact_template_fields','original_fields':sorted(s)})
                data['sentences'][i]={'boundary':kind}
    normalized=copy.deepcopy(response);normalized['content']=json.dumps(data,ensure_ascii=False)
    compiled,log=strict_compile(normalized,templates,citation_field)
    return compiled,normalizations+log
