/* Interactive 3D view of the real test table (no library, no network): x = pressure, y = oxygen share, z = experiment family.
   The translucent box is the planned lunar-base atmosphere from the official text (oxygen 30% or more, pressure 10.2 psi or less).
   Drag to rotate; hover or tap a point for its row. Inlined by scripts/build_site.py. */
function initCube(canvas, tipEl, rows, opts) {
  'use strict';
  const ctx = canvas.getContext('2d');
  const calm = () => document.documentElement.classList.contains('calm');
  const LANES = ['FLEX', 'CFI-G', 'BASS-II', 'Saffire', 'screening_1g', 'partial_gravity_literature'];
  const pts = rows.filter(r => r.t === 'test' && r.o != null && r.p != null).map(r => ({ r, lane: Math.max(0, LANES.indexOf(r.f)) }));
  const pmax = Math.max.apply(null, pts.map(p => p.r.p)) * 1.02;
  const ZONE = opts.zone;                         // {pMaxKpa, oMin}
  let yaw = -0.7, pitch = 0.45, zoom = 1, drag = null, last = 0, hover = null, idle = 0, visible = true, W = 0, H = 0, colors = {}, proj = [];
  function readColors() {
    const cs = getComputedStyle(document.documentElement), g = n => cs.getPropertyValue(n).trim();
    colors = { self_extinguished: g('--c-se'), burned_to_completion: g('--c-bc'), externally_terminated: g('--c-et'), no_ignition: g('--c-ni'), other: g('--c-ot'), unknown: g('--c-uk'),
      accent: g('--accent'), line: g('--line'), ink: g('--ink'), muted: g('--muted') };
  }
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2), b = canvas.getBoundingClientRect();
    W = b.width; H = b.height; canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function P(x, y, z) {                           // unit-cube coordinates (-1..1) to screen
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    let X = x * cy - z * sy, Z = x * sy + z * cy, Y = y * cp - Z * sp; Z = y * sp + Z * cp;
    const d = 3.6, k = (Math.min(W, H) * 0.235 * zoom) * d / (d - Z * 0.9);
    return [W / 2 + X * k * 1.25, H / 2 - Y * k, Z];
  }
  const nx = p => (p / pmax) * 2 - 1, ny = o => o * 2 - 1, nz = l => (l / (LANES.length - 1)) * 2 - 1;
  function line(a, b, col, w, al) { const A = P(a[0], a[1], a[2]), B = P(b[0], b[1], b[2]); ctx.globalAlpha = al; ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(A[0], A[1]); ctx.lineTo(B[0], B[1]); ctx.stroke(); ctx.globalAlpha = 1; }
  function box(x0, x1, y0, y1, z0, z1, col, w, al) {
    const c = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]];
    [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]].forEach(e => line(c[e[0]], c[e[1]], col, w, al));
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    box(-1, 1, -1, 1, -1, 1, colors.line, 1, 0.9);
    // grid floor at oxygen 0 and ticks
    for (let i = 1; i < 5; i++) { const t = -1 + i * 0.4; line([t, -1, -1], [t, -1, 1], colors.line, 1, 0.35); line([-1, -1, t], [1, -1, t], colors.line, 1, 0.35); }
    // lunar-base zone
    const zx1 = nx(ZONE.pMaxKpa), zy0 = ny(ZONE.oMin);
    const zc = [[-1, zy0, -1], [zx1, zy0, -1], [zx1, 1, -1], [-1, 1, -1], [-1, zy0, 1], [zx1, zy0, 1], [zx1, 1, 1], [-1, 1, 1]].map(c => P(c[0], c[1], c[2]));
    ctx.globalAlpha = 0.10; ctx.fillStyle = colors.accent;
    [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [3, 2, 6, 7], [1, 2, 6, 5], [0, 3, 7, 4]].forEach(f => { ctx.beginPath(); f.forEach((i, n) => n ? ctx.lineTo(zc[i][0], zc[i][1]) : ctx.moveTo(zc[i][0], zc[i][1])); ctx.closePath(); ctx.fill(); });
    ctx.globalAlpha = 1; box(-1, zx1, zy0, 1, -1, 1, colors.accent, 1.6, 0.95);
    // points, far to near
    proj = pts.map(p => { const s = P(nx(p.r.p), ny(p.r.o), nz(p.lane)); return { p, x: s[0], y: s[1], z: s[2] }; }).sort((a, b) => a.z - b.z);
    proj.forEach(q => {
      const rad = 2.2 + (q.z + 1) * 1.1, col = colors[q.p.r.c] || colors.unknown, hot = hover === q;
      ctx.globalAlpha = hot ? 1 : 0.55 + (q.z + 1) * 0.2; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(q.x, q.y, hot ? rad + 3 : rad, 0, 6.2832); ctx.fill();
      if (hot) { ctx.strokeStyle = colors.ink; ctx.lineWidth = 2; ctx.stroke(); }
    });
    ctx.globalAlpha = 1;
    // spacesuit marker (100% oxygen, 4.3 psi): drawn on the front lane edge
    const su = P(nx(opts.suit.p), ny(opts.suit.o), 1);
    ctx.strokeStyle = colors.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(su[0], su[1], 7, 0, 6.2832); ctx.stroke();
    ctx.fillStyle = colors.ink; ctx.font = '600 11px system-ui,sans-serif'; ctx.fillText('spacesuit (no test)', su[0] + 11, su[1] + 4);
    // axis labels
    ctx.fillStyle = colors.muted; ctx.font = '600 11px system-ui,sans-serif';
    let a = P(1, -1, 1); ctx.fillText('pressure → ' + Math.round(pmax) + ' kPa', a[0] - 70, a[1] + 16);
    a = P(-1, 1, 1); ctx.fillText('oxygen 100%', a[0] - 4, a[1] - 8);
    a = P(-1, -1, -1); ctx.fillText('0%', a[0] - 22, a[1] + 4);
    a = P(-1, -1, 1); ctx.fillText('experiment family →', a[0] - 4, a[1] + 16);
    const zl = P(zx1, 1, -1); ctx.fillStyle = colors.accent; ctx.fillText('lunar-base atmosphere', zl[0] - 20, zl[1] - 8);
  }
  function loop(t) {
    if (visible && !document.hidden) {
      if (!calm() && !drag && idle <= 0) yaw += 0.0035; else if (idle > 0) idle -= 1;
      draw();
    }
    requestAnimationFrame(loop);
  }
  function pos(e) { const b = canvas.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; }
  function pick(x, y) { let best = null, bd = 144; for (let i = proj.length - 1; i >= 0; i--) { const q = proj[i], d = (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y); if (d < bd) { bd = d; best = q; } } return best; }
  function tip(q, x, y) {
    if (!q) { tipEl.style.display = 'none'; return; }
    const r = q.p.r; tipEl.style.display = 'block';
    tipEl.textContent = (r.i || r.f) + ' | ' + (r.m || '?') + ' | O2 ' + (r.o * 100).toFixed(1) + '% | ' + r.p.toFixed(1) + ' kPa | ' + (r.g === '?' ? 'gravity not stated' : r.g + ' g') + ' | ' + (opts.label[r.c] || r.c);
  }
  canvas.addEventListener('pointerdown', e => { canvas.setPointerCapture(e.pointerId); drag = { x: e.clientX, y: e.clientY, yaw, pitch }; idle = 300; });
  canvas.addEventListener('pointermove', e => {
    if (drag) { yaw = drag.yaw + (e.clientX - drag.x) * 0.008; pitch = Math.max(-1.2, Math.min(1.2, drag.pitch + (e.clientY - drag.y) * 0.006)); idle = 300; }
    const p = pos(e); hover = pick(p[0], p[1]); tip(hover);
  });
  canvas.addEventListener('pointerup', e => { drag = null; const p = pos(e); hover = pick(p[0], p[1]); tip(hover); });
  canvas.addEventListener('pointerleave', () => { drag = null; hover = null; tip(null); });
  canvas.addEventListener('wheel', e => { if (e.ctrlKey || e.metaKey) { e.preventDefault(); zoom = Math.max(0.7, Math.min(2, zoom - e.deltaY * 0.002)); } }, { passive: false });
  canvas.addEventListener('keydown', e => { const k = e.key; if (k === 'ArrowLeft') yaw -= 0.1; else if (k === 'ArrowRight') yaw += 0.1; else if (k === 'ArrowUp') pitch = Math.min(1.2, pitch + 0.08); else if (k === 'ArrowDown') pitch = Math.max(-1.2, pitch - 0.08); else return; e.preventDefault(); idle = 300; });
  if ('IntersectionObserver' in window) new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(canvas);
  window.addEventListener('resize', () => { resize(); draw(); });
  if (window.ResizeObserver) new ResizeObserver(() => { resize(); draw(); }).observe(canvas);
  readColors(); resize(); draw(); requestAnimationFrame(loop);
  return { refresh() { readColors(); draw(); }, count: pts.length };
}

