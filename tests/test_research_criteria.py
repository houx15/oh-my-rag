"""Synthetic checks of diagnostic mechanics, not semantic accuracy."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('research_criteria', Path(__file__).resolve().parents[1] / 'scripts/research_criteria.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CriteriaTests(unittest.TestCase):
    def test_missing_scope_and_wrong_cap_are_flagged(self):
        requirements = [{'id':'scope','criterion':'prior period','patterns':['prior-year']},
                        {'id':'cap','criterion':'cap','patterns':['maximum10credits']}]
        checks = mod.inspect_answer('Maximum 12 credits.', requirements)
        self.assertTrue(all(x['status'].startswith('missing') for x in checks))
        checks = mod.inspect_answer('Prior-year projects: maximum 10 credits.', requirements)
        self.assertTrue(all(x['status']=='surface_present_needs_semantic_review' for x in checks))

    def test_source_anchor_tampering_rejected(self):
        ann = {'status':'posthoc_assistant_source_review_not_human_gold','cases':[{'qid':'a','requirements':[
            {'id':'cap','patterns':['10'],'support':{'kind':'source_span','page':'p','quote':'maximum 10'}}]}]}
        mod.validate_annotations(ann, {'a':{'fixed_context':{'p':'maximum 10'}}})
        with self.assertRaises(ValueError):
            mod.validate_annotations(ann, {'a':{'fixed_context':{'p':'maximum 20'}}})

    def test_negation_is_not_semantic_acceptance(self):
        check = mod.inspect_answer('not prior-year', [{'id':'s','criterion':'scope','patterns':['prior-year']}])[0]
        self.assertEqual(check['status'],'surface_present_needs_semantic_review')


if __name__ == '__main__':
    unittest.main()

class SemanticRiskTests(unittest.TestCase):
    def test_negated_requirement_flagged(self):
        req=[{'id':'completion','patterns':['本区建成']}]
        self.assertEqual(mod.risk_checks('无需本区建成即可申请',req)[0]['id'],'negated_obligation:completion')
        self.assertEqual(mod.risk_checks('要求在本区建成才可申请',req),[])

    def test_refusal_does_not_excuse_fabrication(self):
        self.assertTrue(mod.risk_checks('本次资料未包含依据。但该企业今天到账123万元。',[]))
        self.assertEqual(mod.risk_checks('资料不足，不能确认今天到账123万元。',[]),[])
        self.assertEqual(mod.risk_checks('资料不足，政策最高上限123万元不能当作到账额。',[]),[])
