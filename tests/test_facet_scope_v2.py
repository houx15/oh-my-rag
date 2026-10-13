import unittest
from newdomain.catalogue_counts import aggregate
from newdomain.scoped_aggregation import evidence
from newdomain.facet_recovery_v2 import recover
class FocusedMethodsTest(unittest.TestCase):
 def data(self):
  return aggregate([{'doc_id':'X','locator':str(i),'text':f'成果名称：项{i}\n分类：{c}\n单位名称：{n}\n应用领域：{f}'}for i,c,n,f in [(1,'生命类','光明实验室','甲'),(2,'生命类','其他','乙'),(3,'材料类','其他','甲'),(4,'材料类','其他','乙')]],dimensions=('分类','单位名称','应用领域'))
 def test_ties_and_source_scope(self):
  c,t=evidence('哪个应用领域的成果最集中？',self.data());op=t['operations']['CALC:X:scoped-operation'];self.assertEqual(op['winners'],['乙','甲']);self.assertEqual(op['denominator'],4)
  self.assertFalse(evidence('全国所有应用领域的成果哪个最多？',self.data())[0]);self.assertFalse(evidence('上线成果总数多少',self.data())[0])
 def test_compare_zero_not_unknown(self):
  c,t=evidence('生命类成果比材料类多多少？',self.data());self.assertEqual(t['operations']['CALC:X:scoped-operation']['result'],0)
 def test_alias_is_conditional_not_global(self):
  c,t=evidence('光明实验科研成果有多少项',self.data());self.assertIn('如果指',next(iter(c.values())));self.assertIn('不代表机构全部',next(iter(c.values())))
 def test_one_addition_and_wrong_entity_exclusion(self):
  old={str(i):'unrelated'for i in range(8)};records=[{'id':'wrong','text':'别的大厦 主楼99层'},{'id':'right','text':'科技金融大厦 主楼42层'}];new,t=recover('科技金融大厦多少层',old,records);self.assertEqual(len(new),8);self.assertEqual(t['added'],'right');self.assertNotIn('wrong',new)
 def test_no_deictic_guess_or_unasked_trigger(self):
  old={'x':'old'};self.assertEqual(recover('他是谁',old,[])[0],old);self.assertFalse(evidence('材料有什么用途',self.data())[0])
 def test_book_exact_title_and_facets(self):
  records=[{'id':'right','text':'【《本草纲目》·牛黄性味主治】\n【气味】x【主治】y'},{'id':'wrong','text':'【《本草纲目拾遗》·牛黄性味主治】\n【气味】x【主治】y'}];c,t=recover('《本草纲目》关于牛黄有什么记载',{'x':'old'},records);self.assertEqual(t['added'],'right')

 def test_neighbor_property_cannot_lend_transport_numbers(self):
  wrong={'id':'other','title':'管理园区','text':'（二）凤凰广场\n地铁 高铁 高速 步行 驾车 分钟。与科技金融大厦联动。'}
  right={'id':'right','title':'管理园区','text':'（一）科技金融大厦\n地铁 步行 分钟'}
  c,t=recover('科技金融大厦交通位置优势',{'old':'x'},[wrong,right]);self.assertEqual(t['added'],'right')
 def test_floor_heading_in_dedicated_document_title(self):
  row={'id':'p2','title':'科技金融大厦项目推介','text':'项目参数\n楼层层数-4F-42F'}
  c,t=recover('科技金融大厦多少层',{},[row]);self.assertEqual(t['added'],'p2')
