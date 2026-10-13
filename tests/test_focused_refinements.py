import unittest
from newdomain.scoped_aggregation_v2 import evidence
from newdomain.facet_recovery_v3 import recover
from newdomain.catalogue_counts import aggregate
class FocusedRefinementTest(unittest.TestCase):
 def test_unique_mode_does_not_claim_tie(self):
  a=aggregate([{'doc_id':'x','locator':'1','text':'成果名称：甲\n应用领域：技术'}],dimensions=('应用领域',))
  c,_=evidence('哪个应用领域的成果最多？',a);self.assertIn('已知字段中最多',next(iter(c.values())));self.assertNotIn('并列',next(iter(c.values())))
 def test_access_facts_beat_forecast_and_wrong_entity(self):
  rows=[{'id':'plan','title':'科技金融大厦','text':'地铁 高铁 高速 分钟 预计2024年通车'},{'id':'facts','title':'园区','text':'（一）科技金融大厦\n步行 7 分钟到地铁；行车3分钟高速，8分钟高铁'},{'id':'wrong','title':'园区','text':'（二）凤凰广场\n步行5分钟地铁，行车10分钟高铁，科技金融大厦在旁边'}]
  c,t=recover('科技金融大厦交通位置',{},rows);self.assertEqual(t['added'],'facts')
  self.assertFalse(recover('科技金融大厦交通位置',c,rows)[1]['applied'])
 def test_floor_entity_scope_unchanged(self):
  rows=[{'id':'right','title':'科技金融大厦','text':'楼层层数-4F-42F'},{'id':'wrong','title':'其他楼','text':'主楼99层'}]
  self.assertEqual(recover('科技金融大厦多少层',{},rows)[1]['added'],'right')
