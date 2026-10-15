import json,unittest
import numpy as np
from experiments.gold100.baseline import Index as BaseIndex
from experiments.gold100.r05 import text_key
from experiments.gold100.r06 import Index,MAX_CONTEXT,messages
from experiments.gold100.r04 import SYSTEM

class ComposedRetrievalTests(unittest.TestCase):
    def index(self,records):
        vector=np.ones(1024)
        vs={text_key(c['text']):vector for c in BaseIndex(records).chunks}
        return Index(records,vs),vector
    def test_page_dependency_and_scope_keep_exact_sources(self):
        records={'D01:1:01':'申请投资退出奖励，收入条件见下页。','D01:2:01':'收入达标或利润达标；门槛以上含本数。','D01:3:01':'本办法有效期三年。'}
        index,v=self.index(records);chunks=index.search('申请投资退出奖励门槛',v)
        self.assertEqual({c['source_id']for c in chunks},set(records))
        for c in chunks:self.assertEqual(c['text'],records[c['source_id']][c['start']:c['end']])
        for rid in records:
            spans=[(c['start'],c['end'])for c in chunks if c['source_id']==rid]
            self.assertEqual(sum(b-a for a,b in spans),len(set(i for a,b in spans for i in range(a,b))))
    def test_catalog_count_does_not_merge_same_name_or_invent_type(self):
        def row(title,book):return '原文。目录字段：'+json.dumps({'标题':title,'出处典籍':book},ensure_ascii=False)
        records={'a':row('同名方','甲书'),'b':row('同名方','乙书'),'c':row('同名方','乙书')}
        index,v=self.index(records);chunks=index.search('同名方有多少条，出处哪些书？',v)
        derived=[c for c in chunks if c.get('derived')]
        self.assertEqual(len(derived),1);self.assertEqual(derived[0]['derivation']['count'],3)
        self.assertEqual(derived[0]['derivation']['record_ids'],['a','b','c'])
        self.assertIn('非去重处方数量',derived[0]['text'])
        self.assertNotIn('方剂3首',derived[0]['text'])
    def test_budget_and_prompt(self):
        records={f'D01:{i}:01':('政策资助条款' * 200)for i in range(1,12)}
        index,v=self.index(records);chunks=index.search('政策申请有效期',v)
        self.assertLessEqual(sum(len(c['text'])for c in chunks),MAX_CONTEXT)
        self.assertEqual(messages('政策申请有效期',chunks)[0]['content'],SYSTEM)

if __name__=='__main__':unittest.main()
