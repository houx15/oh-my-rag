import unittest
from newdomain.evidence_use_prompt_v2 import apply,focus
class TaskFocusTests(unittest.TestCase):
 def test_person_uses_literal_header_only(self):
  c={'x':'【名医·张某（古代）】\n生平'}
  self.assertEqual(focus('介绍张某',c),'person')
  self.assertEqual(focus('介绍李某',c),'introduction')
 def test_distinct_tasks(self):
  self.assertEqual(focus('什么是这个对象',{}),'definition')
  self.assertEqual(focus('介绍这里的特色菜',{}),'introduction')
  self.assertEqual(focus('现在多少钱',{}),'general')
 def test_preserves_evidence_and_default(self):
  m=[{'role':'system','content':'fixedcontract'},{'role':'user','content':'source'}];c={'x':'unchanged'}
  self.assertEqual(apply(m,'介绍',c),m);out=apply(m,'介绍',c,True)
  self.assertEqual(out[1:],m[1:]);self.assertTrue(out[0]['content'].startswith('fixedcontract\n'))
  self.assertEqual(m[0]['content'],'fixedcontract');self.assertEqual(c,{'x':'unchanged'})
 def test_absence_not_forced_answer(self):
  m=[{'role':'system','content':'fixed'},{'role':'user','content':'source'}]
  self.assertIn('必须保留证据不足',apply(m,'介绍美食',{},True)[0]['content'])
