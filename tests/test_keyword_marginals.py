import unittest
from newdomain.keyword_marginals import analyze

class MarginalTests(unittest.TestCase):
    def trace(self, extra, selected):
        return {'views': [['kept'], ['lexical'], extra], 'selected': selected, 'hypotheses': ['guess']}

    def test_original_lexical_is_not_expansion_recall(self):
        out = analyze({'kept': 'x'}, self.trace(['dict'], ['kept', 'dict']), self.trace(['lexical'], ['kept', 'lexical']))
        self.assertEqual(out['small_model']['selected_new_vs_baseline'], ['lexical'])
        self.assertEqual(out['small_model']['selected_new_vs_original_pool'], [])

    def test_dictionary_shared_is_not_model_unique(self):
        out = analyze({'kept': 'x'}, self.trace(['shared'], ['kept']), self.trace(['shared', 'new'], ['kept', 'shared']))
        self.assertEqual(out['model_unique_pool_vs_original_and_dictionary'], ['new'])
        self.assertEqual(out['model_unique_selected_vs_original_and_dictionary'], [])
        self.assertEqual(out['small_model']['view_ranks']['new'], [None, None, 2])

    def test_reject_mismatched_controls_and_impossible_selection(self):
        d = self.trace(['dict'], ['kept'])
        m = self.trace(['new'], ['absent'])
        with self.assertRaises(ValueError):
            analyze({'kept': 'x'}, d, m)
        m = self.trace(['new'], ['kept']); m['views'][1] = ['other']
        with self.assertRaises(ValueError):
            analyze({'kept': 'x'}, d, m)

    def test_dropped_original_preserved_as_regression_signal(self):
        out = analyze({'kept': 'x'}, self.trace(['dict'], ['dict']), self.trace(['new'], ['new']))
        self.assertEqual(out['small_model']['baseline_records_dropped'], ['kept'])
        self.assertEqual(out['model_unique_selected_vs_original_and_dictionary'], ['new'])
