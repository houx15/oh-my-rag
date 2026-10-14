"""Opt-in exact citation completion, never a semantic entailment certificate.

Both treatments preserve every answer sentence and original quoted character.
They never add source IDs or regenerate answers. Ambiguous occurrence, section
crossing and an over-budget extension leave the original quote unchanged.
"""
import copy,re
_STOPS='。；！？\n'

def complete(answer,contexts,mode='sentence',max_chars=400):
    if mode not in ('sentence','neighbor'):raise ValueError('mode')
    if type(max_chars)is not int or max_chars<1:raise ValueError('budget')
    out=copy.deepcopy(answer);trace=[]
    if not isinstance(out,dict)or not isinstance(out.get('sentences'),list):raise ValueError('answer schema')
    for i,s in enumerate(out['sentences']):
        for j,c in enumerate(s.get('citations',[])):
            source=contexts.get(c.get('id'));quote=c.get('quote')
            if not isinstance(source,str)or not isinstance(quote,str)or not quote or source.count(quote)!=1:continue
            start=source.index(quote);end=start+len(quote)
            if mode=='neighbor':
                # Simple baseline: one punctuation-delimited neighbor on each side.
                cuts=[0]+[k+1 for k,ch in enumerate(source)if ch in _STOPS]
                if cuts[-1]!=len(source):cuts.append(len(source))
                left=max(k for k,x in enumerate(cuts)if x<=start)
                right=next(k for k,x in enumerate(cuts)if x>=end)
                a=cuts[max(0,left-1)];b=cuts[min(len(cuts)-1,right+1)]
            else:
                # Finish only the currently quoted sentence. A directly trailing
                # parenthetical attribution belongs to that sentence, not the next.
                a=start
                while a>0 and source[a-1]not in _STOPS:a-=1
                b=end
                if b and source[b-1]not in _STOPS:
                    while b<len(source)and source[b-1]not in _STOPS:b+=1
                tail=re.match(r'[（(][^()（）\n]{1,60}[）)]',source[b:])
                if tail:b+=tail.end()
            if a==start and b==end:continue
            extra=source[a:start]+source[end:b]
            if b-a>max_chars or re.search(r'【[^】]+】',extra):continue
            expanded=source[a:b]
            if quote not in expanded:raise ValueError('original quote lost')
            c['quote']=expanded
            trace.append({'sentence':i,'citation':j,'source':c['id'],'mode':mode,'before_start':start,'before_end':end,'after_start':a,'after_end':b,'added_chars':len(expanded)-len(quote),'semantic_support_verified':False})
    return out,trace
