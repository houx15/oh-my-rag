"""Cycle10 factorable source/window adapter over the frozen Cycle8 generator.

Source repair, section selection and protocol normalization are independent
switches. No promotion, paid retries or changed historical/current intent policy.
"""
import json
from pathlib import Path
from newdomain.source_grounded_pipeline_v2 import SourceGroundedPipeline as Previous
from newdomain.source_amendments import apply
from newdomain.section_windows import select as section_window
from newdomain.protocol_normalization import normalize

class SourceGroundedPipeline(Previous):
    def __init__(self,records,templates,source=False,sections=False,protocol=True,aliases=()):
        records=list(records);super().__init__(records,templates)
        self.source=source;self.sections=sections;self.protocol=protocol;self.aliases=aliases
        self.patch=json.loads((Path(__file__).parent/'data/niuhuang_source_amendments.json').read_text())['amendments'] if source else []
        if source:apply(records,self.patch) # Require the frozen full original source before any window substitution.
    def prepare_nh(self,q,baseline_context,build_messages):
        p=super().prepare_nh(q,baseline_context,build_messages);context=dict(p['context']);changes=[]
        if self.sections:
            # Consider only uniquely identified section-bearing records of an
            # explicitly named book, plus records already in selected evidence.
            explicit=[b for b in self.facets.books if b in q]
            proposals=[]
            for book in explicit:
                candidates=[]
                for rid,r in self.facets.records.items():
                    if r.get('metadata',{}).get('出处典籍','').strip('《》')!=book:continue
                    w=section_window(r['text'],q)
                    if w:candidates.append((rid,w))
                if len(candidates)==1:proposals.extend(candidates)
            for rid in list(context):
                if rid in self.facets.records:
                    w=section_window(self.facets.records[rid]['text'],q)
                    if w and rid not in [x[0]for x in proposals]:proposals.append((rid,w))
            if len(proposals)==1:
                rid,(text,trace)=proposals[0]
                if rid in context:context[rid]=text
                else:context={rid:text,**dict(list(context.items())[:3])}
                changes.append({'kind':'explicit_unique_section','source':rid,**trace})
        if self.source:
            for a in self.patch:
                rid=a['record_id'];before=context.get(rid,'')
                if before.count(a['before'])!=1:continue
                context={a['amended_id']if k==rid else k:v.replace(a['before'],a['after'],1)if k==rid else v for k,v in context.items()}
                changes.append({'kind':'exact_in_window_source_patch','source':rid,'amended_id':a['amended_id']})
        if context!=p['context']:
            from newdomain.citation_contract_v3 import messages
            p['context']=context;p['messages']=messages(build_messages(q,context))
        p['trace']['cycle10_changes']=changes;p['configuration']='cycle10-factorable'
        return p
    def canonical_nh(self,raw,context,processor):
        if not self.protocol or raw.get('local_route'):return super().canonical_nh(raw,context,processor)
        normalized,trace=normalize(raw,context,self.templates,self.aliases)
        answer,valid,gate=super().canonical_nh(normalized,context,processor)
        gate['protocol_normalizations']=trace
        return answer,valid,gate
