import unittest
from newdomain.keyword_hypotheses import KeywordSearch
from newdomain.keyword_control import select

class KeywordControlTests(unittest.TestCase):
    def test_original_lexical_control_actually_adds_candidates(self):
        search = KeywordSearch({'a': '保留原文', 'b': '目标证据 内容', 'c': '无关原文'}, lambda s: s.split())
        ctx, trace = select(search, '目标证据', [], {'a': '保留原文', 'c': '无关原文'}, 2)
        self.assertEqual(list(ctx), ['a', 'b'])
        self.assertEqual(trace['hypotheses'], [])
        self.assertEqual(trace['views'][1][0], 'b')

    def test_expanded_arms_are_exact_existing_implementation(self):
        search = KeywordSearch({'a': '既有资料', 'b': '新发现 目标', 'c': '其他资料'}, lambda s: s.split())
        args = ('目标', ['新发现'], {'a': '既有资料', 'c': '其他资料'}, 2)
        self.assertEqual(select(search, *args), search.select(*args))

    def test_retained_windows_and_new_exact_window_bounds(self):
        search = KeywordSearch({'a': '保留短文其他文字', 'b': '其他'*700 + '目标证据'*20, 'c': '一般'}, lambda s: s.split())
        ctx, _ = select(search, '目标证据', [], {'a': '保留短文', 'c': '一般'}, 2)
        self.assertEqual(ctx['a'], '保留短文')
        self.assertIn(ctx['b'], search.records['b'])
        self.assertLessEqual(len(ctx['b']), 900)
