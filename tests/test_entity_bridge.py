import unittest
from newdomain.entity_bridge import bridge

class EntityBridgeTests(unittest.TestCase):
 def test_link_preserves_query_and_budget(self):
  old=[{'id':'a','text':'成果名称：星光试纸'},{'id':'b','text':'其他'},{'id':'c','text':'其他2'}]
  corpus=old+[{'id':'d','text':'星光试纸。'+('来源证据。'*30)},{'id':'e','text':'另一个试纸。'+('无关。'*40)}]
  result,trace=bridge('这个试纸介绍一下',old,corpus)
  self.assertEqual([r['id']for r in result],['a','d','b']);self.assertEqual(len(old),3);self.assertEqual(trace['added'][0]['entity'],'星光试纸')
 def test_no_shared_entity_no_expansion(self):
  old=[{'id':'a','text':'成果名称：星光试纸'}]
  self.assertEqual(bridge('大楼多少层',old,old)[0],old)
 def test_never_invent_missing_detail(self):
  old=[{'id':'a','text':'成果名称：星光试纸'}]
  self.assertEqual(bridge('星光试纸',old,old)[1]['added'],[])
