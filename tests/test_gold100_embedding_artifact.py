import hashlib,json,tempfile,unittest
from pathlib import Path
from experiments.gold100.embedding_artifact import compile_vectors,sha
from experiments.gold100.embedding_transport import MODEL,payload

class ArtifactIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
        (self.p/'responses').mkdir();(self.p/'allocation').mkdir();self.jobs=[];self.events=[]
        for kind,text in [('corpus','原文'),('query','问题')]:
            ident=kind+'1';h=hashlib.sha256(text.encode()).hexdigest();job={'id':ident,'kind':kind,'texts':[text],'text_sha256':[h]};self.jobs.append(job)
            digest=hashlib.sha256(json.dumps(payload([text]),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            path=self.p/'responses'/('call-'+hashlib.sha256((kind+ident).encode()).hexdigest()+'.json')
            self.write(path,{'request_sha256':digest,'text_sha256':[h],'model':MODEL,'vectors':[[1.0]*1024],'usage':{'input_tokens':2,'output_tokens':0},'elapsed_ms':123.4})
            key='|'.join([ident,kind,digest,MODEL]);self.events.extend([{'key':key,'status':'started'},{'key':key,'status':'terminal','success':True,'result_sha256':sha(path)}])
        self.write(self.p/'embedding-jobs.json',self.jobs)
        self.write(self.p/'freeze.json',{'hashes':{str(self.p/'embedding-jobs.json'):sha(self.p/'embedding-jobs.json')}})
        self.write(self.p/'allocation/ledger.final.json',{'totals':{'requests_dispatched':2,'open_reservations':0,'retries':0}})
        self.journal()
    def write(self,p,d):p.write_text(json.dumps(d))
    def journal(self):(self.p/'calls.journal.jsonl').write_text('\n'.join(json.dumps(x)for x in self.events))
    def test_reconciles_vectors_and_keeps_query_time(self):
        result=compile_vectors(self.p);self.assertEqual(len(result['source_vectors']),1)
        self.assertEqual(next(iter(result['query_vectors'].values()))['elapsed_ms'],123.4)
    def test_changed_response_rejected(self):
        next((self.p/'responses').glob('*.json')).write_text('{}')
        with self.assertRaisesRegex(ValueError,'response content changed'):compile_vectors(self.p)
    def test_inflight_and_failure_rejected(self):
        self.events.pop();self.journal()
        with self.assertRaisesRegex(ValueError,'incomplete journal'):compile_vectors(self.p)
    def test_changed_frozen_input_rejected(self):
        self.write(self.p/'embedding-jobs.json',[])
        with self.assertRaisesRegex(ValueError,'frozen input changed'):compile_vectors(self.p)

if __name__=='__main__':unittest.main()
