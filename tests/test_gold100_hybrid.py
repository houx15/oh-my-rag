import unittest
import numpy as np
from experiments.gold100.r05 import Index, text_key
from experiments.gold100.baseline import Index as BaselineIndex

class HybridRetrievalTests(unittest.TestCase):
    def test_dense_retrieves_lexically_disjoint_source_and_preserves_slices(self):
        records={'A':'汽车维修服务','B':'小轿车故障检修','C':'蔬菜温室种植'}
        a=np.zeros(1024);a[0]=1
        b=np.zeros(1024);b[1]=1
        vectors={text_key(records['A']):a,text_key(records['B']):a,text_key(records['C']):b}
        index=Index(records,vectors)
        result=index.search('车辆出问题',a,k=2)
        self.assertEqual({c['source_id']for c in result},{'A','B'})
        for c in result:self.assertEqual(c['text'],records[c['source_id']][c['start']:c['end']])
    def test_missing_or_invalid_source_vectors_fail(self):
        with self.assertRaises(KeyError):Index({'a':'资料'}, {})
        with self.assertRaises(ValueError):Index({'a':'资料'}, {text_key('资料'):[0]*1024})
    def test_context_record_cap(self):
        records={'a':'统计数据'*700,'b':'统计数据其他'}
        v=np.ones(1024)
        vectors={text_key(c['text']):v for c in BaselineIndex(records).chunks}
        index=Index(records,vectors);result=index.search('统计数据',v)
        self.assertLessEqual(sum(c['source_id']=='a'for c in result),2)
        self.assertEqual(result,index.search('统计数据',v))

if __name__=='__main__':unittest.main()
