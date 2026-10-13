import unittest
from newdomain.catalogue_counts import aggregate,evidence
class CatalogueCountTests(unittest.TestCase):
 def units(self):return [{'doc_id':'x','title':'资料清单','locator':str(i),'text':t}for i,t in enumerate(['成果名称：甲\n分类：生命类\n单位名称：机构一','成果名称：甲\n分类：生命类','成果名称：乙\n分类：信息类\n单位名称：机构二'])]
 def test_rows_distinct_and_missing_are_separate(self):
  a=aggregate(self.units())['x'];self.assertEqual(a['record_count'],3);self.assertEqual(a['distinct_name_count'],2);self.assertEqual(a['missing']['单位名称'],1);self.assertEqual(sum(a['dimensions']['单位名称'].values())+a['missing']['单位名称'],3)
 def test_scope_is_explicit_and_no_answer_lookup(self):
  ctx,trace=evidence('成果一共有多少项',aggregate(self.units()));text=next(iter(ctx.values()));self.assertIn('计算结果，不是原文引文',text);self.assertIn('未声称覆盖全地区',text);self.assertEqual(len(next(iter(trace.values()))['provenance']),3)
 def test_duplicate_rows_rejected(self):
  u=self.units();u[1]['locator']=u[0]['locator']
  with self.assertRaises(ValueError):aggregate(u)
