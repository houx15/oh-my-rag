import unittest
from newdomain.lexical import preserve_lexical
class LexicalTests(unittest.TestCase):
    def test_missing_same_document_hit_added_without_mutation(self):
        b=[{'id':str(i),'doc_id':'A','text':'original'} for i in range(8)];h={'id':'needed','doc_id':'A','text':'exact'};out=preserve_lexical(b,h);self.assertEqual(out,b[:7]+[h]);self.assertIs(out[-1],h);self.assertEqual(len(b),8)
    def test_cross_document_hit_rejected(self):
        b=[{'id':'x','doc_id':'A'}];self.assertEqual(preserve_lexical(b,{'id':'y','doc_id':'B'}),b)
    def test_existing_nohit_empty_short(self):
        b=[{'id':'x','doc_id':'A'}];self.assertEqual(preserve_lexical(b,b[0]),b);self.assertEqual(preserve_lexical(b,None),b);self.assertEqual(preserve_lexical([],b[0]),[]);self.assertEqual(len(preserve_lexical(b,{'id':'y','doc_id':'A'})),2)
    def test_overbudget_rejected(self):
        with self.assertRaises(ValueError):preserve_lexical([{}]*9,None)
