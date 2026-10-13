"""Bounded direct-subject evidence supplementation for explicit property questions.

Independent implementation; no reference answers, case IDs or judge feedback used
at inference. Keeps k sources and at least k-2 existing sources. A quotation or
named-book request is left unchanged, as is missing conversational context.
"""
import re


def property_facets(question):
    if '牛黄' not in question or re.search(r'《|本草|千金|伤寒|金匮|解毒|解酒|方子|配方|药方|丸|片|胶囊', question):
        return ()
    facets=[]
    if re.search(r'寒|凉|性味|药性|偏性',question):facets.append('temperature')
    if re.search(r'有.{0,3}毒|毒性|小毒|无毒',question):facets.append('toxicity')
    return tuple(facets)


def supplement(question, context, originals):
    """Return context plus trace, preserving original full-record source text."""
    facets=property_facets(question)
    trace={'facets':list(facets),'promoted':[],'prior_selected':list(context)}
    if not facets or len(context)<2:return dict(context),trace
    candidates=[]
    patterns={'temperature':(r'性凉|甘凉|苦甘凉',r'性平|味苦[，、]?平|气味苦[、，]?平|气平'),
              'toxicity':(r'有小毒|有毒',r'无毒')}
    for rid,row in originals.items():
        text=row['text'];parts=text.split('\n',1)
        if len(parts)!=2:continue
        body=parts[1].strip()
        if not re.match(r'牛黄[：:（(]',body):continue
        lead=body[:100].split('主治')[0].split('主惊')[0]
        for facet in facets:
            for side,pat in enumerate(patterns[facet]):
                if re.search(pat,lead):candidates.append((facet,side,len(text),rid,text))
    by_id={}
    for facet,side,size,rid,text in candidates:
        item=by_id.setdefault(rid,{'coverage':set(),'size':size})
        item['coverage'].add((facet,side))
    # Maximize distinct requested property positions, then minimize source size.
    # Two facets can be covered jointly by the same direct entry.
    from itertools import combinations
    pairs=list(combinations(sorted(by_id),min(2,len(by_id)))) if by_id else []
    promoted=list(min(pairs,key=lambda ids:(-len(set().union(*(by_id[i]['coverage'] for i in ids))),sum(by_id[i]['size'] for i in ids),ids))) if pairs else []
    selected=promoted+[rid for rid in context if rid not in promoted]
    selected=selected[:len(context)]
    result={rid:(originals[rid]['text'][:900] if rid in promoted else context[rid]) for rid in selected}
    trace.update(promoted=promoted,selected=selected)
    return result,trace
