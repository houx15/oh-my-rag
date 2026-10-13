import unittest
from newdomain.evidence_pool import EvidencePool
class EvidencePoolTests(unittest.TestCase):
 def test_rescue_detail_without_reference_input(self):
  pool=EvidencePool({'old':'【普通资料】\n泛泛说明','key':'【星光装置】\n设备介绍','detail':'【工程记录】\n星光装置的功率为额定值。'})
  got,trace=pool.build('星光装置功率是多少',{'old':'【普通资料】\n泛泛说明'})
  self.assertEqual(next(iter(got)),'old');self.assertIn('detail',got);self.assertIn('key',got)
 def test_bounded_deterministic(self):
  records={str(i):'【主题】\n内容'+str(i)for i in range(30)}
  a=EvidencePool(records).build('主题内容',{},5)[0]
  b=EvidencePool(dict(reversed(list(records.items())))).build('主题内容',{},5)[0]
  self.assertEqual(list(a),list(b));self.assertEqual(len(a),5)
