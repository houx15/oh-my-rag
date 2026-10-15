import json,unittest
from experiments.gold100.r04 import Index,messages,validate
from experiments.gold100.baseline import Index as BaselineIndex,messages as baseline_messages
class Tests(unittest.TestCase):
 def test_retrieval_and_user_message_unchanged(self):
  self.assertIs(Index,BaselineIndex)
  chunks=Index({'one':'资助按实际发生费用的 50%，最高 30 万元。'}).search('资助标准')
  self.assertEqual(messages('资助标准',chunks)[1],baseline_messages('资助标准',chunks)[1])
 def test_short_quote_still_exact(self):
  chunks=Index({'one':'资助按实际发生费用的 50%，最高 30 万元。'}).search('资助标准')
  raw={'content':json.dumps({'sentences':[{'text':'上限30万元。','citations':[{'id':chunks[0]['id'],'quote':'最高 30 万元'}]}]}),'stream_done':True,'finish_reason':'stop'}
  self.assertTrue(validate(raw,chunks)['valid'])
  raw['content']=raw['content'].replace('30 ', '30')
  self.assertFalse(validate(raw,chunks)['valid'])
if __name__=='__main__':unittest.main()
