"""Cycle9 source-marker treatment, over the corrected historical contract."""
import json
from newdomain.source_grounded_pipeline_v4 import SourceGroundedPipeline as Previous
from newdomain.speaker_evidence import anchors
CONFIGURATION='source-grounded-cycle9-v3'
class SourceGroundedPipeline(Previous):
    def prepare_nh(self,question,baseline_context,build_messages):
        p=super().prepare_nh(question,baseline_context,build_messages)
        if any(word in question for word in ('评价','评述','看法','认为','观点')):
            found=anchors(question,p['context'],self.facets.people)
            p['trace']['speaker_anchors']=found
            if found:
                p['messages'][0]['content']+='\n所问人物的显式署名片段定位（仅原文表面标记，非独立证据；仍引用原有段号）：'+json.dumps(found,ensure_ascii=False)+'。把该人物本人的观点限制在这些明确署名文字内；其余相关内容仍可按某书所载来介绍，归属不明就说明片段不能确认发言人。尤其不能把同一引用段中其他人的话或署名后另一节的话算给该人物。不得因归属不明而省掉已有的明确署名观点。'
        p['configuration']=CONFIGURATION
        return p
