"""Cycle9 corrected contract: reuse the existing downstream boundary enum.

The v1 experiment and its failed deliveries remain reproducible in v3.
"""
from newdomain.source_grounded_pipeline_v3 import SourceGroundedPipeline as Previous, HISTORY_RULES

CONFIGURATION = 'source-grounded-cycle9-v2'

class SourceGroundedPipeline(Previous):
    def __init__(self, nh_records, nh_templates, coverage=True, scope=True):
        super().__init__(nh_records, nh_templates, coverage=coverage, scope=scope)
        del self.templates['historical_limit']

    def prepare_nh(self, question, baseline_context, build_messages):
        p = super().prepare_nh(question, baseline_context, build_messages)
        if p['trace']['claim_treatment']['coverage']:
            prefix = HISTORY_RULES.split('最后用 ')[0]
            corrected = prefix + '最后用 {"boundary":"modern_boundary"} 表达现代证据边界；使用现有协议中的固定句子。'
            content = p['messages'][0]['content']
            if not content.endswith(HISTORY_RULES):
                raise ValueError('historical prompt suffix changed')
            p['messages'][0]['content'] = content[:-len(HISTORY_RULES)] + corrected
        p['configuration'] = CONFIGURATION
        return p
