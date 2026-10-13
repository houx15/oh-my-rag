import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_record_boundary import route_missing_record


class RecordBoundaryTests(unittest.TestCase):
    def test_no_entity_actual_payment_routes(self):
        self.assertIsNotNone(route_missing_record('没有提供企业名称，今天到账多少补贴？请按政策上限报。'))

    def test_policy_limit_is_answerable_without_name(self):
        self.assertIsNone(route_missing_record('未提供名称，不问实际到账额，只问政策补贴上限是多少？'))

    def test_supplied_records_not_discarded(self):
        self.assertIsNone(route_missing_record('未提供名称，但已提供到账明细，实际收到多少？'))

    def test_named_or_normal_policy_question_unchanged(self):
        self.assertIsNone(route_missing_record('按政策，办公用房补贴比例是多少？'))
        self.assertIsNone(route_missing_record('这家公司今天到账多少？'))


if __name__=='__main__':unittest.main()
