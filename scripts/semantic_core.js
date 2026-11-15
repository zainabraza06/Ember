/* Meaning-based search core: BERT (uncased) WordPiece tokenizer, mean-free CLS pooling helpers and cosine ranking. No model, no network.
   Inlined into the site by scripts/build_site.py and unit-tested through Node (tests/test_semantic.py). The tokenizer is kept identical to scripts/wordpiece.py. */
(function (root) {
  'use strict';
  const QUERY_PREFIX = 'Represent this sentence for searching relevant passages: ';
  const isPunct = ch => { const cp = ch.codePointAt(0); return (cp >= 33 && cp <= 47) || (cp >= 58 && cp <= 64) || (cp >= 91 && cp <= 96) || (cp >= 123 && cp <= 126) || /\p{P}/u.test(ch); };
  function basicTokens(text) {
    let s = '';
    for (const ch of text) {
      const cp = ch.codePointAt(0);
      if (cp === 0 || cp === 0xFFFD || (/[\p{Cc}\p{Cf}]/u.test(ch) && !'\t\n\r'.includes(ch))) continue;
      s += ('\t\n\r'.includes(ch) || /\p{Zs}/u.test(ch)) ? ' ' : ch;
    }
    s = s.toLowerCase().normalize('NFD').replace(/\p{Mn}/gu, '');
    const toks = [];
    for (const word of s.split(/\s+/).filter(Boolean)) {
      let cur = '';
      for (const ch of word) { if (isPunct(ch)) { if (cur) { toks.push(cur); cur = ''; } toks.push(ch); } else cur += ch; }
      if (cur) toks.push(cur);
    }
    return toks;
  }
  function wordpiece(token, vocab) {
    if ([...token].length > 100) return ['[UNK]'];
    const chars = [...token], pieces = []; let start = 0;
    while (start < chars.length) {
      let end = chars.length, found = null;
      while (start < end) { let sub = chars.slice(start, end).join(''); if (start > 0) sub = '##' + sub; if (vocab.has(sub)) { found = sub; break; } end--; }
      if (found === null) return ['[UNK]'];
      pieces.push(found); start = end;
    }
    return pieces;
  }
  function parseVocab(text) { const m = new Map(); text.split('\n').forEach((l, i) => { if (l !== '' || i < 30522) m.set(l.replace(/\r$/, ''), i); }); return m; }
  function encode(text, vocab, maxLen) {
    maxLen = maxLen || 128; const ids = [vocab.get('[CLS]')], unk = vocab.get('[UNK]');
    for (const t of basicTokens(text)) for (const p of wordpiece(t, vocab)) ids.push(vocab.has(p) ? vocab.get(p) : unk);
    const cut = ids.slice(0, maxLen - 1); cut.push(vocab.get('[SEP]')); return cut;
  }
  function normalize(v) { let n = 0; for (let i = 0; i < v.length; i++) n += v[i] * v[i]; n = Math.sqrt(n) || 1; const o = new Float32Array(v.length); for (let i = 0; i < v.length; i++) o[i] = v[i] / n; return o; }
  function cosine(a, b, off) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[off + i]; return s; }   // both unit length
  function rank(q, vecs, dim) { const n = vecs.length / dim, out = []; for (let i = 0; i < n; i++) out.push({i, s: cosine(q, vecs, i * dim)}); return out.sort((x, y) => y.s - x.s); }
  function decodeF32(b64) { const bin = (root.atob || (s => Buffer.from(s, 'base64').toString('binary')))(b64), buf = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i); return new Float32Array(buf.buffer); }
  const api = {QUERY_PREFIX, basicTokens, wordpiece, parseVocab, encode, normalize, cosine, rank, decodeF32};
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.SemanticCore = api;
})(typeof self !== 'undefined' ? self : this);
