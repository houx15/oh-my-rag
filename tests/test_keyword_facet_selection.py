import unittest
from newdomain.keyword_hypotheses import KeywordSearch
from newdomain.keyword_control import select as original
from newdomain.keyword_facet_selection import select, mode

class KeywordFacetTests(unittest.TestCase):
    def test_unrelated_and_current_price_queries_do_not_activate(self):
        records={'a':'【名医·王安（古代）】介绍', 'b':'【《古书》·白石】王安曰：此物甚贵。'}
        self.assertIsNone(mode('它有什么影响？', records)[0])
        self.assertIsNone(mode('你们白石多少钱一斤？', records)[0])
        self.assertIsNone(mode('科技成果有多少项？', records)[0])
        self.assertIsNone(mode('介绍一下这个科技成果', records)[0])
        self.assertEqual(mode('王安评价白石的价值了吗？', records)[0], 'historical_valuation')

    def test_fallback_is_identical(self):
        search=KeywordSearch({'a':'一般证据','b':'另外材料','c':'目标内容'},lambda s:s.split())
        args=('目标内容', [], {'a':'一般证据','b':'另外材料'},2)
        self.assertEqual(select(search,*args)[0], original(search,*args)[0])

    def test_original_concrete_result_survives_beyond_first_half(self):
        records={'a':'科技成果简介','b':'会议 科研成果','c':'成果名称：柔性平台\n科研成果细节','d':'其他','e':'科技成果 会议 活动'}
        search=KeywordSearch(records,lambda s:s.split());base={k:records[k]for k in ['a','b','c','d']}
        ctx,tr=select(search,'介绍科研成果',['科技成果 会议'],base,4)
        self.assertEqual(ctx['c'],base['c']);self.assertIn('c',tr['preserved_original_facets'])

    def test_attributed_valuation_not_biography_price_word(self):
        records={'a':'【名医·王安（古代）】白石价值研究','b':'【典籍档案·古书】白石价值', 'c':'【《古书》·白石】王安曰：白石甚贵。','d':'【《另一书》·白石】白石主治记载。'}
        search=KeywordSearch(records,lambda s:s.split());base={k:records[k]for k in ['a','b','d']}
        ctx,tr=select(search,'王安评价白石的价值了吗？',[],base,3)
        self.assertIn('c',ctx);self.assertNotIn('a',tr['candidate_facet_tags'])
        self.assertIn('attributed_valuation',tr['candidate_facet_tags']['c'])
        for rid,text in ctx.items():self.assertIn(text,records[rid])

    def test_no_pool_injection_or_extra_budget(self):
        search=KeywordSearch({'a':'科研成果 会议','b':'成果名称：某项\n完全无关'},lambda s:s.split())
        ctx,tr=select(search,'介绍科研成果',[],{'a':'科研成果 会议'},1)
        self.assertEqual(ctx,{'a':'科研成果 会议'});self.assertLessEqual(len(ctx),1)

    def test_different_speaker_value_not_misattributed(self):
        records={'a':'【名医·王安（古代）】白石记载','b':'【《古书》·白石】王安曰：白石有诸性质。李平曰：白石甚贵。','c':'一般'}
        search=KeywordSearch(records,lambda s:s.split())
        _,tr=select(search,'王安评价白石的价值了吗？',[],{'a':records['a'],'c':'一般'},2)
        self.assertNotIn('attributed_valuation',tr['candidate_facet_tags'].get('b',[]))

    def test_catalogue_family_does_not_override_named_lab(self):
        records={'cat:1:01':'成果名称：甲成果\n青山实验室 科研成果','cat:2:01':'成果名称：乙成果\n海滨实验室 科研成果','x':'一般 科研成果'}
        search=KeywordSearch(records,lambda s:s.split())
        _,tr=select(search,'青山实验室科研成果',[],{'cat:1:01':records['cat:1:01'],'x':records['x']},2)
        self.assertNotIn('cat:2:01',tr['candidate_facet_tags'])

    def test_existing_result_slide_is_preserved_without_lab_in_window(self):
        records={'a':'青山实验室 科研成果概况','b':'代表性科研成果\n缺陷检测系统 科研成果','c':'成果名称：弹性计算\n青山实验室 科研成果','d':'科研成果会议通知','e':'代表性科研成果\n未知单位成果'}
        search=KeywordSearch(records,lambda s:s.split());base={k:records[k]for k in ['a','b','c','d']}
        ctx,tr=select(search,'青山实验室科研成果',[],base,4)
        self.assertIn('b',ctx)
        self.assertNotIn('e',tr['candidate_facet_tags'])
