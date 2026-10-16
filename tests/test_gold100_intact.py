import json
import unittest
import numpy as np
from experiments.gold100.r09 import Index,units,spans,messages,validate
from experiments.gold100.baseline import Index as BaseIndex
from experiments.gold100.r05 import text_key

class IntactEvidenceTests(unittest.TestCase):
    def index(self,r):
        v=np.ones(1024)
        return Index(r,{text_key(c['text']):v for c in BaseIndex(r).chunks}),v
    def test_long_numeric_line_never_splits(self):
        text='说明'*49+'基金50亿元，期限2027-12-31。\n下一行1000kg/㎡。'
        us=list(units(text));self.assertEqual(''.join(us),text)
        self.assertTrue(any('50亿元' in t and '2027-12-31' in t for t in us))
        self.assertTrue(any('1000kg/㎡' in t for t in us))
    def test_section_context_uses_original_preceding_heading(self):
        r={'D01:1:01':'（一）甲园\n建筑面积。\n（二）乙园\n区位。','D01:2:01':'项目概况：荷载2T/㎡。\n（三）丙园\n荷载3T/㎡。'}
        ix,v=self.index(r);cs=ix.search('乙园荷载多少？',v)
        c=next(c for c in cs if c['source_id']=='D01:2:01');h=c['section_context']
        self.assertEqual(h['text'],'（二）乙园');self.assertEqual(h['text'],r[h['source_id']][h['start']:h['end']])
    def test_personal_dose_and_procedure_omissions(self):
        t='历史病候壮热兼咳。每月一剂。少许傅鼻下。牛黄分许蜜调与吮。犀角锉末。主治为古籍记载。'
        c={'id':'a','source_id':'a','start':0,'end':len(t),'text':t,'personal_use':True}
        visible=''.join(x['quote']for x in spans([c]).values())
        for bad in ['一剂','傅鼻下','蜜调','锉末']:self.assertNotIn(bad,visible)
        self.assertIn('壮热兼咳',visible)
        g=json.loads(messages('我能用药吗？',[c])[1]['content'])['sources'][0]
        self.assertIn('original_content_withheld',g)
        self.assertFalse(validate({'content':'[["答案",["E9S9"]]]','stream_done':True,'finish_reason':'stop'},[c])['valid'])
    def test_quoted_term_recovers_low_rank_source(self):
        r={'a':'相关症状说明。','b':'别的文字。','c':'古名词：寒热往来是历史描述。'}
        ix,v=self.index(r);cs=ix.search('请解释“寒热往来”。',v)
        self.assertTrue(any('寒热往来' in c['text'] for c in cs))
        for c in cs:self.assertEqual(c['text'],r[c['source_id']][c['start']:c['end']])

if __name__=='__main__':unittest.main()
