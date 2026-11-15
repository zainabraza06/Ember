# Meaning-based search (on-device embedding model)

Added after the first submission build. The Ask page can now also rank the 255 public claims **by meaning**, using a small embedding model that runs inside the visitor's browser. The word-matching search and the condition parser are unchanged and remain the default and the fallback.

## What it does and does not do
- **Does:** embeds the user's question on the device, compares it with 255 precomputed claim vectors (cosine similarity) and shows the closest existing claims.
- **Does not:** generate or rewrite any text, change any claim or citation, send anything anywhere, or use a model for the test-table answers. Every result is a real ledger claim with its review label and page citation.
- **Refusal still works.** A claim is shown only if its similarity is at least **0.60**. The off-topic questions tested here score at most 0.52, so they are still refused.

## Design
```
offline:  public claims --BGE-small int8--> data/embeddings/claim_vectors.f32 (255 x 384 float32, 382 KB)
browser:  question --prefix + WordPiece--> BGE-small int8 (onnxruntime-web, WASM, 1 thread) --> 384-d vector
          cosine against the 255 claim vectors --> claims with similarity >= 0.60 (at most 3)
```
- **Model:** BAAI `bge-small-en-v1.5` (MIT), int8 ONNX export by Xenova (`site/model/bge-small-en-v1.5-int8.onnx`, 34 MB). 384 dimensions, CLS pooling, L2-normalised. Questions carry the BGE retrieval prefix; claims are embedded as plain passages.
- **Runtime:** `onnxruntime-web` 1.17.3 (MIT), single-threaded SIMD WASM build (`site/model/ort.wasm.min.js`, `ort-wasm-simd.wasm`, 10.5 MB). Browsers without WASM SIMD, and pages opened from a file, fall back to word matching and the page says so.
- **Tokenizer:** a BERT WordPiece tokenizer written twice, `scripts/wordpiece.py` (offline) and `scripts/semantic_core.js` (page). `tests/test_semantic.py` checks they give identical token ids, including accents, punctuation, long and empty strings.
- **Vectors:** `scripts/build_embeddings.py` embeds only the public claims (`verified_auto`, `approved`). The build fails if the vectors do not match the claims shown on the page. Held-back and rejected claims have no vector.
- **Files** are loaded from the site's own `model/` folder, once, and cached by the browser. There are no external requests; a test allows only `fetch('model/...')` calls.

## Cost (measured on the build machine, Windows, Chrome)
| Item | Size or memory |
|---|---|
| Model weights (int8) | 34 MB, downloaded once |
| WASM runtime and loader | 10.7 MB |
| Claim vectors inside the page | 382 KB (about 520 KB as base64) |
| Chrome process memory, page without the model | about +210 MB over an empty tab |
| Chrome process memory, page with the model ready | about +425 MB over an empty tab, so the model adds **about 215 MB** |
| JavaScript heap | about 5 MB (the model lives in WASM memory) |
| Model load time | 1.8 to 2.6 s from a local server; about 21 s for the first, uncached visit to GitHub Pages on the build machine's connection (the browser caches it afterwards) |
| Embedding one question | roughly 0.1 to 0.2 s |

## Evaluation (`data/eval/semantic_queries.json`, `scripts/eval_semantic.mjs`)
16 hand-written paraphrases of existing claims, written to avoid the claim's own key words, plus 6 off-topic questions. Run in headless Chrome against the served site.

| Measure | Word matching | Meaning-based |
|---|---|---|
| Paraphrase: expected claim in the top 3 | 0 of 16 | **9 of 16** |
| Paraphrase: expected claim ranked first | 0 of 16 | 8 of 16 |
| Off-topic questions that would show a claim | 0 of 6 | 0 of 6 (highest similarity 0.52, threshold 0.60) |

Caveats, stated plainly: the paraphrases were deliberately written without the claims' words, so word matching scoring 0 is built into the test and is not a general claim about it. 7 of 16 paraphrases were still missed (the model ranked a related but different claim first). The set is small and hand-made; it shows the direction, not a benchmark. Results are in `data/eval/semantic_results.json`.

## Reproduce
```
pip install onnxruntime numpy
python scripts/build_embeddings.py          # data/embeddings/ (382 KB)
python scripts/build_site.py                # embeds the vectors in site/index.html
python -m http.server -d site 8765          # the model needs http(s); file:// uses word matching
node scripts/eval_semantic.mjs <chrome profile dir> http://localhost:8765/ data/eval/semantic_results.json
python -m unittest discover -s tests -q
```

## Licences and sources
`BAAI/bge-small-en-v1.5` (MIT), ONNX int8 export `Xenova/bge-small-en-v1.5` (`onnx/model_quantized.onnx`), `onnxruntime-web` (MIT). Hashes are in `data/embeddings/meta.json`. See `docs/THIRD_PARTY.md`.
