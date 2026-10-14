import unittest,hashlib,copy
from newdomain.source_amendments import apply
class Amendment(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':'a','text':'前旧后','metadata':{}}]
  self.p={'record_id':'a','amended_id':'a-v2','expected_text_sha256':hashlib.sha256('前旧后'.encode()).hexdigest(),'before':'旧','after':'新','sources':[{'url':'https://example.org/edition'}],'verification':'fixture'}
 def test_versioned_immutable_patch(self):
  old=copy.deepcopy(self.rows);out,tr=apply(self.rows,[self.p]);self.assertEqual(self.rows,old)
  self.assertEqual(out[0]['text'],'前新后');self.assertEqual(out[0]['id'],'a-v2');self.assertIn('a',tr)
 def test_reject_drift_or_missing_provenance(self):
  bad=copy.deepcopy(self.p);bad['expected_text_sha256']='0'*64
  with self.assertRaises(ValueError):apply(self.rows,[bad])
  bad=copy.deepcopy(self.p);bad['sources']=[]
  with self.assertRaises(ValueError):apply(self.rows,[bad])
if __name__=='__main__':unittest.main()
