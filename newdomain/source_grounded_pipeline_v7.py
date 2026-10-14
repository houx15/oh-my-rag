"""Cycle9-v5: retain source repair and targeted aids; remove global scope suffix.

The broad scope instruction had collateral coverage regressions. This single
configuration applies only existing clinical routing and explicit speaker-anchor
conditions, not per-question result selection. Evidence amendments remain data.
"""
import re
from newdomain.typed_query_scope_v2 import response as local_response
from newdomain.citation_contract_v3 import messages as contract_messages
from newdomain.source_grounded_pipeline_v6 import SourceGroundedPipeline as Previous
CONFIGURATION='source-grounded-cycle9-v5'
class SourceGroundedPipeline(Previous):
    def __init__(self,nh_records,nh_templates,amendments=None):
        super().__init__(nh_records,nh_templates,amendments=amendments)
        self.scope=False
    def prepare_nh(self,question,baseline_context,build_messages):
        p=super().prepare_nh(question,baseline_context,build_messages)
        prescribing=bool(re.search(r'怎么用药|如何用药|用什么药|怎么办|剂量|怎么服用|如何服用',question))
        historical=any(x in question for x in ('古籍','古方','记载','历史'))
        local=local_response(question,self.facets)
        if prescribing and not historical and local and local.get('local_route')=='clinical_current':
            p['local_response']=local
            p['messages']=contract_messages(build_messages(question,p['context']))
            p['trace']['claim_treatment']['coverage']=False
            p['trace']['prescribing_boundary_preserved']=True
        p['configuration']=CONFIGURATION
        return p
