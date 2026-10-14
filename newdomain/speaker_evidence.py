"""Conservative surface-form anchors, never an authorship resolver.

Anchors retain exact source offsets; ambiguous aliases are omitted. They only
mark explicitly named speech/parentheticals and never assign intervening text.
"""
import re

def anchors(question, context, people):
    names=[n for n in people if n and n in question]
    out=[]
    for name in names:
        aliases=[name]
        if len(name)>=3:
            short=name[-2:]
            if sum(n.endswith(short) for n in people)==1:aliases.append(short)
        for rid,text in context.items():
            for alias in aliases:
                for m in re.finditer(re.escape(alias)+r'(?:曰|云)[：∶:]',text):
                    end=len(text)
                    tail=text[m.end():]
                    stops=list(re.finditer(r'【|(?:[。！？\n])[^。！？\n【】]{1,10}(?:曰|云)[：∶:]',tail))
                    if stops:end=m.end()+stops[0].start()
                    out.append({'requested_person':name,'surface':alias,'kind':'explicit_speech_marker','source':rid,'start':m.start(),'end':end,'quote':text[m.start():end]})
                for m in re.finditer(r'[（(]'+re.escape(alias)+r'(?:[。．，,][^）)]*)?[）)]',text):
                    start=max(text.rfind('。',0,m.start()),text.rfind('】',0,m.start()),text.rfind('\n',0,m.start()))+1
                    out.append({'requested_person':name,'surface':alias,'kind':'explicit_parenthetical','source':rid,'start':start,'end':m.end(),'quote':text[start:m.end()]})
    # Duplicate full/short matching anchors carry no extra evidentiary weight.
    unique={}
    for a in out:unique[(a['requested_person'],a['source'],a['end'],a['kind'])]=a
    return list(unique.values())
