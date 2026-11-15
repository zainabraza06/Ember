// Renders video/ember_demo.html to numbered JPEG frames with headless Chrome: node render.mjs <outDir> [fps=30] [only=t1,t2,...]
import {spawn} from 'child_process'; import fs from 'fs'; import path from 'path'; import {fileURLToPath} from 'url';
const out = process.argv[2], fps = +(process.argv[3] || 30), only = process.argv[4] ? process.argv[4].split(',').map(Number) : null;
fs.mkdirSync(out, {recursive: true});
const here = path.dirname(fileURLToPath(import.meta.url)), url = 'file:///' + path.join(here, 'ember_demo.html').split(path.sep).join('/');
const chrome = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const p = spawn(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--remote-debugging-port=9377', '--user-data-dir=' + path.join(out, '_prof'), 'about:blank'], {stdio: 'ignore'});
await new Promise(r => setTimeout(r, 3000));
const tabs = await (await fetch('http://127.0.0.1:9377/json')).json();
const ws = new WebSocket(tabs.find(t => t.type == 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}, errs = []; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) pend[d.id](d.result); else if (d.method == 'Runtime.exceptionThrown') errs.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text); };
const send = (method, params = {}) => new Promise(r => { pend[++id] = r; ws.send(JSON.stringify({id, method, params})); });
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', {width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false});
await send('Page.navigate', {url}); await new Promise(r => setTimeout(r, 2500));
for (let i = 0; i < 40; i++) { const r = await send('Runtime.evaluate', {returnByValue: true, expression: 'window.READY === true'}); if (r.result.value) break; await new Promise(r => setTimeout(r, 300)); }
const times = only || Array.from({length: Math.round(28 * fps)}, (_, i) => i / fps);
for (let i = 0; i < times.length; i++) {
  await send('Runtime.evaluate', {expression: `seek(${times[i]})`});
  const s = await send('Page.captureScreenshot', {format: 'jpeg', quality: 94, clip: {x: 0, y: 0, width: 1920, height: 1080, scale: 1}});
  fs.writeFileSync(path.join(out, only ? `t${String(times[i]).replace('.', '_')}.jpg` : `f${String(i).padStart(4, '0')}.jpg`), Buffer.from(s.data, 'base64'));
}
console.log('frames', times.length, 'errors', JSON.stringify(errs)); p.kill(); process.exit();
