import unittest
from newdomain.predicate import add_predicate_instruction,INSTRUCTION
class PredicateTests(unittest.TestCase):
    def test_only_system_suffix_changes_and_inputs_untouched(self):
        b=[{'role':'system','content':'contract'},{'role':'user','content':'question and exact source'}];out=add_predicate_instruction(b);self.assertEqual(out[1],b[1]);self.assertEqual(out[0]['content'],'contract'+INSTRUCTION);self.assertEqual(b[0]['content'],'contract')
    def test_missing_system_rejected(self):
        for x in [[],[{'role':'user','content':'question'}]]:
            with self.assertRaises(ValueError):add_predicate_instruction(x)
