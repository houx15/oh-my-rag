import unittest
from newdomain.definitions import DefinitionSelector


def chunk(doc,page,text,start=0):
    return {'id':f'{doc}:{page}:{start}','doc_id':doc,'locator':page,'text':text,'start':start}

class DefinitionTests(unittest.TestCase):
    def setUp(self):
        self.d=chunk('A',10,'本措施所称“以上”包括本数，“以下”不包括本数。')
        self.local=[chunk('A',i,'年产值100亿元以上（含本数）且增速15%以上。') for i in range(8)]
    def test_exact_source_budget_anchor_and_inline_exception_preserved(self):
        s=DefinitionSelector(self.local+[self.d]);out=s.select(self.local)
        self.assertEqual(out,self.local[:7]+[self.d]);self.assertIs(out[-1],self.d);self.assertEqual(out[0]['text'],self.local[0]['text']);self.assertEqual(len(self.local),8)
    def test_wrong_document_definition_never_joined(self):
        s=DefinitionSelector([self.d]);other=[chunk('B',1,'某项规则')];self.assertEqual(s.select(other),other)
    def test_multiple_pages_and_conflicting_sentences_skipped(self):
        other=chunk('A',11,'本措施所称“以上”不包括本数。')
        for chunks in [[self.d,other],[self.d,chunk('A',10,other['text'],500)]]:
            s=DefinitionSelector(chunks);self.assertEqual(s.select(self.local),self.local);self.assertIn('A',s.ambiguous_documents)
    def test_duplicates_same_page_are_deterministic(self):
        duplicate=chunk('A',10,self.d['text'],500)
        self.assertEqual(DefinitionSelector([duplicate,self.d]).select(self.local),DefinitionSelector([self.d,duplicate]).select(self.local))
    def test_empty_short_already_present_and_missing(self):
        s=DefinitionSelector([self.d]);self.assertEqual(s.select([]),[]);self.assertEqual(s.select([self.d]),[self.d]);self.assertEqual(s.select(self.local[:1]),self.local[:1]+[self.d]);self.assertEqual(DefinitionSelector([]).select(self.local),self.local)
    def test_incomplete_or_inline_definition_not_global(self):
        for t in ['以上包含本数。','本措施所称以上包括本数','年产值100亿元以上（含本数）。']:
            self.assertEqual(DefinitionSelector([chunk('A',10,t)]).select(self.local),self.local)
    def test_more_than_eight_rejected(self):
        with self.assertRaises(ValueError):DefinitionSelector([self.d]).select(self.local+[self.d])
