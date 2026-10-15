import unittest
from experiments.gold100.embedding_transport import payload, parse_body, DIMS

class EmbeddingContractTests(unittest.TestCase):
    def body(self):
        return {'data': [{'index':1,'embedding':[2.0]*DIMS}, {'index':0,'embedding':[1.0]*DIMS}], 'usage':{'prompt_tokens':12,'total_tokens':12}}
    def test_order_and_usage(self):
        vectors,usage=parse_body(self.body(),2)
        self.assertEqual(vectors[0][0],1.0)
        self.assertEqual(usage,{'input_tokens':12,'output_tokens':0})
    def test_reject_duplicate_or_invalid_vectors(self):
        for field,value in [('index',0),('embedding',[float('nan')]*DIMS),('embedding',[False]*DIMS),('embedding',[0]*DIMS)]:
            b=self.body();b['data'][0][field]=value
            with self.assertRaises(ValueError):parse_body(b,2)
    def test_input_bounds(self):
        for texts in [[],['x']*11,['x'*4097],[''],['牛'*1400],'query']:
            with self.assertRaises(ValueError):payload(texts)
        self.assertEqual(payload(['牛黄'])['input'],['牛黄'])
    def test_wrong_model_count_usage(self):
        b=self.body();b['model']='other'
        with self.assertRaises(ValueError):parse_body(b,2)
        with self.assertRaises(ValueError):parse_body(self.body(),1)
        b=self.body();b['usage']['total_tokens']=99
        with self.assertRaises(ValueError):parse_body(b,2)

if __name__=='__main__':unittest.main()
