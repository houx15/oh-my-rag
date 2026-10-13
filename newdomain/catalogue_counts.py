"""Deterministic catalogue aggregates with explicit units and row provenance.

Counts source records, not world entities. Missing dimensions remain unknown;
repeated names are reported separately and never silently deduplicated.
"""
import hashlib,json,re
from collections import Counter,defaultdict


def aggregate(units,name_field='成果名称',dimensions=('分类','单位名称')):
    groups=defaultdict(list)
    for unit in units:
        fields={}
        for line in unit['text'].splitlines():
            m=re.match(r'^([^：:]+)[：:](.*)$',line)
            if m and m[1]in(name_field,)+tuple(dimensions):
                if m[1]in fields:raise ValueError('duplicate field in source record')
                fields[m[1]]=m[2].strip()
        if fields.get(name_field):groups[unit['doc_id']].append((unit,fields))
    output={}
    for doc,rows in groups.items():
        locs=[str(u['locator'])for u,f in rows]
        if len(set(locs))!=len(locs):raise ValueError('duplicate source row locator')
        names=Counter(f[name_field]for u,f in rows)
        dims={d:dict(sorted(Counter(f[d]for u,f in rows if f.get(d)).items()))for d in dimensions}
        missing={d:sum(not f.get(d)for u,f in rows)for d in dimensions}
        output[doc]={'doc_id':doc,'title':rows[0][0].get('title',''),'record_count':len(rows),'distinct_name_count':len(names),'duplicate_name_rows':sum(n-1 for n in names.values()),'dimensions':dims,'missing':missing,'unit':'source rows, not institution/global total achievements','provenance':[{'locator':str(u['locator']),'text_sha256':hashlib.sha256(u['text'].encode()).hexdigest(),'fields':f}for u,f in rows]}
    return output


def evidence(question,aggregates):
    if not re.search(r'多少|几项|数量|总数|合计|各.{0,4}类',question)or'成果'not in question:return {},{}
    contexts={};traces={}
    for doc,a in aggregates.items():
        rid='CALC:'+doc+':catalogue-counts'
        lines=['可复算的清单统计（计算结果，不是原文引文）','来源文档：'+a['title'],f"计数口径：逐来源行计，共{a['record_count']}条成果记录；不同名称{a['distinct_name_count']}个；同名重复行{a['duplicate_name_rows']}条。未声称覆盖全地区或任何机构的全部成果。"]
        for field,counts in a['dimensions'].items():
            lines.append(field+'：'+'；'.join(f'{name}={n}条'for name,n in counts.items())+f"。此字段缺失{a['missing'][field]}条，不能把缺失条目分配给任一机构/类别。")
        contexts[rid]='\n'.join(lines);traces[rid]=a
    return contexts,traces
