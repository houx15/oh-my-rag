import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_case_report import answer_text, unique, COLUMNS, cohort
import tempfile

class CaseReportTests(unittest.TestCase):
    def test_raw_sentence_prose_preserved(self):
        sentences=[{'text':' 不满足。<tag> & a|b\n第二行','evidence':['E1S1']},{'text':'拒绝编造金额。','evidence':[]}]
        text=answer_text({'content':json.dumps({'sentences':sentences},ensure_ascii=False)})
        self.assertEqual(text,' 不满足。<tag> & a|b\n第二行\n拒绝编造金额。')
    def test_invalid_raw_output_is_not_hidden(self):
        raw='  invalid model answer { '
        self.assertEqual(answer_text({'content':raw}),raw)
    def test_ambiguous_source_keys_rejected(self):
        with self.assertRaises(ValueError):unique([{'qid':'a'},{'qid':'a'}],lambda x:x['qid'])
        self.assertEqual(COLUMNS,['Question','Our answer','Score','Response time'])

    def test_pending_coverage_has_no_fabricated_measurement(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rows.json';p.write_text(json.dumps([{'qid':'a','origin':'user','question':'Actual question'},{'qid':'b','origin':'user','question':'Missing question'},{'qid':'c','origin':'curated','question':'Curated'}]))
            c={'format':'pending','results':str(p),'covered_qids':['a'],'origin':'user','arm':'C1','expected_n':1}
            rows,evidence=cohort(c)
            self.assertEqual(rows[0][0],'b | Missing question')
            self.assertTrue(all(v.startswith('MISSING') for v in rows[0][1:]))
            self.assertIsNone(evidence[0]['timing_value'])
            c['covered_qids']=['absent']
            with self.assertRaises(ValueError):cohort(c)
    def test_legacy_paired_score_without_arm_field(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);score={k:2 for k in ['correctness','support','relevance','completeness']};score.update(citation_entailment=True,reference_complete=True,adequate=True)
            (p/'scores.json').write_text(json.dumps([{'qid':'a','scores':{'C1':score}}]))
            (p/'rows.json').write_text(json.dumps([{'qid':'a','arm':'C1','origin':'user','question':'Q','raw_response':{'content':'raw answer','parent_observed_timings':{'full_ms':123.456}}}]))
            rows,_=cohort({'format':'legacy','results':str(p/'rows.json'),'scores':str(p/'scores.json'),'arm':'C1','expected_n':1})
            self.assertEqual(rows[0][1],'raw answer');self.assertEqual(rows[0][3],'123.456 ms')

    def niuhuang_fixture(self,p):
        s={k:2 for k in ['correctness','support','relevance','completeness']};s.update(citation_entailment=True,reference_complete=True,adequate=True)
        final={'sentences':[{'text':'Delivered statement.'}]}
        row={'qid':'a','repeat':0,'arm':'K','question':'Q','answer':final,'response':{'content':json.dumps(final)},'raw_response':{'content':'intermediate handles'},'full_ms':1.234}
        files={'results':[row],'scores':[{'qid':'a','repeat':0,'scores':{'K':s}}],'independent':{'rows':[{'qid':'a','repeat':0,'arm':'K','scores':s,'adequate':True}]},'cases':[{'qid':'a','question':'Q'}]}
        config={'format':'niuhuang','arm':'K','expected_n':1}
        for k,v in files.items():
            path=p/(k+'.json');path.write_text(json.dumps(v));config[k]=str(path)
        return config
    def test_niuhuang_preserves_delivered_output_and_separate_judges(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.niuhuang_fixture(Path(d));rows,e=cohort(c)
            self.assertEqual(rows[0][1],'Delivered statement.')
            self.assertIn('Independent GLM:',rows[0][2]);self.assertEqual(rows[0][3],'1.234 ms')
            self.assertEqual(e[0]['timing_field'],'full_ms')
    def test_niuhuang_mismatched_delivered_prose_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.niuhuang_fixture(Path(d));p=Path(c['results']);x=json.loads(p.read_text());x[0]['response']['content']='altered';p.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,'final response differs'):cohort(c)
