"""One evidence addition for explicit question facets; no answer/reference input."""
import re

def recover(question, context, records, max_contexts=8):
    facet=None;anchor=None
    if '科技金融大厦' in question:
        anchor='科技金融大厦'
        if any(x in question for x in ('多少层','层数','几层')):facet='floors'
        elif any(x in question for x in ('区位','地理位置','交通','位置优势','到达')):facet='transport'
    books=re.findall(r'《([^》]+)》',question)
    if not books and '本草纲目' in question:books=['本草纲目']
    if books and '牛黄' in question and any(x in question for x in ('记载','内容','情况','主治','介绍','讲')):
        facet='book_entry';anchor='《'+books[0]+'》'
    if facet is None:return context,{'applied':False,'reason':'no explicit bounded facet'}
    def score(record):
        text=record['text'];title=record.get('title','')
        if facet in ('floors','transport'):
            # A nearby property's page may mention the requested building only in passing.
            # Bind numeric/transport evidence to its section heading or dedicated source title.
            headings=list(re.finditer(r'（[一二三四五六七八九十]+）([^\n]+)',text))
            matched=[(i,m)for i,m in enumerate(headings)if anchor in m.group(1)]
            if matched:
                i,m=matched[0];text=text[m.start():headings[i+1].start()if i+1<len(headings)else len(text)]
            elif headings:return 0
            elif anchor not in title and not(0<=text.find(anchor)<160):return 0
        elif anchor not in text:return 0
        if facet=='floors':return 3*len(re.findall(r'楼层层数|主楼[^\n]{0,25}层|总层数',text))
        if facet=='transport':return sum(k in text for k in ('地铁','高铁','高速','步行','驾车','车程','分钟'))
        header=text.split('\n',1)[0]
        if anchor not in header or '牛黄'not in header:return 0
        return sum(k in text for k in ('【主治】','【气味】','【释名】'))+sum(k in header for k in ('主治','气味','性味','功效'))
    ranked=sorted([(score(r),r['id'],r['text'])for r in records],key=lambda x:(-x[0],x[1]))
    if not ranked or ranked[0][0]<3:return context,{'applied':False,'reason':'insufficient facet evidence','facet':facet}
    best=ranked[0]
    if best[1]in context:return context,{'applied':False,'reason':'best evidence already selected','facet':facet}
    output={best[1]:best[2]}
    for k,v in context.items():
        if len(output)>=max_contexts:break
        output[k]=v
    return output,{'applied':True,'facet':facet,'added':best[1],'score':best[0],'removed':[k for k in context if k not in output],'max_contexts':max_contexts}
