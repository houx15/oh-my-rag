import importlib.util
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_axis_review import AXES,validate

class AxisReviewTests(unittest.TestCase):
    def row(self):return dict(answer_id='A',obligations={'R1':'present'},notes='source check',**{a:False for a in AXES})
    def test_complete_typed_review(self):self.assertEqual(len(validate(json.dumps({'reviews':[self.row()]}),['A'],['R1'])),1)
    def test_duplicate_answer_rejected(self):
        with self.assertRaises(ValueError):validate(json.dumps({'reviews':[self.row(),self.row()]}),['A','B'],['R1'])
    def test_missing_obligation_rejected(self):
        with self.assertRaises(ValueError):validate(json.dumps({'reviews':[self.row()]}),['A'],['R1','R2'])
    def test_string_boolean_rejected(self):
        r=self.row();r['false_refusal']='false'
        with self.assertRaises(ValueError):validate(json.dumps({'reviews':[r]}),['A'],['R1'])
if __name__=='__main__':unittest.main()