/* 2D "Where fire was tested" plot: pressure (kPa) on x, oxygen share (%) on y.
   Many tests share the same oxygen and pressure, so single dots would pile up. Tests that fall in the same small cell are merged into one
   bubble: its AREA grows with the number of tests, and the BLUE share of the bubble is the share of those tests where a flame was lit
   (this includes tests stopped while the flame was still burning); the grey share is no ignition or no recorded outcome.
   x is linear to 120 kPa and compressed above it (tests reach 331 kPa); y runs 10 to 100 % (tests reach 12 %).
   Motion: bubbles pop in as a left-to-right sweep, the lunar-base box draws in and its dashes march slowly, the hovered bubble pulses.
   In calm mode (html.calm) everything is drawn at once and nothing moves. */
function initScatter(canvas, tipEl, rows, opts) {
  'use strict';
  const ctx = canvas.getContext('2d'), all = rows.filter(r => r.t === 'test' && r.o != null && r.p != null);
  const XLIN = 120, XMAX = 350, FRAC = 0.86, YMIN = 10, YMAX = 100, M = { l: 44, r: 16, t: 24, b: 34 }, CELL = 11;
  const FAM = { 'FLEX': 'FLEX', 'CFI-G': 'CFI-G', 'BASS-II': 'BASS-II', 'Saffire': 'Saffire' }, famOf = r => FAM[r.f] || 'REPORTS';
  const famShort = { FLEX: 'FLEX', 'CFI-G': 'CFI-G', 'BASS-II': 'BASS-II', Saffire: 'Saffire', REPORTS: 'reports' };
  let active = new Set(['FLEX', 'CFI-G', 'BASS-II', 'Saffire', 'REPORTS']);
  let W = 0, H = 0, col = {}, hover = null, bins = [], t0 = performance.now(), visible = true, frameT = 0;
  const calm = () => document.documentElement.classList.contains('calm');
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const easeOut = t => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
  const pop = t => { if (t <= 0) return 0; if (t >= 1) return 1; const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
  const lit = r => r.c !== 'no_ignition' && r.c !== 'unknown';
  function colors() {
    const cs = getComputedStyle(document.documentElement), g = n => cs.getPropertyValue(n).trim();
    col = { lit: g('--blue'), dark: g('--c-ni'), ember: g('--ember'), head: g('--head'), muted: g('--muted'), line: g('--line'), panel: g('--panel') };
  }
  function size() { const dpr = Math.min(window.devicePixelRatio || 1, 2), b = canvas.getBoundingClientRect(); W = b.width; H = b.height; canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  const pw = () => W - M.l - M.r;
  const X = p => M.l + (p <= XLIN ? (p / XLIN) * FRAC : FRAC + ((p - XLIN) / (XMAX - XLIN)) * (1 - FRAC)) * pw();
  const Y = o => M.t + (1 - (o * 100 - YMIN) / (YMAX - YMIN)) * (H - M.t - M.b);
  const mono = (px, w) => (w || 400) + ' ' + px + 'px "IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace';
  function rebin() {
    const m = {};
    all.forEach(r => { if (!active.has(famOf(r))) return; const x = X(r.p), y = Y(r.o), k = Math.floor(x / CELL) + ':' + Math.floor(y / CELL);
      const b = m[k] || (m[k] = { n: 0, lit: 0, sx: 0, sy: 0, fam: {}, omin: 9, omax: 0, pmin: 1e9, pmax: 0, rows: [] });
      b.n++; b.sx += x; b.sy += y; if (lit(r)) b.lit++; const f = famOf(r); b.fam[f] = (b.fam[f] || 0) + 1; b.omin = Math.min(b.omin, r.o); b.omax = Math.max(b.omax, r.o); b.pmin = Math.min(b.pmin, r.p); b.pmax = Math.max(b.pmax, r.p); b.rows.push(r); });
    bins = Object.values(m).map(b => { b.x = b.sx / b.n; b.y = b.sy / b.n; b.rad = Math.min(15, 3.6 + 1.55 * Math.sqrt(b.n - 1) + (b.n > 1 ? 1 : 0)); b.top = Object.entries(b.fam).sort((a, c) => c[1] - a[1])[0][0]; return b; });
    bins.sort((a, b) => b.n - a.n);   // big bubbles first so small ones stay visible on top
    bins.reverse();
  }
  function draw(now) {
    now = now || performance.now();
    const age = calm() ? 1e9 : now - t0;
    ctx.clearRect(0, 0, W, H); ctx.font = mono(12); ctx.textBaseline = 'middle'; ctx.lineWidth = 1;
    const gridA = easeOut(age / 500);
    [20, 40, 60, 80, 100].forEach(v => { const y = Y(v / 100); ctx.strokeStyle = col.line; ctx.globalAlpha = 0.7 * gridA; ctx.beginPath(); ctx.moveTo(M.l, y); ctx.lineTo(M.l + pw() * easeOut(age / 700), y); ctx.stroke(); ctx.globalAlpha = gridA; ctx.fillStyle = col.muted; ctx.textAlign = 'right'; ctx.fillText(v, M.l - 8, y); });
    ctx.globalAlpha = gridA; ctx.fillStyle = col.muted; ctx.textAlign = 'center';
    [0, 25, 50, 75, 100].forEach(v => ctx.fillText(v, X(v), H - M.b + 16));
    ctx.fillText('kPa', X(120) + 18, H - M.b + 16);
    ctx.strokeStyle = col.muted; ctx.beginPath(); ctx.moveTo(X(XLIN) - 3, H - M.b - 4); ctx.lineTo(X(XLIN) + 3, H - M.b + 4); ctx.stroke();
    ctx.textAlign = 'left'; ctx.fillText('O₂ %', 4, M.t - 12); ctx.globalAlpha = 1;
    // lunar-base zone: oxygen 30% or more, pressure 10.2 psi (70.33 kPa) or less
    const zk = easeOut((age - 250) / 700), zx = X(0), zy = Y(1), zw = (X(opts.zone.pMaxKpa) - X(0)) * zk, zh = (Y(opts.zone.oMin) - Y(1)) * zk;
    ctx.fillStyle = col.ember; ctx.globalAlpha = 0.12; ctx.fillRect(zx, zy, zw, zh); ctx.globalAlpha = 1;
    ctx.strokeStyle = col.ember; ctx.lineWidth = 1.5; ctx.setLineDash([6, 4]); ctx.lineDashOffset = calm() ? 0 : -((now / 90) % 10); ctx.strokeRect(zx, zy, zw, zh); ctx.setLineDash([]); ctx.lineDashOffset = 0; ctx.lineWidth = 1;
    ctx.globalAlpha = easeOut((age - 900) / 500); ctx.fillStyle = col.ember; ctx.font = mono(12, 500); ctx.textAlign = 'left'; ctx.fillText('LUNAR BASE · ≥30% O₂ · ≤10.2 psi', zx + 10, zy + 22, Math.max(60, X(opts.zone.pMaxKpa) - X(0) - 16)); ctx.globalAlpha = 1;
    // bubbles: area = number of tests, blue wedge = share with a flame lit
    bins.forEach(b => {
      const hot = hover === b, k = pop((age - 350 - ((b.x - M.l) / pw()) * 1000 - (1 - b.omax) * 160) / 450); if (k <= 0 && !hot) return;
      const r = Math.max(0, (hot ? b.rad + 2 + (calm() ? 0 : Math.sin(now / 160) * 1.2) : b.rad) * Math.min(k, 1.12));
      ctx.globalAlpha = hot ? 1 : 0.9 * clamp(k, 0, 1);
      ctx.fillStyle = col.dark; ctx.beginPath(); ctx.arc(b.x, b.y, r, 0, 6.2832); ctx.fill();
      if (b.lit > 0) { ctx.fillStyle = col.lit; ctx.beginPath(); if (b.lit < b.n) ctx.moveTo(b.x, b.y); ctx.arc(b.x, b.y, r, -Math.PI / 2, -Math.PI / 2 + (b.lit / b.n) * 6.2832); if (b.lit < b.n) ctx.closePath(); ctx.fill(); }
      ctx.lineWidth = hot ? 2 : 1.2; ctx.strokeStyle = hot ? col.head : col.panel; ctx.beginPath(); ctx.arc(b.x, b.y, r, 0, 6.2832); ctx.stroke(); ctx.lineWidth = 1;
    });
    ctx.globalAlpha = 1;
    // direct labels on the biggest clusters: count and family
    if (age > 1100) {
      const placed = [[X(101.325) - 22 - 100, Y(0.2095) - 22, 100]], la = easeOut((age - 1100) / 500);   // the Earth-air label is already there
      bins.slice().sort((a, b) => b.n - a.n).filter(b => b.n >= 12).slice(0, 6).forEach(b => {
        const txt = b.n + ' \u00b7 ' + famShort[b.top]; ctx.font = mono(12, 500); const w = ctx.measureText(txt).width;
        const cands = [[b.x + b.rad + 7, b.y], [b.x - b.rad - 7 - w, b.y], [b.x - w / 2, b.y - b.rad - 10], [b.x - w / 2, b.y + b.rad + 11]];   // right, left, above, below
        const pick1 = cands.find(c => c[0] > M.l && c[0] + w < W - M.r && c[1] > M.t && c[1] < H - M.b && !placed.some(p => c[0] < p[0] + p[2] + 4 && c[0] + w > p[0] - 4 && Math.abs(c[1] - p[1]) < 14));
        if (!pick1) return; placed.push([pick1[0], pick1[1], w]);
        ctx.globalAlpha = la; ctx.textAlign = 'left'; ctx.lineWidth = 3.5; ctx.strokeStyle = col.panel; ctx.strokeText(txt, pick1[0], pick1[1]); ctx.fillStyle = col.head; ctx.fillText(txt, pick1[0], pick1[1]); ctx.lineWidth = 1;
      }); ctx.globalAlpha = 1;
    }
    // reference markers fade in last
    ctx.globalAlpha = easeOut((age - 1300) / 500);
    const sx = X(opts.suit.p), sy = Y(opts.suit.o), lx2 = Math.min(X(opts.zone.pMaxKpa) + 14, W - M.r - 150);
    ctx.strokeStyle = col.head; ctx.lineWidth = 1.8; ctx.beginPath(); ctx.arc(sx, sy, 6, 0, 6.2832); ctx.stroke(); ctx.lineWidth = 1;
    ctx.strokeStyle = col.muted; ctx.setLineDash([2, 3]); ctx.beginPath(); ctx.moveTo(sx + 7, sy); ctx.lineTo(sx + 7 + (lx2 - 4 - sx - 7) * easeOut((age - 1400) / 500), sy); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = col.head; ctx.font = mono(12, 500); ctx.textAlign = 'left'; ctx.fillText('SPACESUIT · NO TEST', lx2, sy);
    const ex = X(101.325), ey = Y(0.2095);
    ctx.strokeStyle = col.head; ctx.lineWidth = 1.8; ctx.setLineDash([3, 2]); ctx.beginPath(); ctx.arc(ex, ey, 17, 0, 6.2832); ctx.stroke(); ctx.setLineDash([]); ctx.lineWidth = 1;
    ctx.fillStyle = col.head; ctx.textAlign = 'right'; ctx.fillText('EARTH AIR 21%', ex - 22, ey - 22);
    ctx.globalAlpha = 1;
  }
  function pick(x, y) { let b = null, bd = 1e9; bins.forEach(c => { const e = Math.hypot(c.x - x, c.y - y); if (e < c.rad + 5 && e < bd) { bd = e; b = c; } }); return b; }
  function pos(e) { const b = canvas.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; }
  function tip(b) {
    if (!b) { tipEl.style.display = 'none'; return; }
    tipEl.style.display = 'block';
    if (b.n === 1) { const r = b.rows[0]; tipEl.textContent = (r.i || r.f) + ' | ' + (r.m || '?') + ' | O2 ' + (r.o * 100).toFixed(1) + '% | ' + r.p.toFixed(1) + ' kPa | ' + (r.g === '?' ? 'gravity not stated' : r.g + ' g') + ' | ' + (opts.label[r.c] || r.c); return; }
    const fams = Object.entries(b.fam).sort((a, c) => c[1] - a[1]).map(e => e[0] + ' ' + e[1]).join(', '), o = (b.omin * 100).toFixed(0) + (b.omax > b.omin + 0.004 ? '-' + (b.omax * 100).toFixed(0) : ''), p = b.pmin.toFixed(0) + (b.pmax > b.pmin + 1 ? '-' + b.pmax.toFixed(0) : '');
    tipEl.textContent = b.n + ' tests | ' + fams + ' | O2 ' + o + '% | ' + p + ' kPa | flame lit in ' + b.lit + ', no ignition or no recorded outcome in ' + (b.n - b.lit);
  }
  canvas.addEventListener('pointermove', e => { const p = pos(e); hover = pick(p[0], p[1]); tip(hover); canvas.style.cursor = hover ? 'pointer' : 'default'; draw(); });
  canvas.addEventListener('pointerleave', () => { hover = null; tip(null); draw(); });
  canvas.addEventListener('pointerdown', e => { const p = pos(e); hover = pick(p[0], p[1]); tip(hover); draw(); });
  function loop(now) { if (visible && !document.hidden && W > 0 && !calm() && now - frameT > 30) { frameT = now; draw(now); } requestAnimationFrame(loop); }
  if ('IntersectionObserver' in window) new IntersectionObserver(es => { const v = es[0].isIntersecting; if (v && !visible) t0 = performance.now(); visible = v; }).observe(canvas);
  const relayout = () => { size(); rebin(); draw(); };
  window.addEventListener('resize', relayout);
  if (window.ResizeObserver) new ResizeObserver(() => { const was = W; size(); rebin(); if (!was && W) t0 = performance.now(); draw(); }).observe(canvas);
  const famCounts = {}; all.forEach(r => { const f = famOf(r); famCounts[f] = (famCounts[f] || 0) + 1; });
  colors(); size(); rebin(); draw(); requestAnimationFrame(loop);
  return { refresh() { colors(); relayout(); }, replay() { t0 = performance.now(); draw(); }, setFamilies(list) { active = new Set(list); hover = null; tip(null); rebin(); t0 = performance.now() - 900; draw(); }, famCounts, count: all.length, bubbles() { return bins.length; } };
}
