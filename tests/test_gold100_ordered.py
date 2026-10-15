import json
import unittest
import numpy as np
from experiments.gold100.r08 import Index, spans, messages, validate
from experiments.gold100.baseline import Index as BaseIndex
from experiments.gold100.r05 import text_key

class OrderedEvidenceTests(unittest.TestCase):
    def index(self, records):
        v=np.ones(1024)
        return Index(records,{text_key(c['text']):v for c in BaseIndex(records).chunks}),v

    def test_pages_ordered_and_exact_nonoverlap(self):
        records={'D01:1:01':'(一)甲园区\n项目介绍。','D01:2:01':'项目概况：楼层荷载2T。','D02:1:01':'乙园区荷载3T。'}
        ix,v=self.index(records);cs=ix.search('甲园区荷载多少？',v)
        ids=[c['source_id'] for c in cs if c['source_id'].startswith('D01:')]
        self.assertEqual(ids,sorted(ids))
        for c in cs:
            self.assertEqual(c['text'],records[c['source_id']][c['start']:c['end']])
        for a in cs:
            for b in cs:
                if a is not b and a['source_id']==b['source_id']:
                    self.assertTrue(a['end']<=b['start'] or b['end']<=a['start'])

    def test_filter_discloses_omissions_and_blocks_procedure(self):
        text='历史主治。组成：甲一钱。蜜和丸如梧子。外用佩带。原文观点。'
        c={'id':'a','source_id':'a','start':0,'end':len(text),'text':text,'personal_use':True}
        m=spans([c]);visible=''.join(x['quote'] for x in m.values())
        self.assertIn('历史主治',visible)
        for bad in ['一钱','蜜和丸','佩带']:self.assertNotIn(bad,visible)
        payload=json.loads(messages('我能服用吗？',[c])[1]['content'])
        self.assertGreater(payload['sources'][0]['omitted_chars'],0)
        h=next(iter(m))
        self.assertTrue(validate({'content':json.dumps([['原文历史记载。',[h]]]),'stream_done':True,'finish_reason':'stop'},[c])['valid'])
        self.assertFalse(validate({'content':'[["回答",["1"]]]','stream_done':True,'finish_reason':'stop'},[c])['valid'])

    def test_catalog_children_original_body_recovered(self):
        records={'book':'典籍介绍。目录字段：'+json.dumps({'书名':'《测试本草》','朝代':'汉'},ensure_ascii=False)}
        for n in range(12):
            records['child'+str(n)]=('组成：甲乙丙。' if n%2 else '论述药物。')+'目录字段：'+json.dumps({'出处典籍':'《测试本草》','标题':'条目'+str(n)},ensure_ascii=False)
        ix,v=self.index(records);cs=ix.search('《测试本草》有哪些方剂和论述？',v)
        self.assertTrue(set(records)-{'book'} <= {c['source_id'] for c in cs})
        self.assertLessEqual(sum(len(c['text']) for c in cs),8500)

if __name__=='__main__':unittest.main()
