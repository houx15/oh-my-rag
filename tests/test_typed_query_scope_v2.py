import unittest
from newdomain.typed_query_scope_v2 import response,compile_local
from newdomain.nh_facet_coverage_v2 import FacetIndex
class Scope(unittest.TestCase):
    def test_explicit_condition_is_not_missing_subject(self):
        r=response('这个口腔溃疡一般怎么用药？',FacetIndex([]))
        self.assertEqual(r['local_route'],'clinical_current');self.assertTrue(compile_local(r)[1])
    def test_conservative_pronoun_guard(self):
        for q in ['他们说人参的药性是什么','这个人参是什么','他张三写过什么']:
            self.assertIsNone(response(q,FacetIndex([])))
        for q in ['要那个，感觉慢','他说的那个方子好吗','这个这个有点不明白','他是不是道士']:
            self.assertEqual(response(q,FacetIndex([]))['local_route'],'clarify')
    def test_historical_question_not_clinical(self):
        self.assertIsNone(response('古籍说牛黄能治口腔溃疡吗',FacetIndex([])))
        self.assertEqual(response('牛黄能治口腔溃疡吗',FacetIndex([]))['local_route'],'clinical_current')
if __name__=='__main__':unittest.main()
