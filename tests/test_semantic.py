"""Meaning-based search: tokenizer parity (Python vs the page's JavaScript), the shipped claim vectors and the model files."""
import hashlib, json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wordpiece  # noqa: E402

SAMPLES = ['Which materials burn at 30% oxygen at 10.2 psi?', 'smoke detection in microgravity', 'Mars gravity flammability', 'how fast does the alarm go off after a fire starts',
           'CO2 suppresses flames; helium too?', 'naïve café — flame spread (mm/s)', '½-in. wide samples, 2.5-in.', 'ULOI vs MOC', 'x' * 150, '', '   ', 'Ünïcödé τest 火']


class Semantic(unittest.TestCase):
    def test_tokenizer_matches_the_pages_javascript(self):
        vocab = wordpiece.load_vocab(ROOT / 'site' / 'model' / 'vocab.txt')
        js = ("const S=require('./scripts/semantic_core.js'),fs=require('fs');const v=S.parseVocab(fs.readFileSync('site/model/vocab.txt','utf8'));"
              "const out=JSON.parse(process.argv[1]).map(t=>S.encode(t,v,128));console.log(JSON.stringify(out));")
        r = subprocess.run(['node', '-e', js, json.dumps(SAMPLES)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for text, ids in zip(SAMPLES, json.loads(r.stdout)):
            self.assertEqual(ids, wordpiece.encode(text, vocab, 128), repr(text))

    def test_claim_vectors_match_the_public_claims_and_the_model_files(self):
        emb = ROOT / 'data' / 'embeddings'
        meta = json.loads((emb / 'meta.json').read_text(encoding='utf-8')); ids = json.loads((emb / 'claim_ids.json').read_text(encoding='utf-8'))
        raw = (emb / 'claim_vectors.f32').read_bytes()
        self.assertEqual(len(raw), 4 * meta['dim'] * len(ids))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['vectors_sha256'])
        public = {json.loads(l)['claim_id'] for l in open(ROOT / 'data' / 'ledger' / 'claims.jsonl', encoding='utf-8') if json.loads(l)['status'] in ('verified_auto', 'approved')}
        self.assertEqual(set(ids), public)                       # one vector per public claim, none for held-back or rejected claims
        self.assertEqual(len(ids), 255)
        self.assertEqual(hashlib.sha256((ROOT / 'site' / 'model' / 'bge-small-en-v1.5-int8.onnx').read_bytes()).hexdigest(), meta['model_sha256'])
        self.assertEqual(hashlib.sha256((ROOT / 'site' / 'model' / 'vocab.txt').read_bytes()).hexdigest(), meta['vocab_sha256'])

    def test_vectors_are_unit_length(self):
        import struct
        emb = ROOT / 'data' / 'embeddings'; dim = json.loads((emb / 'meta.json').read_text(encoding='utf-8'))['dim']; raw = (emb / 'claim_vectors.f32').read_bytes()
        for i in (0, 100, 254):
            v = struct.unpack('<%df' % dim, raw[i * dim * 4:(i + 1) * dim * 4]); self.assertAlmostEqual(sum(x * x for x in v), 1.0, places=3)

    def test_rank_orders_by_cosine(self):
        js = "const S=require('./scripts/semantic_core.js');const q=S.normalize(new Float32Array([1,0]));const m=new Float32Array([0,1, 1,0, .6,.8]);console.log(JSON.stringify(S.rank(q,m,2).map(r=>r.i)));"
        r = subprocess.run(['node', '-e', js], cwd=ROOT, capture_output=True, text=True); self.assertEqual(json.loads(r.stdout), [1, 2, 0])

    def test_the_page_carries_the_vectors_and_loads_only_its_own_model_files(self):
        import re
        html = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('"semantic"', html)
        for call in re.findall(r"fetch\(([^)]*)\)", html):
            self.assertTrue(call.startswith("'model/"), call)    # only same-site model files; no external requests
        self.assertNotIn('cdn.jsdelivr', html); self.assertNotIn('huggingface.co/', html.split('<script id="data"')[0])


if __name__ == '__main__':
    unittest.main()
