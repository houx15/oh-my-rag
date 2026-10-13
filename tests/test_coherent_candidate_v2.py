import unittest
from newdomain.coherent_candidate_v2 import select
from newdomain.catalogue_counts import aggregate
class CoherentV2Tests(unittest.TestCase):
 def test_bridge_preserves_count_precedence(self):
  agg=aggregate([{'doc_id':'D','locator':'1','title':'清单','text':'成果名称：量子装置\n分类：信息类'}]);base={'a':'成果名称：量子装置\n介绍','b':'other'};records={'c':'量子装置'+('详细资料'*40)}
  r=select('guangming','量子装置成果有多少项',base,agg,records);self.assertEqual(r['route'],'gm-c1-catalogue-counts')
  r=select('guangming','介绍量子装置',base,agg,records);self.assertEqual(r['route'],'gm-c1-entity-bridge');self.assertEqual(list(r['context']),['a','c'])
 def test_niuhuang_keeps_original_sources(self):
  r=select('niuhuang','问题',{'x':'source'},{},{})
  self.assertEqual(r['route'],'nh-focused-typed-v2-addressed');self.assertEqual(r['context'],{'x':'source'})
