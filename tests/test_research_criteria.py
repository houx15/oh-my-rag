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
