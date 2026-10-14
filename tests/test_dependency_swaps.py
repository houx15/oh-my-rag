import unittest
from newdomain.dependency_swaps import select, proposals

class DependencySwapTests(unittest.TestCase):
    def fixture(self):
        prior='第十四条 入驻程序\n（一）提出申请；\n（二）材料初审；\n（三）资格复审；\n— 1—'
        anchor='（四）专家评审；\n（五）签订协议。\n— 2—'
        baseline={'D01:2:01':anchor,'D09:1:01':'无关背景。'*40}
        return baseline,{'D01:1:01':prior,**baseline}
    def run_select(self,b,r,question='申请流程',enabled=('procedure','metadata','qualifier'),**kwargs):
        return select(question,b,r,[list(b),list(r)],{},len(b),sum(len(t.encode())for t in b.values()),enabled=enabled,**kwargs)
    def test_backward_bundle_swaps_under_same_limits(self):
        b,r=self.fixture();out,tr=self.run_select(b,r)
        self.assertIn('D01:1:01',out);self.assertNotIn('D09:1:01',out);self.assertEqual(out['D01:2:01'],b['D01:2:01'])
        event=next(e for e in tr['events']if e['status']=='accepted');d=event['dependency'];self.assertEqual(r[d['source_id']][d['start']:d['end']],d['text'])
        self.assertLessEqual(sum(len(t.encode())for t in out.values()),sum(len(t.encode())for t in b.values()))
    def test_absent_candidate_cannot_be_retrieved(self):
        b,r=self.fixture();del r['D01:1:01'];out,tr=self.run_select(b,r);self.assertEqual(out,b)
        self.assertTrue(any(e['reason']=='preceding numbered-page candidate absent'for e in tr['skipped']))
    def test_unique_question_terms_prevent_displacement(self):
        b,r=self.fixture();b['D09:1:01']='财务。'*40;r.update(b);out,tr=self.run_select(b,r,'申请流程与财务')
        self.assertEqual(out,b);self.assertTrue(any(e['status']=='blocked_by_ceiling_or_literal_coverage'for e in tr['events']))
    def test_metadata_restores_explicit_table_header_and_unit(self):
        raw='单位：万元\n|项目|金额|\n|---|---|\n|甲|20|\n';b={'table':'|甲|20|\n','other':'无关。'*40};r={'table':raw,'other':b['other']}
        out,tr=self.run_select(b,r,'甲金额',enabled=('metadata',));self.assertEqual(out['table'],raw);self.assertTrue(any(e['status']=='accepted'for e in tr['events']))
    def test_plain_ocr_columns_are_not_inferred(self):
        raw='年度\n2020\n2021\n金额\n20\n30';b={'table':'20\n30','other':'无关。'*40};r={'table':raw,'other':b['other']}
        out,tr=self.run_select(b,r,'金额',enabled=('metadata',));self.assertEqual(out,b)
    def test_qualifier_expansion_keeps_original_text(self):
        raw='奖励最高不超过100万元。';b={'p':'奖励最高','other':'无关。'*40};r={'p':raw,'other':b['other']}
        out,tr=self.run_select(b,r,'奖励',enabled=('qualifier',));self.assertEqual(out['p'],raw)
    def test_forward_continuation_stops_before_next_section(self):
        a='第十四条 入驻程序\n（一）申请；\n（二）初审；';n='（三）复审；\n（四）签订。\n第十五条 无关政策\n另外。';b={'D01:1:01':a,'other':'无关。'*40};r={**b,'D01:2:01':n}
        out,tr=self.run_select(b,r);self.assertIn('D01:2:01',out);self.assertNotIn('第十五条',out['D01:2:01'])
    def test_off_is_exact_baseline_and_inputs_unchanged(self):
        b,r=self.fixture();before=dict(b);out,tr=self.run_select(b,r,enabled=());self.assertEqual(list(out.items()),list(b.items()));self.assertEqual(before,b)
    def test_candidate_input_order_does_not_change_selection(self):
        b,r=self.fixture();out,_=self.run_select(b,r);other,_=select('申请流程',b,dict(reversed(list(r.items()))),[list(b),list(r)],{},len(b),sum(len(t.encode())for t in b.values()));self.assertEqual(out,other)
if __name__=='__main__':unittest.main()
