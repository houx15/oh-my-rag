"""Compile explicitly selected non-factual boundaries to fixed protocol text.

This does not reclassify arbitrary uncited sentences or repair factual claims.
Unknown boundary kinds and mixed boundary/factual fields fail closed. The caller
must still run the unchanged source/citation validator and semantic scoring.
"""
import copy,json


def messages(original,templates,citation_field):
    if citation_field not in ('citations','evidence'):raise ValueError('citation field')
    out=[dict(m)for m in original]
    out[0]['content']+='\n边界输出补充协议（优先于上面的边界原句写法，事实句格式不变）：仅在确实需要非事实边界时，使用单项对象 {"boundary":"类型"}，不要自己改写边界原句，不要同时放text或引用字段。可选类型及系统将显示的固定句子：'+json.dumps(templates,ensure_ascii=False)+'。边界也计入原有句数上限。事实句仍必须给证据，不得把可答事实换成边界。不要把名医档案等记录标题加《》冒充书名。'
    return out


def compile_response(response,templates,citation_field):
    raw=copy.deepcopy(response)
    if response.get('finish_reason')!='stop' or not response.get('stream_done'):raise ValueError('incomplete response')
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('duplicate key')
            d[k]=v
        return d
    data=json.loads(response['content'],object_pairs_hook=unique)
    if not isinstance(data,dict)or not isinstance(data.get('sentences'),list)or not 1<=len(data['sentences'])<=16:raise ValueError('schema')
    log=[]
    for i,s in enumerate(data['sentences']):
        if not isinstance(s,dict):raise ValueError('sentence schema')
        if 'boundary' not in s:continue
        if set(s)!={'boundary'} or not isinstance(s['boundary'],str) or s['boundary']not in templates:raise ValueError('unknown/mixed boundary')
        log.append({'sentence':i,'kind':s['boundary']})
        data['sentences'][i]={'text':templates[s['boundary']],citation_field:[]}
    raw['content']=json.dumps(data,ensure_ascii=False)
    return raw,log
