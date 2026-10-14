import unittest
from newdomain.nh_facet_coverage_v2 import _longest,_main_entry,FacetIndex
from newdomain.typed_query_scope import response,compile_local
class Pipeline(unittest.TestCase):
    def test_comparison_keeps_separate_short_title(self):
        self.assertEqual(_longest(['甲书','甲书补编'],'甲书与甲书补编的异同'),['甲书','甲书补编'])
        self.assertEqual(_longest(['甲书','甲书补编'],'介绍甲书补编'),['甲书补编'])
    def test_not_treatment_subentry(self):
        self.assertFalse(_main_entry({'text':'【主治】吐泻','metadata':{'标题':'牛黄治吐泻'}}))
    def test_local_nonfactual_routes_and_exceptions(self):
        ix=FacetIndex([])
        for q,kind in [('那个是什么','clarify'),('我最近失眠怎么办','personal_current')]:
            raw=response(q,ix);self.assertEqual(raw['local_route'],kind);self.assertTrue(compile_local(raw)[1])
        for q in ['古籍怎样记载失眠','这个牛黄记载是什么','《未知书》是什么']:
            self.assertIsNone(response(q,ix))
        with self.assertRaises(ValueError):compile_local({'local_route':'clarify','content':'{"sentences":[{"text":"unsupported"}]}'})
if __name__=='__main__':unittest.main()
