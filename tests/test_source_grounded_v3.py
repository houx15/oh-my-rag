import json,unittest
from newdomain.nh_facet_coverage import FacetIndex,_window
from newdomain.floor_derivation import plan
from newdomain.citation_contract_v3 import process,CLARIFY
from newdomain.coherent_candidate_v3 import hydrate_ranked_context

class Grounded(unittest.TestCase):
    def test_floor_scope_and_no_trigger_expansion(self):
        c={'A':'项目简介\n楼层层数-4F-42F'};meta={'A':{'title':'科技金融大厦'}}
        p=plan('科技金融大厦一共多少层？',c,meta)
        self.assertEqual((p['above'],p['below'],p['total']),(42,4,46))
        self.assertIsNone(plan('科技金融大厦的楼层范围是多少？',c,meta))
        self.assertIsNone(plan('科技金融大厦多少层？',c,{'A':{'title':'别的楼'}}))
        self.assertIsNone(plan('科技金融大厦多少层？',{'A':c['A']+'不设13层'},meta))
        self.assertIsNone(plan('科技金融大厦多少层？',{**c,'B':'科技金融大厦楼层层数-3F-42F'},meta))
    def test_typed_clarification_only(self):
        def fail(*args):raise AssertionError('must not send sole nonfactual enum to factual validator')
        response={'content':'{"sentences":[{"boundary":"clarify"}]}','finish_reason':'stop','stream_done':True}
        answer,valid,trace=process(response,{}, {},fail)
        self.assertTrue(valid);self.assertEqual(answer['sentences'][0]['text'],CLARIFY)
        for bad in ['{"sentences":[{"boundary":"clarify","text":"safe"}]}','{"sentences":[{"boundary":"clarify"},{"text":"dose"}]}','{"sentences":[],"sentences":[{"boundary":"clarify"}]}']:
            with self.assertRaises(ValueError):process(dict(response,content=bad),{}, {},fail)
    def test_source_windows_and_title_collision(self):
        header='【《甲本草》·牛黄】';text=header+'\n'+'前言'*500+'【气味】平。【主治】古籍记载。'
        r={'id':'a','text':text,'metadata':{'标题':'牛黄','出处典籍':'《甲本草》'}}
        window,trace=_window(r,'牛黄气味')
        self.assertLessEqual(len(window),900);self.assertEqual(window,header+'\n'+text[trace['start']:trace['end']]);self.assertIn('【气味】',window)
        records=[r,{'id':'b','text':'《甲本草》','metadata':{'type':'书目','书名':'《甲本草》'}},{'id':'c','text':'《甲本草拾遗》','metadata':{'type':'书目','书名':'《甲本草拾遗》'}}]
        out,tr=FacetIndex(records).select('介绍《甲本草拾遗》',{'a':'old'})
        self.assertEqual(tr['facets'],[{'facet':'book:甲本草拾遗','source':'c'}]);self.assertEqual(next(iter(out)),'c')
    def test_bounded_multi_entity_and_no_phantom_links(self):
        records=[{'id':'p','text':'person','metadata':{'type':'人物','姓名':'甲医'}},{'id':'f','text':'formula','metadata':{'方名':'牛黄某丸','著者':'甲医'}},{'id':'x','text':'background','metadata':{}}]
        out,tr=FacetIndex(records).select('甲医与牛黄某丸有什么关系？',{'x':'background'})
        self.assertEqual(list(out),['p','f','x']);self.assertEqual(len(tr['facets']),2)
        out,tr=FacetIndex(records).select('他是谁？',{'x':'background'})
        self.assertEqual(out,{'x':'background'});self.assertEqual(tr['facets'],[])
    def test_hydration_preserves_rank(self):
        self.assertEqual(list(hydrate_ranked_context({'z':'old','a':'old'},{'z':{'text':'new'}}).items()),[('z','new'),('a','old')])
if __name__=='__main__':unittest.main()
