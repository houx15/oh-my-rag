import unittest
from newdomain.evidence_use_prompt import apply,CHECK
class EvidenceUseTests(unittest.TestCase):
 def test_default_exact_nonmutating(self):
  m=[{'role':'system','content':'contract'},{'role':'user','content':'question and sources'}];n=apply(m)
  self.assertEqual(n,m);n[0]['content']='changed';self.assertEqual(m[0]['content'],'contract')
 def test_only_system_addition(self):
  m=[{'role':'system','content':'contract'},{'role':'user','content':'source'}];n=apply(m,True)
  self.assertEqual(n[1:],m[1:]);self.assertEqual(n[0]['content'],'contract\n'+CHECK);self.assertEqual(m[0]['content'],'contract')
 def test_missing_system_rejected(self):
  with self.assertRaises(ValueError):apply([{'role':'user','content':'x'}],True)
