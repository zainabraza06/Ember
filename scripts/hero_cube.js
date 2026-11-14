/* Interactive 3D view of the real test table (no library, no network): x = pressure, y = oxygen share, z = experiment family.
   The translucent box is the planned lunar-base atmosphere from the official text (oxygen 30% or more, pressure 10.2 psi or less).
   Drag to rotate; hover or tap a point for its row. Inlined by scripts/build_site.py. */
function initCube(canvas, tipEl, rows, opts) {
  'use strict';
  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
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
      if (!reduce && !drag && idle <= 0) yaw += 0.0035; else if (idle > 0) idle -= 1;
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
  readColors(); resize(); draw(); requestAnimationFrame(loop);
  return { refresh() { readColors(); draw(); }, count: pts.length };
}
