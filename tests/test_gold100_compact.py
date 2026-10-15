import json
import unittest
import numpy as np
from experiments.gold100.r06 import Index as PreviousIndex
from experiments.gold100.r07 import Index, spans, messages, validate
from experiments.gold100.baseline import Index as BaseIndex
from experiments.gold100.r05 import text_key

class CompactEvidenceTests(unittest.TestCase):
    def chunk(self, text, personal=False):
        return {'id':'a@0:'+str(len(text)), 'source_id':'a', 'start':0, 'end':len(text), 'text':text, 'personal_use':personal}
    def raw(self, value, finish='stop'):
        return {'content':json.dumps(value, ensure_ascii=False), 'stream_done':True, 'finish_reason':finish}
    def test_retrieval_content_is_unchanged(self):
        records={'a':'申请奖励按收入或利润门槛，最高20万元。','b':'旧政策有效期三年。'}
        v=np.ones(1024);vectors={text_key(c['text']):v for c in BaseIndex(records).chunks}
        q='申请奖励需要哪些条件？';actual=Index(records,vectors).search(q,v)
        self.assertEqual([{k:v for k,v in c.items() if k!='personal_use'} for c in actual],PreviousIndex(records,vectors).search(q,v))
    def test_exact_quotes_and_no_invented_handle(self):
        c=self.chunk('甲条：20%\n最高 30万元。乙条仍须核实。');mapping=spans([c])
        for v in mapping.values():self.assertIn(v['quote'],c['text'])
        h=next(iter(mapping));result=validate(self.raw([['资料显示20%。',[h]]]),[c])
        self.assertTrue(result['valid']);self.assertEqual(result['parsed']['sentences'][0]['citations'][0],mapping[h])
        self.assertFalse(validate(self.raw([['答案',['E99S1']]]),[c])['valid'])
        self.assertFalse(validate(self.raw([['答案',[h]]],finish='length'),[c])['valid'])
    def test_personal_quote_filter_before_splitting(self):
        text='【古籍条目】\n主治为历史记载。\n用法：'+('药物'*80)+'每服二十丸。\n目录字段：朝代清。'
        c=self.chunk(text,True);m=spans([c]);visible=''.join(v['quote'] for v in m.values())
        self.assertIn('历史记载',visible);self.assertNotIn('二十丸',visible);self.assertNotIn('药物',visible)
        self.assertNotIn('二十丸',messages('我能自行服用吗？',[c])[1]['content'])
        self.assertIn('二十丸',''.join(v['quote'] for v in spans([self.chunk(text)]).values()))
    def test_empty_evidence_clarification_and_bad_schema(self):
        c=self.chunk('资料未记录。')
        self.assertTrue(validate(self.raw([['请说明所指对象。',[]]]),[c])['valid'])
        self.assertFalse(validate(self.raw({'sentences':[]}),[c])['valid'])

if __name__=='__main__':unittest.main()
