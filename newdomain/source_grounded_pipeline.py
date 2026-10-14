"""Single opt-in cycle8 configuration for application and evaluation adapters.
Retrieval backend and approved model transport remain dependency-injected.
No saved answers, question IDs, score lookups or case-by-case arm selection.
"""
from newdomain.nh_facet_coverage_v2 import FacetIndex
from newdomain.typed_query_scope import response as local_response,compile_local
from newdomain.citation_contract_v3 import messages as contract_messages,process
from newdomain.floor_derivation import messages as floor_messages

CONFIGURATION='source-grounded-cycle8-v2'
class SourceGroundedPipeline:
    def __init__(self, nh_records, nh_templates):
        self.facets=FacetIndex(nh_records);self.templates=dict(nh_templates)
    def prepare_nh(self, question, baseline_context, build_messages):
        context,trace=self.facets.select(question,baseline_context)
        local=local_response(question,self.facets)
        return {'configuration':CONFIGURATION,'context':context,'messages':contract_messages(build_messages(question,context)), 'local_response':local,'trace':trace}
    def prepare_gm(self, question, recovered_context, messages, source_records):
        msg,trace=floor_messages(messages,question,recovered_context,source_records)
        return {'configuration':CONFIGURATION,'context':recovered_context,'messages':msg,'local_response':None,'trace':trace}
    def canonical_nh(self, raw, context, processor):
        if raw.get('local_route'):return compile_local(raw)
        return process(raw,context,self.templates,processor)
