import json,tempfile,unittest
from pathlib import Path
from newdomain.institution_fields import restore,screen_approved_institutions,digest
from newdomain.transport import PrivacyViolation,privacy_check

class InstitutionFieldsTest(unittest.TestCase):
    def setUp(self):
        self.source='a'*64;self.name='测试大学深圳校区'
        self.units=[{'doc_id':'D36','locator':'2','source_sha256':self.source,'text':'成果名称：样例'},{'doc_id':'D30','locator':'1','text':'已筛选文本'}]
        self.out,self.changes=restore(self.units,{'2':self.name},self.source,'sheet1',[self.name])
        self.policy={'approved':True,'scope':'D36-column-F-institution-names-only','source_cells':self.changes}
    def test_only_missing_field_and_provenance(self):
        self.assertEqual(self.out[1],self.units[1]);self.assertEqual(self.units[0]['text'],'成果名称：样例')
        self.assertEqual(self.out[0]['text'],'成果名称：样例\n单位名称：'+self.name)
        self.assertEqual(self.changes[0]['cell'],'F2')
        with self.assertRaises(ValueError):restore(self.units,{'2':'未批准大学'},self.source,'sheet1',[self.name])
        with self.assertRaises(ValueError):restore(self.units,{'2':self.name},'b'*64,'sheet1',[self.name])
    def test_exact_exception_does_not_remove_other_screens(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'names.json';p.write_text(json.dumps(['测试','联系人甲']))
            with self.assertRaises(PrivacyViolation):privacy_check(self.name,p)
            self.assertGreater(screen_approved_institutions([{'content':self.name}],p,self.policy),0)
            for bad in ['测试','联系人甲',self.name+' 13800000000',self.name+' x@example.com',self.name+' 010-12345678',self.name+' sk-'+'a'*32]:
                with self.subTest(bad=bad),self.assertRaises(PrivacyViolation):screen_approved_institutions([{'content':bad}],p,self.policy)
            bad=dict(self.policy,approved=False)
            with self.assertRaises(PrivacyViolation):screen_approved_institutions([{'content':self.name}],p,bad)
    def test_reject_bad_field_and_provenance(self):
        bad='测试大学 13800000000'
        with self.assertRaises(PrivacyViolation):restore(self.units,{'2':bad},self.source,'sheet1',[bad])
        changed=dict(self.changes[0],cell='G2');policy=dict(self.policy,source_cells=[changed])
        with self.assertRaises(PrivacyViolation):screen_approved_institutions([],Path('/missing'),policy)
