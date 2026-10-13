import unittest
from newdomain.catalogue_counts import aggregate
from newdomain.coherent_candidate import select, transform_messages

class CoherentCandidateTests(unittest.TestCase):
    def setUp(self):
        self.base={str(i):str(i) for i in range(8)}
        self.agg=aggregate([{'doc_id':'D','locator':'2','text':'成果名称：甲\n分类：材料类','title':'清单'}])
    def test_noncount_guangming_is_unchanged(self):
        r=select('guangming','介绍机构的研究方向',self.base,self.agg)
        self.assertEqual(r['route'],'gm-c1')
        self.assertEqual(list(r['context'].items()),list(self.base.items()))
        messages=[{'role':'user','content':'original'}]
        self.assertIs(transform_messages(r['route'],messages),messages)
    def test_count_is_source_derived_and_bounded(self):
        r=select('guangming','成果有多少项',self.base,self.agg)
        self.assertEqual(r['route'],'gm-c1-catalogue-counts')
        self.assertEqual(len(r['context']),8)
        self.assertEqual(list(r['context'])[1:],list(self.base)[:7])
        self.assertEqual(r['calculation_trace']['CALC:D:catalogue-counts']['record_count'],1)
    def test_niuhuang_preserves_context_even_for_count_question(self):
        r=select('niuhuang','成果有多少项',self.base,self.agg)
        self.assertEqual(r['route'],'nh-focused-typed-v2')
        self.assertEqual(r['context'],self.base)
    def test_fail_closed_on_untested_scope(self):
        with self.assertRaises(ValueError):select('other','问题',{},self.agg)
        two={**self.agg,'other':dict(self.agg['D'],doc_id='other')}
        with self.assertRaises(ValueError):select('guangming','成果有多少项',self.base,two)
        with self.assertRaises(ValueError):transform_messages('nh-focused-typed-v2',[])
