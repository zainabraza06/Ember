// Compares the word-matching search with the meaning-based search on data/eval/semantic_queries.json, in headless Chrome against the served site.
// Usage: node scripts/eval_semantic.mjs <chrome profile dir> http://localhost:8765/ [out.json]
import {spawn} from 'child_process'; import fs from 'fs'; import path from 'path'; import {fileURLToPath} from 'url';
const here = path.dirname(fileURLToPath(import.meta.url)), prof = process.argv[2], URL = process.argv[3] || 'http://localhost:8765/', outp = process.argv[4];
const Q = JSON.parse(fs.readFileSync(path.join(here, '..', 'data', 'eval', 'semantic_queries.json'), 'utf8'));
const p = spawn(process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', '--disable-gpu', '--remote-debugging-port=9396', '--user-data-dir=' + prof, 'about:blank'], {stdio: 'ignore'});
await new Promise(r => setTimeout(r, 3000));
const tabs = await (await fetch('http://127.0.0.1:9396/json')).json(), ws = new WebSocket(tabs.find(t => t.type == 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) pend[d.id](d.result); };
const send = (method, params = {}) => new Promise(r => { pend[++id] = r; ws.send(JSON.stringify({id, method, params})); });
const ev = async e => (await send('Runtime.evaluate', {returnByValue: true, awaitPromise: true, expression: e})).result.value;
await send('Runtime.enable'); await send('Page.enable'); await send('Page.navigate', {url: URL}); await new Promise(r => setTimeout(r, 5000));
await ev(`show('ask'); true`); for (let i = 0; i < 120 && !['ready', 'off'].includes(await ev('SEM.state')); i++) await new Promise(r => setTimeout(r, 500));
const state = await ev('SEM.state'); const res = {state, min: await ev('SEM_MIN'), para: [], off: []};
for (const {q, expect} of Q.paraphrases) { const r = await ev(`(async()=>{const s=await semRank(${JSON.stringify(q)});const t=search(${JSON.stringify(q)}).hits.map(h=>h.c.claim_id);return {sem:s.slice(0,5).map(x=>[x.c.claim_id,+x.s.toFixed(3)]),term:t.slice(0,8),termN:t.length}})()`);
  res.para.push({q, expect, termRank: r.term.indexOf(expect) + 1 || null, termHits: r.termN, semRank: r.sem.findIndex(x => x[0] === expect) + 1 || null, semTop: r.sem[0]}); }
for (const q of Q.off_topic) { const r = await ev(`(async()=>{const s=await semRank(${JSON.stringify(q)});return {top:+s[0].s.toFixed(3),term:search(${JSON.stringify(q)}).hits.length}})()`); res.off.push({q, semTop: r.top, termHits: r.term, shownBySemantic: r.top >= res.min}); }
const n = res.para.length, hit = (x, k) => x && x <= k;
res.summary = {paraphrases: n, term_top3: res.para.filter(r => hit(r.termRank, 3)).length, term_top8: res.para.filter(r => hit(r.termRank, 8)).length, semantic_top1: res.para.filter(r => hit(r.semRank, 1)).length, semantic_top3: res.para.filter(r => hit(r.semRank, 3)).length, semantic_top5: res.para.filter(r => hit(r.semRank, 5)).length,
  off_topic: res.off.length, off_topic_shown_by_semantic: res.off.filter(r => r.shownBySemantic).length, off_topic_with_term_hits: res.off.filter(r => r.termHits > 0).length};
if (outp) fs.writeFileSync(outp, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res.summary, null, 1)); p.kill(); process.exit();
