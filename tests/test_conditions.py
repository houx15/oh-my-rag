import unittest
from newdomain.conditions import compile_ledger, quantities, augment

class TypedConditionsTests(unittest.TestCase):
    def test_exact_ocr_offsets(self):
        s='年产值 10 亿\n元以上（含本数）的企业。'
        q=quantities(s)[0];p=q['span'];self.assertEqual(s[p['start']:p['end']],p['text']);self.assertEqual(q['value'],'1000000000')
    def test_document_definition(self):
        c={'D:1:1':'连续运营一年以上。','D:2:1':'本措施中有关数据“以上”“不超过”“最高”包括本数，“以下”不包括本数。'}
        x=compile_ledger('连续运营12个月',c)['conditions'][0]
        self.assertEqual(x['operator'],'ge');self.assertEqual(x['numeric_comparisons'][0]['scalar_test'],True)
        self.assertFalse(x['numeric_comparisons'][0]['semantic_binding_verified'])
    def test_local_exception_overrides_definition(self):
        c={'D:1:1':'年产值10亿元以上（含本数），增速35%以上。','D:2:1':'本规程所称“以上”不包括本数字。'}
        xs=compile_ledger('年产值10亿元，增速35%',c)['conditions']
        self.assertEqual([x['operator'] for x in xs],['ge','gt']);self.assertEqual([x['numeric_comparisons'][0]['scalar_test'] for x in xs],[True,False])
    def test_other_document_definition_does_not_join(self):
        x=compile_ledger('连续运营12个月',{'A:1':'连续运营一年以上。','B:1':'本措施中有关数据“以上”包括本数。'})['conditions'][0]
        self.assertIsNone(x['operator']);self.assertEqual(x['numeric_comparisons'],[])
    def test_conflicting_definitions_abstain(self):
        c={'D:1':'连续运营一年以上。本措施中有关数据“以上”包括本数。','D:2':'本措施中有关数据“以上”不包括本数。'}
        self.assertIsNone(compile_ledger('连续运营12个月',c)['conditions'][0]['operator'])
    def test_same_unit_different_measure_no_join(self):
        x=compile_ledger('合同金额100万元',{'D:1':'注册资本不少于100万元。'})['conditions'][0]
        self.assertEqual(x['numeric_comparisons'],[])
    def test_multiple_entities_same_measure_unresolved(self):
        x=compile_ledger('甲注册资本100万元，乙注册资本200万元',{'D:1':'注册资本不少于150万元。'})['conditions'][0]
        self.assertEqual(x['numeric_comparisons'],[]);self.assertEqual(x['entity_scope'],'unresolved')
    def test_unknown_not_zero(self):
        x=compile_ledger('注册资本没有披露',{'D:1':'注册资本不少于100万元。'})['conditions'][0]
        self.assertEqual(x['numeric_comparisons'],[])
    def test_incompatible_dimensions_no_join(self):
        x=compile_ledger('实际支出30%',{'D:1':'实际支出不超过30万元。'})['conditions'][0]
        self.assertEqual(x['numeric_comparisons'],[])
    def test_unsupported_negative_and_chinese_number_not_partial(self):
        self.assertEqual(quantities('连续运营十一年，年产值-1亿元。'),[])
    def test_negation_not_inferred_as_true(self):
        self.assertEqual(compile_ledger('已经获得用地支持',{'D:1':'未获得用地支持的项目。'})['conditions'],[])
    def test_counts_keep_entity_unit(self):
        self.assertEqual(quantities('最高3次')[0]['dimension'],'count:次');self.assertEqual(quantities('最高3家')[0]['dimension'],'count:家')
    def test_request_retains_original_evidence_and_no_decision(self):
        selected=[{'id':'D:1:1','text':'注册资本不少于100万元。','title':'示例','doc_id':'D','locator':'1'}]
        m,l=augment('注册资本100万元',selected)
        self.assertIn('E1S1',m[-1]['content']);self.assertIn('semantic_binding_verified',m[-1]['content']);self.assertFalse(l['eligibility_verified'])
    def test_truncation_disclosed(self):
        x=compile_ledger('注册资本100万元',{'D:1':'注册资本不少于100万元。'*20},limit=2)
        self.assertEqual(len(x['conditions']),2);self.assertEqual(x['omitted_conditions'],18)
