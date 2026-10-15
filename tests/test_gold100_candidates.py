import json,unittest
from experiments.gold100.r03 import Index,messages
from experiments.gold100.baseline import messages as baseline_messages

def record(title,book=None,bookroot=False):
 m={'标题':title}
 if book:m['出处典籍']='《'+book+'》'
 if bookroot:m.update(书名='《'+title+'》',著者='甲作者')
 return '【'+title+'】\n原始正文。\n目录字段：'+json.dumps(m,ensure_ascii=False)
class Tests(unittest.TestCase):
 def test_grouping_and_source_identity(self):
  r={'B':record('甲书',bookroot=True),'a':record('同名丸','甲书'),'b':record('同名丸','甲书'),'c':record('同名丸','乙书'),'d':record('另一丸','甲书'),'noise':'没有目录','untitled':'目录字段：'+json.dumps({'出处典籍':'《丙书》'},ensure_ascii=False)};i=Index(r)
  self.assertEqual(i.aggregates[('title','同名丸')]['derivation']['record_ids'],['a','b','c'])
  self.assertEqual(i.aggregates[('book','甲书')]['derivation']['record_ids'],['a','b','d'])
  # A duplicate-looking title remains a distinct record, not a distinct-formula claim.
  self.assertIn('非去重处方数量',i.aggregates[('title','同名丸')]['text'])
  r2=dict(r);r2['e']=record('同名丸','乙书');self.assertEqual(Index(r2).aggregates[('title','同名丸')]['derivation']['count'],4)
 def test_fallback_unchanged(self):
  i=Index({'D1:1:1':'公司的财政补贴为百分之五。'})
  chunks=i.search('财政补贴');self.assertEqual(chunks,i.base.search('财政补贴'));self.assertEqual(messages('财政补贴',chunks),baseline_messages('财政补贴',chunks))
class OtherRounds(unittest.TestCase):
 def test_r01_exact_handles_and_unknown_rejection(self):
  from experiments.gold100 import r01
  chunks=r01.Index({'sample':'支持条件为收入五千万元或利润两千万元。'}).search('收入')
  handle=next(iter(r01.spans(chunks)))
  raw={'content':json.dumps({'sentences':[{'text':'样例','evidence':[handle]}]}),'stream_done':True,'finish_reason':'stop'}
  self.assertTrue(r01.validate(raw,chunks)['valid'])
  raw['content']=json.dumps({'sentences':[{'text':'样例','evidence':['nonexistent']} ]})
  self.assertFalse(r01.validate(raw,chunks)['valid'])
 def test_r02_adjacent_page_is_same_document(self):
  from experiments.gold100 import r02
  corpus={'D01:1:01':'申请投资退出奖励收入','D01:2:01':'5000万元或利润2500万元。','D01:3:01':'本办法自2023年施行，有效期三年。','D02:2:01':'无关资料'}
  chunks=r02.Index(corpus).search('申请投资退出奖励',k=1)
  self.assertIn('D01:2:01',{c['source_id']for c in chunks})
  self.assertNotIn('D02:2:01',{c['source_id']for c in chunks})
  for c in chunks:self.assertEqual(c['text'],corpus[c['source_id']][c['start']:c['end']])
if __name__=='__main__':unittest.main()
