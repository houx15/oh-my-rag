"""Explicit source-section windows, independent of question IDs and answer keys.

A section can be requested only by its exact source header. No symptom synonyms
or learned rewrite triggers. Returns exact header/body offsets within a budget.
"""
import re

def select(text,question,limit=900):
    if not isinstance(limit,int)or limit<1:raise ValueError('window budget')
    marks=list(re.finditer(r'【([^【】\n]{1,12})】',text))
    requested=[(i,m)for i,m in enumerate(marks)if m.group(1)in question]
    if len(requested)!=1:return None
    i,m=requested[0];header=text.partition('\n')[0]
    if len(header)+1>=limit:return None
    end=min(marks[i+1].start()if i+1<len(marks)else len(text),m.start()+limit-len(header)-1)
    return header+'\n'+text[m.start():end],{'header_start':0,'header_end':len(header),'start':m.start(),'end':end,'section':m.group(1),'complete_section':i+1==len(marks)and end==len(text)or i+1<len(marks)and end==marks[i+1].start()}
