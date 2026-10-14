import copy,json,unittest
from newdomain.structured_claims import catalog,build_messages,render,MAX_UNIT_CHARS

class StructuredClaimsTests(unittest.TestCase):
    def setUp(self):
        self.context={'doc-a':'相比旧架构，在等量负载前提下，可节省30%资源。其他说明。','doc-b':'【《古书》】甲曰：此石贵。乙曰：此石廉。'}
        self.original=[{'role':'user','content':'【E1S1】特定技术资料｜定位:1\n'+self.context['doc-a']}]
        self.data=catalog(self.context,self.original)
    def response(self,obj):return {'content':json.dumps(obj,ensure_ascii=False),'finish_reason':'stop','stream_done':True,'usage':{'input_tokens':10,'output_tokens':10}}
    def claim(self,uid):
        u=self.data['units'][uid];return {'source':u['source'],'claim':uid,'conditions':u['conditions'],'attribution':u['attribution']}
    def deliver(self,obj,**kwargs):return render(self.response(obj),kwargs.get('context',self.context),self.original,self.data['fingerprint'])
    def test_whole_condition_is_in_answer_not_only_citation(self):
        uid=next(k for k,u in self.data['units'].items()if'30%'in u['text'])
        a,t=self.deliver({'mode':'answer','claims':[self.claim(uid)]})
        self.assertIn('相比旧架构，在等量负载前提下，可节省30%资源。',a['sentences'][0]['text'])
        self.assertFalse(t['semantic_binding_verified'])
    def test_detached_qualifier_rejects(self):
        uid=next(k for k,u in self.data['units'].items()if u['conditions']);c=self.claim(uid);c['conditions']=[]
        with self.assertRaisesRegex(ValueError,'detached'):self.deliver({'mode':'answer','claims':[c]})
    def test_cross_source_and_attribution_substitution_rejects(self):
        for field,value in [('source','S2'),('attribution','A999')]:
            c=self.claim('U1');c[field]=value
            with self.assertRaises(ValueError):self.deliver({'mode':'answer','claims':[c]})
    def test_no_free_claim_text_or_unknown_unit(self):
        c=self.claim('U1');c['text']='invented'
        with self.assertRaises(ValueError):self.deliver({'mode':'answer','claims':[c]})
        c=self.claim('U1');c['claim']='U999'
        with self.assertRaises(ValueError):self.deliver({'mode':'answer','claims':[c]})
    def test_clarify_and_abstain_are_typed_and_exclusive(self):
        for mode in ['clarify','abstain']:
            a,_=self.deliver({'mode':mode,'claims':[]});self.assertFalse(a['sentences'][0]['citations'])
            with self.assertRaises(ValueError):self.deliver({'mode':mode,'claims':[self.claim('U1')]})
    def test_conditional_does_not_assert_candidate_identity(self):
        a,_=self.deliver({'mode':'conditional','claims':[self.claim('U1')]})
        self.assertIn('尚需确认',a['sentences'][0]['text'])
    def test_speaker_neighborhood_stops_before_other_speaker(self):
        units=[u for u in self.data['units'].values()if u['kind']=='speaker_neighborhood'and u['text'].startswith('甲曰')]
        self.assertEqual(units[0]['text'],'甲曰：此石贵。')
        uid=next(k for k,u in self.data['units'].items()if u==units[0]);a,_=self.deliver({'mode':'answer','claims':[self.claim(uid)]})
        self.assertIn('甲曰',a['sentences'][0]['text']);self.assertNotIn('乙曰',a['sentences'][0]['text'])
    def test_catalog_freeze_prevents_source_substitution(self):
        ctx=dict(self.context);ctx['doc-a']='完全不同的内容。'
        with self.assertRaisesRegex(ValueError,'catalog changed'):self.deliver({'mode':'answer','claims':[self.claim('U1')]},context=ctx)
    def test_duplicates_and_invalid_envelope_reject(self):
        r=self.response({'mode':'abstain','claims':[]});r['content']='{"mode":"abstain","mode":"clarify","claims":[]}'
        with self.assertRaises(ValueError):render(r,self.context,self.original,self.data['fingerprint'])
        for field,value in [('stream_done',False),('finish_reason','length'),('usage',{'input_tokens':True,'output_tokens':2})]:
            r=self.response({'mode':'abstain','claims':[]});r[field]=value
            with self.assertRaises(ValueError):render(r,self.context,self.original,self.data['fingerprint'])
    def test_unrepresentable_long_unit_is_not_truncated(self):
        text='条件未完'+('长'*MAX_UNIT_CHARS)+'才允许。';data=catalog({'x':text},[])
        self.assertFalse(data['units']);self.assertTrue(data['omitted']);self.assertIn(text,build_messages('问',{'x':text},[])[0][1]['content'])
    def test_source_is_exact_and_inputs_unchanged(self):
        old=copy.deepcopy(self.context);msgs,data=build_messages('问',self.context,self.original)
        self.assertEqual(self.context,old)
        for u in data['units'].values():self.assertEqual(u['text'],self.context[data['sources'][u['source']]['id']][u['start']:u['end']])
        self.assertIn('特定技术资料',msgs[1]['content'])
    def test_duplicate_units_and_empty_answer_reject(self):
        for cs in [[],[self.claim('U1'),self.claim('U1')]]:
            with self.assertRaises(ValueError):self.deliver({'mode':'answer','claims':cs})

    def test_parenthetical_provenance_keeps_internal_punctuation(self):
        from newdomain.structured_claims import sentence_spans
        text='某记载（甲。出乙方）。次条。（丙。引丁书）再条。'
        values=[text[a:b] for a,b,_ in sentence_spans(text)]
        self.assertEqual(values,['某记载（甲。出乙方）。','次条。（丙。引丁书）','再条。'])
    def test_explicit_opening_policy_scope_is_rendered_and_cited(self):
        ctx={'x':'某区关于支持特定产业的若干措施\n其他说明。资助最高十万元。'}
        data=catalog(ctx,[]);uid=next(k for k,u in data['units'].items() if '资助' in u['text']);u=data['units'][uid]
        obj={'mode':'answer','claims':[{'source':u['source'],'claim':uid,'conditions':u['conditions'],'attribution':u['attribution']}]}
        a,_=render(self.response(obj),ctx,[],data['fingerprint'])
        self.assertIn('支持特定产业',a['sentences'][0]['text'])
        self.assertEqual(a['sentences'][0]['citations'][1]['quote'],ctx['x'].split('\n')[0])
