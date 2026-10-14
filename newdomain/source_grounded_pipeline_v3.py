"""Opt-in controlled treatments over cycle8-v3; evidence and its order unchanged.

Independent implementation: cited-speaker/excerpt scope and historical coverage.
No case IDs, reference answers, grading results, or source text rewriting.
"""
import copy
from newdomain.source_grounded_pipeline_v2 import SourceGroundedPipeline as Previous
from newdomain.citation_contract_v3 import process

CONFIGURATION = "source-grounded-cycle9-v1"
HISTORICAL_LIMIT = "本次提供的是历史文献，不能据此认定对现代疾病的疗效或给出用药方案。"
SCOPE_RULES = """
证据归属与范围检查：逐句区分编者、书中引用的人和现代资料整理者。书名或作者元数据仅能说明载录出处，不能把书中所有引述归为编者本人的观点。只有原文明确署名、曰或括注的相应话语才能归给该人；归属不清时说某书所录文字，不推断发言人。引用中有否定、条件、限定或对前文的解释时，保留这些限定，不把被解释的古语孤立成结论。回答问题本身，不因参考主题扩大问题要求。仅凭所给片段未提到某事，不能断言整本书没有记载、两个人或事项没有关系、全书只列这些内容；用本次所给片段的范围说明尚无法判断。目录只能证明条目名称，不能代表条目全文。上述检查不妨碍转述已经有直接证据的事实。"""
HISTORY_RULES = """
这是现代疾病/用药问法，但证据是历史文本：先回答可支持的历史资料部分，注明书名和原文的病名、方名或是否含该药；不把古代病名直接等同现代诊断，不把复方记载推成单味药疗效。不要因为现代疗效无法判断就丢弃相关历史事实。没有相关历史记载才使用no_evidence。描述历史用途即可，不向提问者提供剂量、制法、服法或治疗推荐。最后用 {"boundary":"historical_limit"} 表达现代证据边界；系统显示：""" + HISTORICAL_LIMIT

class SourceGroundedPipeline(Previous):
    def __init__(self, nh_records, nh_templates, coverage=True, scope=True):
        super().__init__(nh_records, nh_templates)
        self.coverage = coverage
        self.scope = scope
        self.templates["historical_limit"] = HISTORICAL_LIMIT

    def prepare_nh(self, question, baseline_context, build_messages):
        p = super().prepare_nh(question, baseline_context, build_messages)
        p = copy.deepcopy(p)
        treatment = {"coverage": False, "scope": self.scope}
        if self.scope:
            p["messages"][0]["content"] += SCOPE_RULES
        local = p.get("local_response")
        if self.coverage and local and local.get("local_route") == "clinical_current":
            p["local_response"] = None
            p["messages"][0]["content"] += HISTORY_RULES
            treatment["coverage"] = True
        p["configuration"] = CONFIGURATION
        p["trace"]["claim_treatment"] = treatment
        return p
