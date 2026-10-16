import unittest
from unittest.mock import patch
from experiments.gold100.confirmation import measure


class ConfirmationTests(unittest.TestCase):
    def test_fresh_vector_flows_into_search_and_all_time_is_counted(self):
        calls=[]
        class Index:
            def search(self,q,v):
                calls.append(('search',q,v));return [{'id':'x','text':'evidence'}]
        def embed(q):calls.append(('embed',q));return [1,2]
        def generate(msg):calls.append(('generate',msg));return {'content':'answer'}
        def record(cs,msg):calls.append(('record',cs,msg))
        ticks=iter([10,10.2,10.3,11.8,11.9])
        with patch('experiments.gold100.confirmation.messages',return_value=['prompt']),patch('experiments.gold100.confirmation.validate',return_value={'valid':True}):
            r=measure('q',Index(),embed,generate,record,lambda:next(ticks))
        self.assertEqual([x[0]for x in calls],['embed','search','record','generate'])
        self.assertEqual(calls[1],('search','q',[1,2]))
        self.assertAlmostEqual(r['response_ms'],1900)
        self.assertAlmostEqual(sum(r[k]for k in ('embedding_ms','preparation_ms','generation_ms','validation_ms')),r['response_ms'])

    def test_embedding_failure_never_generates(self):
        def fail(q):raise RuntimeError('one attempt failed')
        def forbidden(*args):self.fail('must not generate after failed embedding')
        with self.assertRaises(RuntimeError):measure('q',None,fail,forbidden,forbidden)
