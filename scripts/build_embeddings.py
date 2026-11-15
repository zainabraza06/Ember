"""Precompute the claim vectors for the meaning-based search (run offline; the page only embeds the user's question).

Model: BAAI bge-small-en-v1.5 (MIT licence), int8 ONNX export by Xenova (site/model/bge-small-en-v1.5-int8.onnx), 384 dimensions, CLS pooling, L2 normalised.
Claims are embedded as plain passages (the claim statement, no prefix). Questions get the BGE retrieval prefix in the browser.
Writes data/embeddings/claim_vectors.f32 (float32, one row per public claim), claim_ids.json and meta.json.
Usage (repo root):  pip install onnxruntime numpy ;  python scripts/build_embeddings.py
Only public claims (verified_auto, approved) are embedded; held-back and rejected claims never leave the ledger."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import wordpiece  # noqa: E402
from ledger import config, display  # noqa: E402

MODEL = ROOT / 'site' / 'model' / 'bge-small-en-v1.5-int8.onnx'
VOCAB = ROOT / 'site' / 'model' / 'vocab.txt'
OUT = ROOT / 'data' / 'embeddings'
PREFIX = 'Represent this sentence for searching relevant passages: '


def embed(session, vocab, text, max_len):
    ids = np.array([wordpiece.encode(text, vocab, max_len)], dtype=np.int64)
    out = session.run(None, {'input_ids': ids, 'attention_mask': np.ones_like(ids), 'token_type_ids': np.zeros_like(ids)})[0]
    v = out[0, 0].astype(np.float32)               # CLS pooling
    return v / (np.linalg.norm(v) or 1.0)


def main():
    vocab = wordpiece.load_vocab(VOCAB)
    session = ort.InferenceSession(str(MODEL), providers=['CPUExecutionProvider'])
    claims = [c for c in display.load_claims(config.CLAIMS_JSONL) if c['status'] in ('verified_auto', 'approved')]
    claims.sort(key=lambda c: c['claim_id'])
    mat = np.stack([embed(session, vocab, c['statement'], 512) for c in claims]).astype('<f4')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'claim_vectors.f32').write_bytes(mat.tobytes())
    (OUT / 'claim_ids.json').write_text(json.dumps([c['claim_id'] for c in claims]), encoding='utf-8')
    meta = {'model': 'BAAI/bge-small-en-v1.5', 'export': 'Xenova/bge-small-en-v1.5 onnx/model_quantized.onnx (int8)', 'dim': int(mat.shape[1]), 'claims': len(claims),
            'pooling': 'cls', 'normalized': True, 'query_prefix': PREFIX, 'passage_text': 'claim statement',
            'model_sha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(), 'vocab_sha256': hashlib.sha256(VOCAB.read_bytes()).hexdigest(),
            'vectors_sha256': hashlib.sha256(mat.tobytes()).hexdigest()}
    (OUT / 'meta.json').write_text(json.dumps(meta, indent=1), encoding='utf-8')
    print(f"{len(claims)} claim vectors, dim {mat.shape[1]}, {mat.nbytes / 1024:.0f} KB")


if __name__ == '__main__':
    main()
