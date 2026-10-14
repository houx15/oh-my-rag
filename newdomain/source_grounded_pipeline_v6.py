"""Cycle9-v4: source-marker candidate plus an explicit versioned source amendment.

The original corpus and earlier configurations stay unchanged. Public historical
transcriptions are source evidence, not modern clinical evidence.
"""
import json
from pathlib import Path
from newdomain.source_grounded_pipeline_v5 import SourceGroundedPipeline as Previous
from newdomain.nh_facet_coverage_v2 import _window
from newdomain.source_amendments import apply
CONFIGURATION='source-grounded-cycle9-v4'
class SourceGroundedPipeline(Previous):
    def __init__(self,nh_records,nh_templates,amendments=None):
        if amendments is None:
            amendments=json.loads((Path(__file__).parent/'data/niuhuang_source_amendments.json').read_text())['amendments']
        records,self.amendments=apply(nh_records,amendments)
        super().__init__(records,nh_templates)
    def prepare_nh(self,question,baseline_context,build_messages):
        context={}
        for rid,text in baseline_context.items():
            change=self.amendments.get(rid)
            if change:
                rid=change['amended_id'];text=_window(self.facets.records[rid],question)[0]
            context[rid]=text
        p=super().prepare_nh(question,context,build_messages)
        p['trace']['source_amendments']={k:v for k,v in self.amendments.items()if v['amended_id']in p['context']}
        p['configuration']=CONFIGURATION
        return p
