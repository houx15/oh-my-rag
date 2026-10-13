"""Opt-in coherent candidate after repeated bridge and address-prompt pilots."""
from newdomain.coherent_candidate import select as previous_select, transform_messages as previous_messages
from newdomain.entity_bridge import bridge
from newdomain.citation_addresses import messages as address_messages

def select(corpus, question, baseline_context, aggregates, corpus_records):
    plan=previous_select(corpus,question,baseline_context,aggregates)
    if corpus=='niuhuang':
        plan['route']='nh-focused-typed-v2-addressed';return plan
    if plan['route']!='gm-c1':return plan
    old=[{'id':rid,'text':text}for rid,text in baseline_context.items()]
    records=[{'id':rid,'text':text}for rid,text in corpus_records.items()]
    selected,trace=bridge(question,old,records)
    if trace['added']:
        plan.update(route='gm-c1-entity-bridge',context={r['id']:r['text']for r in selected},bridge_trace=trace)
    return plan

def transform_messages(route, messages, templates=None, segment_counts=None):
    if route=='nh-focused-typed-v2-addressed':
        return address_messages(previous_messages('nh-focused-typed-v2',messages,templates),segment_counts)
    if route=='gm-c1-entity-bridge':return messages
    return previous_messages(route,messages,templates)
