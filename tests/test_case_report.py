import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_case_report import answer_text, unique, COLUMNS

class CaseReportTests(unittest.TestCase):
    def test_raw_sentence_prose_preserved(self):
        sentences=[{'text':' 不满足。<tag> & a|b\n第二行','evidence':['E1S1']},{'text':'拒绝编造金额。','evidence':[]}]
        text=answer_text({'content':json.dumps({'sentences':sentences},ensure_ascii=False)})
        self.assertEqual(text,' 不满足。<tag> & a|b\n第二行\n拒绝编造金额。')
    def test_invalid_raw_output_is_not_hidden(self):
        raw='  invalid model answer { '
        self.assertEqual(answer_text({'content':raw}),raw)
    def test_ambiguous_source_keys_rejected(self):
        with self.assertRaises(ValueError):unique([{'qid':'a'},{'qid':'a'}],lambda x:x['qid'])
        self.assertEqual(COLUMNS,['Question','Our answer','Score','Response time'])
