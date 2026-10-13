import unittest
from newdomain.subject_evidence import supplement,property_facets

class SubjectEvidenceTests(unittest.TestCase):
    def test_direct_subject_and_contrasting_evidence(self):
        corpus={'cold':{'text':'【甲】\n牛黄：甘凉。'},'neutral':{'text':'【乙】\n牛黄：味苦，平。'},'list':{'text':'【丙】\n防风（寒）牛黄（平）'},'wrong':{'text':'【丁】\n石膏：性凉。'}}
        ctx={'list':corpus['list']['text'],'other':'其他资料','a':'甲','b':'乙'}
        result,trace=supplement('但是他们说牛黄有寒凉，这个对吗？',ctx,corpus)
        self.assertEqual(list(result),['cold','neutral','list','other'])
        self.assertEqual(ctx['a'],'甲');self.assertNotIn('wrong',trace['promoted'])
    def test_missing_antecedent_and_formula_and_book_unchanged(self):
        for q in ['那寒凉的东西呢？','牛黄解毒片好吗？','《本草经》牛黄有毒吗','牛黄丸有小毒吗']:
            self.assertEqual(property_facets(q),())
    def test_no_evidence_does_not_invent(self):
        context={'a':'甲','b':'乙'}
        self.assertEqual(supplement('牛黄有毒吗',context,{})[0],context)
