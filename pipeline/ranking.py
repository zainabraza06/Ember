"""Deterministic relevance ranking of the 24 PSI combustion investigations per mission profile. Documented in docs/RANKING.md.

No model is involved: every score is computed from the catalog, the PSI records, the unified test table and the official
challenge text. The weights are the team's judgement and are shown to the user next to every score.
Writes data/processed/ranking.json. Run from the repo root: python -m pipeline.ranking"""
import csv
import json
import math
import re
from pathlib import Path

from .profiles import PSI_TO_KPA

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS = {'atmosphere': 0.35, 'safety_area': 0.20, 'fuel': 0.20, 'data': 0.15, 'gravity': 0.10}
WEIGHT_TEXT = {
    'atmosphere': 'How close the investigation\'s tested atmospheres (oxygen, pressure) are to the profile: 60% share of its rows inside the envelope + 40% nearness of its closest row',
    'safety_area': 'Tagged prevention, detection or suppression (official Background text or record metadata): 1 if tagged, else 0',
    'fuel': 'Fuel type: solid materials 1.0; smoke or aerosol from heated materials 0.6; liquid droplets or gas flames 0.4; ground analysis or unknown 0.2',
    'data': 'Per-test data available in the unified table: min(1, test rows / 100)',
    'gravity': 'Flight data in microgravity 1.0; ground analysis or modelling 0.4 (no investigation has partial-gravity data)',
}
# envelopes: (o2_lo, o2_hi, p_lo_kpa, p_hi_kpa). Lunar base, rover and suit are official; the ISS-like cabin is TEAM-DEFINED (see RANKING.md).
ENVELOPES = {
    'lunar_base': ('Lunar base', 0.30, 1.0, 0.0, 10.2 * PSI_TO_KPA, 'official: oxygen 30% or more, pressure 10.2 psi or less'),
    'pressurized_rover': ('Pressurized rover', 0.30, 1.0, 0.0, 10.2 * PSI_TO_KPA, 'official: oxygen 30% or more, pressure 10.2 psi or less'),
    'spacesuit': ('Spacesuit', 1.0, 1.0, 4.3 * PSI_TO_KPA, 4.3 * PSI_TO_KPA, 'official: 100% oxygen at 4.3 psi'),
    'iss_cabin': ('ISS-like cabin', 0.19, 0.25, 0.9 * 14.7 * PSI_TO_KPA, 1.1 * 14.7 * PSI_TO_KPA, 'team-defined: air-like, oxygen 19-25% and pressure within 10% of Earth sea level (14.7 psi, official reference)'),
}
SCALE_O2, SCALE_P = 0.15, 50.0   # distance scales used by the nearness term


def dist(o2, p, env):
    _, lo2, hi2, lp, hp, _ = env
    d2 = max(lo2 - o2, 0.0, o2 - hi2)
    dp = max(lp - p, 0.0, p - hp)
    return math.hypot(d2 / SCALE_O2, dp / SCALE_P)


def fuel_score(material_class):
    m = (material_class or '').lower()
    if m.startswith('solid'):
        return 1.0, 'solid materials'
    if m.startswith('smoke') or m.startswith('aerosol'):
        return 0.6, 'smoke or aerosol from heated materials'
    if m.startswith('liquid') or m.startswith('gas'):
        return 0.4, 'liquid droplets or gas flames'
    return 0.2, 'ground analysis or fuel not documented'


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def build():
    with open(ROOT / 'data/catalog.csv', encoding='utf-8') as f:
        cat = {r['item_id'].split(' ')[0]: r for r in csv.DictReader(f) if r['source'] == 'NASA PSI'}
    with open(ROOT / 'data/processed/tests.csv', encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['record_type'] == 'test']
    by = {}
    for r in rows:
        pid = r['psi_id'] or ('PSI-69' if r['family'] == 'FLEX' else '')
        if pid:
            by.setdefault(pid, []).append(r)
    # tags and hardware come from the site builder's tables so the two never disagree
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts' / 'build_site.py')
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    out = {'weights': WEIGHTS, 'weight_text': WEIGHT_TEXT, 'profiles': {}}
    for pk, env in ENVELOPES.items():
        items = []
        for pid in sorted(cat, key=lambda i: int(i.split('-')[1])):
            c = cat[pid]
            rr = [r for r in by.get(pid, []) if num(r['oxygen_fraction']) is not None and num(r['pressure_kpa']) is not None]
            ds = [dist(num(r['oxygen_fraction']), num(r['pressure_kpa']), env) for r in rr]
            if rr:
                inside = sum(1 for d in ds if d == 0.0) / len(rr)
                near = max(max(0.0, 1.0 - d) for d in ds)
                atm = 0.6 * inside + 0.4 * near
                atm_note = f'{len(rr)} rows with oxygen and pressure; {round(inside * 100)}% inside; closest row distance {min(ds):.2f}'
            else:
                atm, atm_note = 0.0, 'no per-test oxygen and pressure in the unified table (not scored from record text)'
            tags = [t for t, _ in bs.TAGS.get(pid, [])]
            fs, fnote = fuel_score(c['material_class'])
            n_tests = len(by.get(pid, []))
            ground = c['platform'].lower().startswith('ground')
            comp = {'atmosphere': atm, 'safety_area': 1.0 if tags else 0.0, 'fuel': fs, 'data': min(1.0, n_tests / 100.0), 'gravity': 0.4 if ground else 1.0}
            notes = {'atmosphere': atm_note, 'safety_area': ', '.join(tags) or 'untagged', 'fuel': fnote + f' ({c["material_class"][:60]})',
                     'data': f'{n_tests} test rows', 'gravity': 'ground analysis or modelling' if ground else 'flight, microgravity'}
            total = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
            items.append({'id': pid, 'score': round(100 * total, 1), 'components': {k: round(v, 3) for k, v in comp.items()},
                          'points': {k: round(100 * WEIGHTS[k] * comp[k], 1) for k in WEIGHTS}, 'notes': notes})
        items.sort(key=lambda x: (-x['score'], int(x['id'].split('-')[1])))
        for i, it in enumerate(items, 1):
            it['rank'] = i
        out['profiles'][pk] = {'name': env[0], 'envelope': {'o2_min': env[1], 'o2_max': env[2], 'p_min_kpa': round(env[3], 2), 'p_max_kpa': round(env[4], 2)},
                               'basis': env[5], 'items': items}
    (ROOT / 'data/processed/ranking.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return out


if __name__ == '__main__':
    o = build()
    for pk, p in o['profiles'].items():
        print(pk, [(i['id'], i['score']) for i in p['items'][:6]])
