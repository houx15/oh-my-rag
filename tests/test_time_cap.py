import unittest
from scripts.time_cap_report import summarize

class TimeCapTests(unittest.TestCase):
    def row(self, elapsed=2000, valid=True, adequate=True):
        return dict(corpus='fixture',arm='baseline',pipeline_component_sum_ms=elapsed,valid=valid,score={'adequate':adequate})
    def group(self, rows):
        return summarize(rows,2000)['groups']['fixture/baseline']
    def test_boundary_and_late_answers(self):
        g=self.group([self.row(1999),self.row(2000),self.row(2000.01)])
        self.assertEqual((g['within_cap'],g['valid_adequate_within_cap'],g['over_cap']),(2,2,1))
    def test_invalid_or_inadequate_fast_answers_fail(self):
        g=self.group([self.row(1,False),self.row(1,True,False)])
        self.assertEqual(g['within_cap'],2);self.assertEqual(g['valid_adequate_within_cap'],0)
    def test_unknown_or_invalid_timings_never_succeed(self):
        g=self.group([self.row(x) for x in [None,float('nan'),float('inf'),-1,True,'100']])
        self.assertEqual(g['timing_unknown'],6);self.assertEqual(g['valid_adequate_within_cap'],0)
    def test_missing_score_keeps_denominator(self):
        r=self.row(1);r['score']=None;g=self.group([r])
        self.assertEqual(g['scheduled'],1);self.assertEqual(g['valid_adequate_within_cap'],0)
    def test_invalid_cap_rejected(self):
        for cap in [0,-1,float('inf'),True]:
            with self.assertRaises(ValueError):summarize([],cap)

    def test_current_default_is_4700_ms(self):
        g=summarize([self.row(4700),self.row(4700.01)])['groups']['fixture/baseline']
        self.assertEqual((g['within_cap'],g['over_cap']),(1,1))
