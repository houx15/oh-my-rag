import unittest
from newdomain.speaker_evidence import anchors
class SpeakerEvidence(unittest.TestCase):
 def test_no_transfer_across_section_or_speaker(self):
  text='【气味】仲景曰：甲。王甲曰：乙。【主治】丙（仲景。出某方）。【发明】李乙曰：丁。戊。'
  rows=anchors('张仲景的观点',{'s':text},['张仲景','王甲','李乙'])
  self.assertEqual([x['quote']for x in rows],['仲景曰：甲','丙（仲景。出某方）'])
  for x in rows:self.assertEqual(x['quote'],text[x['start']:x['end']])
 def test_ambiguous_alias_and_author_metadata_prove_nothing(self):
  self.assertEqual(anchors('王仲景观点',{'s':'仲景曰：甲。'},['张仲景','王仲景']),[])
  self.assertEqual(anchors('王甲观点',{'s':'作者王甲；书中记载乙。'},['王甲']),[])
if __name__=='__main__':unittest.main()
