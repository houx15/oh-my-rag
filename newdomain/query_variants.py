"""Auditable retrieval-only alternatives; original utterances are never replaced.

Aliases are user-provided or conventional document-type terms, never derived from
answer keys. Ancient and modern disease terms are not asserted equivalent.
"""
import re

DOCUMENT_TERMS=('pad','PPT','资料库','演示文稿','幻灯片')
PROPERTY_TERMS=('性味','药性')


def variants(question):
    alternatives=[];events=[]
    # User-supplied ASR repair, constrained to a request to show/open material.
    if (re.search(r'打开|调出|翻到|展示|看看|看一下',question)
        and re.search(r'(?<![门党分帮])派的',question)
        and not re.search(r'党派|门派|派的任务|派的工作',question)):
        repaired=re.sub(r'(?<![门党分帮])派的','pad',question)
        alternatives.append(repaired);events.append({'rule':'user-pad-asr','from':'派的','to':'pad','status':'retrieval hypothesis, not confirmed intent'})
    if any(t.lower() in question.lower() for t in DOCUMENT_TERMS) or events:
        alternatives.append('PPT 资料库 演示文稿 幻灯片')
    if any(t in question for t in PROPERTY_TERMS):
        alternatives.append('性味 药性')
    return {'original':question,'alternatives':list(dict.fromkeys(alternatives))[:3],'events':events}
