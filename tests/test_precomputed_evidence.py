import copy, unittest
from scripts.precomputed_pilot import build
from newdomain.precomputed_evidence import answer,validate

class PrecomputedTests(unittest.TestCase):
    def setUp(self):
        self.sources={'p1':'第十四条 入驻程序\n（一）申请。\n（二）初审。\n（三）复审。\n— 6—','p2':'（四）专家审。\n（五）入驻审。\n（六）签订。\n（七）协议签订起补贴。\n第十五条 最高1000平方米，最长3年，依规。\n第十六条 其他。'}
        self.bundle=build(self.sources)
    def test_procedure_and_citations(self):
        q='光明留创园签协议前有哪些流程？';a=answer(q,self.bundle,self.sources);self.assertEqual(a,answer(q,self.bundle,self.sources,'graph'));self.assertEqual([f['id']for f in a['facts']],['step1','step2','step3','step4','step5'])
        for f in a['facts']:self.assertEqual(f['text'],self.sources[f['source_id']][f['start']:f['end']])
    def test_source_change_rejected(self):
        self.sources['p1']+='改';
        with self.assertRaises(ValueError):answer('光明留创园租金起算',self.bundle,self.sources)
    def test_graph_break_rejected(self):
        del self.bundle['next']['step2']
        with self.assertRaises(ValueError):validate(self.bundle,self.sources)
    def test_bad_offsets_rejected(self):
        self.bundle['facts']['step1']['start']+=1
        with self.assertRaises(ValueError):validate(self.bundle,self.sources)
    def test_unsupported_mixed_request(self):
        self.assertEqual(answer('光明留创园租金何时开始，联系人电话？',self.bundle,self.sources)['status'],'fallback')
    def test_caps_keep_entire_condition(self):
        a=answer('光明留创园租金面积上限？',self.bundle,self.sources);self.assertIn('依规',a['answer']);self.assertEqual([f['id']for f in a['facts']],['caps'])
