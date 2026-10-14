import unittest
from newdomain.claim_constraints import cards,apply

class ClaimConstraintTests(unittest.TestCase):
    def test_condition_keeps_comparator_and_premise(self):
        text='成果简介。相比旧架构，在等量负载前提下，可节省30%资源。后来获奖。'
        out=cards('介绍该成果',{'x':text})['cards']
        self.assertTrue(any('相比旧架构，在等量负载前提下，可节省30%资源。'==r['exact_text']for r in out))
        for r in out:self.assertEqual(text[r['start']:r['end']],r['exact_text'])

    def test_speaker_scope_stops_at_next_speaker(self):
        out=cards('甲对石头有什么评价',{'x':'甲曰：石头很贵。产于山中。乙曰：石头便宜。【主治】其他。'})['cards']
        row=next(r for r in out if r['kind']=='speaker_scope_candidate'and r['exact_text'].startswith('甲曰'))
        self.assertNotIn('乙曰',row['exact_text']);self.assertIn('石头很贵',row['exact_text'])

    def test_trailing_attribution_stays_with_claim(self):
        out=cards('平心如何记载',{'x':'【《古书》】\n平心（某医）。其他内容。'})['cards']
        self.assertTrue(any(r['exact_text'].endswith('平心（某医）。')for r in out))

    def test_unbounded_long_scope_is_omitted_not_truncated(self):
        out=cards('甲',{'x':'甲曰：'+'长文'*400})['cards']
        self.assertFalse(any(r['kind']=='speaker_scope_candidate'for r in out))

    def test_budget_and_missing_context(self):
        out=cards('前提',{'x':'在前提下才成立。'*20},limit=2,max_bytes=500)
        self.assertLessEqual(len(out['cards']),2)
        self.assertFalse(cards('是谁',{})['cards'])
        self.assertFalse(out['semantic_binding_verified'])

    def test_baseline_and_input_immutability(self):
        msg=[{'role':'system','content':'schema'},{'role':'user','content':'question'}]
        out,_=apply(msg,'问',{'x':'甲曰：原文。'},'baseline');self.assertEqual(out,msg)
        changed,_=apply(msg,'问',{'x':'甲曰：原文。'},'cards')
        self.assertEqual(msg[0]['content'],'schema');self.assertIn('schema',changed[0]['content'])
        with self.assertRaises(ValueError):apply(msg,'问',{},'other')

    def test_modern_parentheses_are_not_speaker_attribution(self):
        out=cards('机构介绍',{'x':'介绍机构（深圳）。其他信息。'})['cards']
        self.assertFalse(any(r['kind']=='attribution_candidate'for r in out))
