import unittest
from newdomain.outbound_redaction import OutboundRedactor
class RedactionTests(unittest.TestCase):
 def test_preserve_only_approved_full_institution(self):
  r=OutboundRedactor(['示例姓名'],{'source_cells':[{'value':'示例姓名研究院'}]})
  self.assertEqual(r.text('示例姓名研究院；示例姓名'), '示例姓名研究院；[已隐去姓名]')
 def test_redact_nested_values_and_contacts_without_mutating_input(self):
  r=OutboundRedactor(['示例姓名'],{'source_cells':[]});obj={'source':['示例姓名 test@example.com']}
  self.assertEqual(r.value(obj),{'source':['[已隐去姓名] [已隐去联系信息]']});self.assertIn('test@example.com',obj['source'][0])
 def test_secrets_rejected_not_sent_as_replacement(self):
  r=OutboundRedactor([] ,{'source_cells':[]})
  with self.assertRaises(ValueError):r.text('sk-'+'x'*20)
