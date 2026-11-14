/* Deterministic query parser and test-table filter for the Ask page. No model, no network.
   Inlined into the site by scripts/build_site.py and unit-tested through Node (tests/test_ask_parser.py).
   Units: oxygen is a mole fraction (0-1) inside the filters; pressure is kPa. */
(function (root) {
  'use strict';
  const PSI = 6.894757, ATM = 101.325, MMHG = 0.133322;
  const O2_TOL = 0.005;      // "at 30% oxygen" matches 29.5% to 30.5%
  const P_TOL = 0.03;        // "at 10.2 psi" matches within 3 percent

  function toKpa(v, unit) {
    const u = unit.toLowerCase();
    if (u === 'kpa') return v;
    if (/^psi/.test(u)) return v * PSI;
    if (u === 'atm') return v * ATM;
    if (u === 'mmhg' || u === 'torr') return v * MMHG;
    if (u === 'bar') return v * 100;
    return null;
  }

  const RX = {
    minEx: /(above|over|greater than|more than|higher than|exceeding|exceeds|more oxygen than)\s*$|>(?!=)\s*$/i,
    maxEx: /(below|under|less than|lower than|fewer than)\s*$|<(?!=)\s*$/i,
    minIn: /(at least|no less than|not less than|minimum of|minimum|min\.?|from)\s*$|(>=|≥)\s*$/i,
    maxIn: /(at most|no more than|not more than|maximum of|maximum|max\.?|up to)\s*$|(<=|≤)\s*$/i,
    minPost: /^\s*(?:oxygen|o2|o₂)?\s*(or more|or greater|or higher|or above|and above|and higher|and over|\+)/i,
    maxPost: /^\s*(?:oxygen|o2|o₂)?\s*(or less|or lower|or below|and below|and lower|and under)/i
  };
  // words that can sit between an operator and its number: "above about 30%", "at least 30% oxygen"
  const FILLER = /(oxygen|o2|o₂|pressure|concentration|level|content|of|about|around|approximately|roughly|~|is|at)\s*$/i;

  function mode(pre, post) {
    let p = pre;
    for (let i = 0; i < 3; i++) { const q = p.replace(FILLER, ''); if (q === p) break; p = q; }
    p = p.replace(/\s+$/, ' ');
    if (RX.minIn.test(p) || RX.minPost.test(post)) return 'min';
    if (RX.maxIn.test(p) || RX.maxPost.test(post)) return 'max';
    if (RX.minEx.test(p)) return 'minEx';
    if (RX.maxEx.test(p)) return 'maxEx';
    return 'eq';
  }

  function spec(kind, mode_, a, b, label) {
    // kind 'o' (fraction) or 'p' (kPa); returns {min,max,minEx,maxEx,label}
    const tol = kind === 'o' ? O2_TOL : null;
    const f = { label };
    if (mode_ === 'range') { f.min = Math.min(a, b); f.max = Math.max(a, b); }
    else if (mode_ === 'min') f.min = a;
    else if (mode_ === 'minEx') { f.min = a; f.minEx = true; }
    else if (mode_ === 'max') f.max = a;
    else if (mode_ === 'maxEx') { f.max = a; f.maxEx = true; }
    else { const d = tol !== null ? tol : a * P_TOL; f.min = a - d; f.max = a + d; f.eq = a; }
    return f;
  }

  const NUM = '(\\d+(?:\\.\\d+)?)';
  const UNIT_O = '(%|percent|per cent|pct)';
  const UNIT_P = '(psia|psig|psi|kpa|atm|mmhg|torr|bar)';
  const SEP = '\\s*(?:-|–|—|to|and)\\s*';

  function fmt(n, d) { return String(Math.round(n * Math.pow(10, d)) / Math.pow(10, d)); }
  function oLabel(f, raw) {
    const r = (x) => fmt(x * 100, 1);
    if (f.min !== undefined && f.max !== undefined && f.eq === undefined) return 'O2 ' + r(f.min) + ' to ' + r(f.max) + '%';
    if (f.eq !== undefined) return 'O2 about ' + r(f.eq) + '% (' + r(f.min) + ' to ' + r(f.max) + ')';
    if (f.min !== undefined) return 'O2 ' + (f.minEx ? 'above ' : 'at least ') + r(f.min) + '%';
    return 'O2 ' + (f.maxEx ? 'below ' : 'at most ') + r(f.max) + '%';
  }
  function pLabel(f, raw) {
    const k = (x) => fmt(x, 1);
    if (f.min !== undefined && f.max !== undefined && f.eq === undefined) return 'Pressure ' + k(f.min) + ' to ' + k(f.max) + ' kPa' + (raw ? ' (' + raw + ')' : '');
    if (f.eq !== undefined) return 'Pressure about ' + k(f.eq) + ' kPa' + (raw ? ' (' + raw + ')' : '') + ', range ' + k(f.min) + ' to ' + k(f.max);
    if (f.min !== undefined) return 'Pressure ' + (f.minEx ? 'above ' : 'at least ') + k(f.min) + ' kPa' + (raw ? ' (' + raw + ')' : '');
    return 'Pressure ' + (f.maxEx ? 'below ' : 'at most ') + k(f.max) + ' kPa' + (raw ? ' (' + raw + ')' : '');
  }

  const GRAV = [
    ['0.165', /\b(lunar|moon|0\.165\s*g)\b/i],
    ['0.38', /\b(mars|martian|0\.38\s*g)\b/i],
    ['0', /(micro-?\s?gravity|zero[- ]g(?:ravity)?|weightless|free-?\s?fall|\b0\s?g\b|\bug\b|µ\s?g)/i],
    ['1', /(\b1\s?-?g\b|normal gravity|earth gravity|terrestrial|ground[- ]based|1 g\b)/i]
  ];
  // Environment words mean an atmosphere envelope, not a gravity: lunar base, rover and habitat use the official envelope
  // (oxygen 30% or more, pressure 10.2 psi or less, docs/CHALLENGE.md); cabin uses the team-defined ISS-like cabin profile.
  const ENVS = [
    ['lunar', /\b(?:lunar|moon)\s+(?:base|habitat|outpost|surface base)\b|\b(?:pressuri[sz]ed\s+)?rovers?\b|\bhabitat\b/ig, 'lunar base / rover atmosphere (oxygen 30% or more, pressure 10.2 psi or less)', { o: { min: 0.30 }, p: { max: 70.33 } }],
    ['cabin', /\b(?:iss[- ]like\s+|space\s+station\s+)?cabin\b/ig, 'ISS-like cabin atmosphere (team-defined: oxygen 19-25%, pressure within 10% of sea level)', { o: { min: 0.19, max: 0.25 }, p: { min: 91.22, max: 111.49 } }]
  ];
  const DIL = [['co2', /(\bco2\b|\bco₂\b|carbon dioxide)/i, 'CO2'], ['he', /(\bhelium\b|\bHe\b)/, 'helium'], ['n2', /(\bnitrogen\b|\bn2\b)/i, 'nitrogen']];
  const DESCRIPTORS = new Set(['fabric']);          // describes a material, does not identify one ("SIBAL fabric")
  const GLABEL = { '0': 'microgravity (0 g)', '1': '1 g', '0.165': 'lunar gravity (0.165 g, outside PSI)', '0.38': 'Mars gravity (0.38 g, outside PSI)' };

  const OUT = [
    ['no_ignition', /\b(no ignition|not ignite|did not ignite|didn't ignite|fail(?:s|ed)? to ignite|won't ignite|does not ignite|do not ignite)\b/i, 'did not ignite'],
    ['self_extinguished', /\b(self[- ]?extinguish\w*|extinguish\w*|goes? out|went out|flame out|quench\w*)\b/i, 'self-extinguished'],
    ['burned_to_completion', /\b(burn(?:s|ed)? (?:to completion|completely|entirely|fully)|complete(?:ly)? burn\w*|burned to completion)\b/i, 'burned to completion'],
    ['ignited', /\b(ignit(?:e|es|ed|ion))\b/i, 'ignited']
  ];
  const IGNITED = ['self_extinguished', 'burned_to_completion', 'externally_terminated'];

  const STOP = new Set('the and for with was were are not from that this than then when what which how does did can could should would will into over under between about have has had been being its their there these those also any all some more most less least above below near around roughly approximately test tests tested testing material materials fuel fuels sample samples burn burns burned burning burnt flame flames oxygen pressure gravity micro psi kpa atm percent per cent happen happens what\'s whats who why where show list give tell find'.split(' '));
  const ALIAS = { acrylic: 'pmma', plexiglas: 'pmma', plexiglass: 'pmma', perspex: 'pmma' };

  function words(s) { return (s.toLowerCase().match(/[a-z][a-z0-9-]*/g) || []); }

  function parseQuery(q, vocab) {
    const text = String(q || '');
    let work = text;                                    // consumed numeric spans are blanked
    const out = { query: text, o: null, p: null, g: null, materials: [], outcomes: [], outcomeLabels: [], plainBurn: false, numeric: false, chips: [], residual: '' };
    const blank = (m) => { work = work.slice(0, m.index) + ' '.repeat(m[0].length) + work.slice(m.index + m[0].length); };

    // pressure ranges, then single pressures
    let m, rg = new RegExp(NUM + SEP + NUM + '\\s*' + UNIT_P + '\\b', 'ig');
    while ((m = rg.exec(work)) !== null) {
      const a = toKpa(parseFloat(m[1]), m[3]), b = toKpa(parseFloat(m[2]), m[3]);
      if (a === null) continue;
      out.p = spec('p', 'range', a, b); out.p.label = pLabel(out.p, m[1] + ' to ' + m[2] + ' ' + m[3]);
      blank(m); rg.lastIndex = 0;
    }
    const rp = new RegExp(NUM + '\\s*' + UNIT_P + '\\b', 'ig');
    while (!out.p && (m = rp.exec(work)) !== null) {
      const v = toKpa(parseFloat(m[1]), m[2]); if (v === null) continue;
      const md = mode(work.slice(Math.max(0, m.index - 30), m.index), work.slice(m.index + m[0].length, m.index + m[0].length + 16));
      out.p = spec('p', md, v); out.p.label = pLabel(out.p, /^kpa$/i.test(m[2]) ? '' : m[1] + ' ' + m[2]);
      blank(m); rp.lastIndex = 0;
    }
    // oxygen ranges, then single values with a percent sign
    rg = new RegExp(NUM + SEP + NUM + '\\s*' + UNIT_O, 'ig');
    while (!out.o && (m = rg.exec(work)) !== null) {
      out.o = spec('o', 'range', parseFloat(m[1]) / 100, parseFloat(m[2]) / 100); out.o.label = oLabel(out.o);
      blank(m); rg.lastIndex = 0;
    }
    const ro = new RegExp(NUM + '\\s*' + UNIT_O + '(?![a-z])', 'ig');
    while (!out.o && (m = ro.exec(work)) !== null) {
      const md = mode(work.slice(Math.max(0, m.index - 30), m.index), work.slice(m.index + m[0].length, m.index + m[0].length + 16));
      out.o = spec('o', md, parseFloat(m[1]) / 100); out.o.label = oLabel(out.o);
      blank(m); ro.lastIndex = 0;
    }
    // oxygen without a unit: "O2 >= 30", "oxygen above 30", "oxygen 0.3", "O2 between 25 and 35"
    if (!out.o) {
      const rr = new RegExp('(?:o2|o₂|oxygen)\\s*(?:concentration|level|fraction|content)?\\s*(?:between\\s*)?' + NUM + SEP + NUM + '(?![\\d.]*\\s*(?:psi|kpa|atm))', 'ig');
      if ((m = rr.exec(work)) !== null) {
        const a = parseFloat(m[1]), b = parseFloat(m[2]), sc = Math.max(a, b) > 1 ? 100 : 1;
        out.o = spec('o', 'range', a / sc, b / sc); out.o.label = oLabel(out.o); blank(m);
      }
    }
    if (!out.o) {
      const r1 = new RegExp('((?:o2|o₂|oxygen)(?:\\s*(?:concentration|level|fraction|content))?\\s*)((?:>=|<=|≥|≤|=|>|<|at least|at most|above|below|over|under|up to|of|at|is|about|around)?\\s*)' + NUM + '(?!\\s*(?:psi|psia|kpa|atm|mmhg|torr|bar|g\\b|cm|mm))', 'ig');
      if ((m = r1.exec(work)) !== null) {
        const v = parseFloat(m[3]), sc = v > 1 ? 100 : 1;
        const md = mode(m[1] + m[2], work.slice(m.index + m[0].length, m.index + m[0].length + 16));
        out.o = spec('o', md, v / sc); out.o.label = oLabel(out.o); blank(m);
      }
    }
    // environment words
    let gtext = text;
    out.env = null; out.dil = []; out.dilIntent = false;
    if (!/\b(mars|martian)\b/i.test(text)) {
      for (const [key, rx, label, envSpec] of ENVS) {
        rx.lastIndex = 0;
        if (!rx.test(text)) continue;
        rx.lastIndex = 0; gtext = gtext.replace(rx, ' ');
        out.env = { key, label };
        // explicit numbers win, except a restatement of the envelope boundary ("lunar base at 30% oxygen and 10.2 psi")
        const restO = out.o && out.o.eq !== undefined && envSpec.o.min !== undefined && envSpec.o.max === undefined && Math.abs(out.o.eq - envSpec.o.min) < 1e-9;
        const restP = out.p && out.p.eq !== undefined && envSpec.p.max !== undefined && envSpec.p.min === undefined && Math.abs(out.p.eq - envSpec.p.max) / envSpec.p.max < 0.03;
        if (!out.o || restO) { out.o = Object.assign({ fromEnv: true, label: '' }, envSpec.o); }
        if (!out.p || restP) { out.p = Object.assign({ fromEnv: true, label: '' }, envSpec.p); }
        break;
      }
    }
    // diluent words (FLEX rows carry diluent mole fractions)
    for (const [key, rx, lab] of DIL) { if (rx.test(text)) out.dil.push(key); }
    out.dilIntent = /\b(suppress\w*|dilut\w*|extinguish\w*|inert)\b/i.test(text);
    out.numeric = !!(out.o || out.p);
    out.tableQuery = !!(out.numeric || out.dil.length);

    // gravity
    for (const [g, rx] of GRAV) { if (rx.test(gtext)) { out.g = g; break; } }
    // outcomes
    for (const [cls, rx, lab] of OUT) {
      if (rx.test(text)) {
        if (cls === 'ignited') { if (!out.outcomes.length) { out.outcomes = IGNITED.slice(); out.outcomeLabels = [lab]; } }
        else { out.outcomes = [cls]; out.outcomeLabels = [lab]; break; }
      }
    }
    out.plainBurn = !out.outcomes.length && /\bburn(s|ed|ing)?\b/i.test(text);
    // materials: words that occur in the test table's material names
    const seen = new Set(), vs = vocab || new Set();
    const leftover = [];
    for (let w of words(work)) {
      const a = ALIAS[w] || w;
      const stem = a.length > 3 && a.endsWith('s') && !vs.has(a) ? a.slice(0, -1) : a;
      if (!STOP.has(w) && stem.length >= 3 && vs.has(stem)) { if (!seen.has(stem)) { seen.add(stem); out.materials.push(stem); } }
      else if (!STOP.has(w)) leftover.push(w);
    }
    if (out.materials.length > 1) out.materials = out.materials.filter((x) => !DESCRIPTORS.has(x));
    out.residual = leftover.join(' ');
    out.stripped = work.replace(/\s+/g, ' ').trim();

    if (out.env) out.chips.push({ key: 'env', label: 'Environment: ' + out.env.label });
    if (out.o && !out.o.fromEnv) out.chips.push({ key: 'o', label: out.o.label });
    if (out.p && !out.p.fromEnv) out.chips.push({ key: 'p', label: out.p.label });
    out.dil.forEach((k) => out.chips.push({ key: 'd:' + k, label: 'Diluent: ' + DIL.find((d) => d[0] === k)[2] + ' present' }));
    if (out.g !== null) out.chips.push({ key: 'g', label: 'Gravity: ' + GLABEL[out.g] });
    out.materials.forEach((mw) => out.chips.push({ key: 'm:' + mw, label: 'Material: ' + mw }));
    if (out.outcomes.length) out.chips.push({ key: 'c', label: 'Outcome: ' + out.outcomeLabels[0] });
    return out;
  }

  function within(v, f) {
    if (v === null || v === undefined || isNaN(v)) return false;
    if (f.min !== undefined && (f.minEx ? !(v > f.min) : !(v >= f.min - 1e-9))) return false;
    if (f.max !== undefined && (f.maxEx ? !(v < f.max) : !(v <= f.max + 1e-9))) return false;
    return true;
  }
  function matName(m, w) { return new RegExp('(^|[^a-z])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(m || ''); }

  // rows: {m, o, p, g, c, t}; only record type "test" rows are counted as tests
  function nonNumeric(r, f) {
    if (r.t !== 'test') return false;
    if (f.g !== null && f.g !== undefined && String(r.g) !== String(f.g)) return false;
    for (const w of f.materials || []) if (!matName(r.m, w)) return false;
    if (f.outcomes && f.outcomes.length && f.outcomes.indexOf(r.c) < 0) return false;
    for (const k of f.dil || []) if (!(r.d && r.d[k] > 0)) return false;
    return true;
  }
  function applyFilters(rows, f) {
    const hit = [];
    let noO = 0, noP = 0, noD = 0;
    for (const r of rows) {
      if (!nonNumeric(r, f)) { if (f.dil && f.dil.length && r.t === 'test' && !r.d) noD++; continue; }
      if (f.o && !within(r.o, f.o)) { if (r.o === null || r.o === undefined) noO++; continue; }
      if (f.p && !within(r.p, f.p)) { if (r.p === null || r.p === undefined) noP++; continue; }
      hit.push(r);
    }
    return { hit, noO, noP, noD };
  }
  function target(f) { return f.eq !== undefined ? f.eq : (f.min !== undefined && f.max !== undefined ? (f.min + f.max) / 2 : (f.min !== undefined ? f.min : f.max)); }
  // nearest tested conditions when nothing matches: distance in O2 (5 points = 1 unit) and pressure (10 kPa = 1 unit)
  function nearest(rows, f, n) {
    const to = f.o ? target(f.o) : null, tp = f.p ? target(f.p) : null, scored = [], seen = new Set();
    for (const r of rows) {
      if (!nonNumeric(r, f)) continue;
      let d2 = 0, used = 0;
      if (to !== null) { if (r.o === null || r.o === undefined) continue; d2 += Math.pow((r.o - to) / 0.05, 2); used++; }
      if (tp !== null) { if (r.p === null || r.p === undefined) continue; d2 += Math.pow((r.p - tp) / 10, 2); used++; }
      if (!used) continue;
      scored.push({ r, d: Math.sqrt(d2) });
    }
    scored.sort((a, b) => a.d - b.d);
    const out = [];
    for (const s of scored) {
      const k = [s.r.i, s.r.m, s.r.o, s.r.p, s.r.g].join('|');
      if (seen.has(k)) continue; seen.add(k); out.push(s);
      if (out.length >= n) break;
    }
    return out;
  }
  function split(rows) {
    const s = { no_ignition: 0, self_extinguished: 0, burned_to_completion: 0, externally_terminated: 0, other: 0, unknown: 0 };
    for (const r of rows) s[r.c] = (s[r.c] || 0) + 1;
    return s;
  }
  function vocabFrom(rows) {
    const v = new Set();
    for (const r of rows) for (const w of words(r.m || '')) if (w.length >= 3 && !STOP.has(w)) v.add(w);
    return v;
  }
  function without(f, key) {
    const g = Object.assign({}, f, { materials: (f.materials || []).slice() });
    g.dil = (f.dil || []).slice();
    if (key === 'o') g.o = null; else if (key === 'p') g.p = null; else if (key === 'g') g.g = null;
    else if (key === 'env') { g.env = null; if (g.o && g.o.fromEnv) g.o = null; if (g.p && g.p.fromEnv) g.p = null; }
    else if (key.indexOf('d:') === 0) g.dil = g.dil.filter((x) => x !== key.slice(2));
    else if (key === 'c') { g.outcomes = []; g.outcomeLabels = []; }
    else if (key.indexOf('m:') === 0) g.materials = g.materials.filter((x) => x !== key.slice(2));
    g.numeric = !!(g.o || g.p);
    g.tableQuery = !!(g.numeric || g.dil.length);
    g.chips = f.chips.filter((c) => c.key !== key);
    return g;
  }

  const api = { parseQuery, applyFilters, nearest, split, vocabFrom, without, within, toKpa, GLABEL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.AskParser = api;
})(typeof window !== 'undefined' ? window : globalThis);
