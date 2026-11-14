"""Mission atmosphere profiles from the official challenge text (docs/CHALLENGE.md, Potential Considerations).

The psi values are the official numbers; kPa is computed here (1 psi = 6.894757 kPa), never typed by hand.
Writes data/processed/mission_profiles.json: each profile with its envelope and how many rows of tests.csv fall inside it.
Rows without oxygen or pressure are counted as 'not testable', never guessed.
Run from the repo root: python -m pipeline.profiles"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PSI_TO_KPA = 6.894757
SOURCE = ('Official challenge text, Potential Considerations (docs/CHALLENGE.md): '
          'https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/')

PROFILES = [
    {'id': 'lunar_base', 'name': 'Lunar base (planned)', 'o2_min': 0.30, 'o2_max': None, 'p_max_psi': 10.2, 'p_min_psi': None,
     'statement': 'oxygen likely 30% or greater, pressure 10.2 psi or less'},
    {'id': 'pressurized_rover', 'name': 'Pressurized rover (planned)', 'o2_min': 0.30, 'o2_max': None, 'p_max_psi': 10.2, 'p_min_psi': None,
     'statement': 'oxygen likely 30% or greater, pressure 10.2 psi or less'},
    {'id': 'spacesuit', 'name': 'Spacesuit', 'o2_min': 1.0, 'o2_max': 1.0, 'p_max_psi': 4.3, 'p_min_psi': 4.3,
     'statement': '100% oxygen at 4.3 psi'},
]
REFERENCE = {'name': 'Earth sea level (reference in the same text)', 'p_psi': 14.7}
SUIT_PRESSURE_TOLERANCE_KPA = 0.5   # a test reported at "4.3 psi" may carry rounding; only used for the suit's lower bound


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def inside(p, row):
    """True / False, or None when the row has no oxygen or no pressure."""
    o2, pk = num(row['oxygen_fraction']), num(row['pressure_kpa'])
    if o2 is None or pk is None:
        return None
    ok = o2 >= p['o2_min'] - 1e-9 and (p['o2_max'] is None or o2 <= p['o2_max'] + 1e-9)
    ok = ok and pk <= p['p_max_kpa'] + SUIT_PRESSURE_TOLERANCE_KPA * (p['p_min_kpa'] is not None)
    if p['p_min_kpa'] is not None:
        ok = ok and pk >= p['p_min_kpa'] - SUIT_PRESSURE_TOLERANCE_KPA
    return ok


def build():
    with open(ROOT / 'data/processed/tests.csv', encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['record_type'] == 'test']
    out = {'source': SOURCE, 'conversion': '1 psi = 6.894757 kPa',
           'reference': dict(REFERENCE, p_kpa=round(REFERENCE['p_psi'] * PSI_TO_KPA, 2)), 'profiles': []}
    for p in PROFILES:
        p = dict(p)
        p['p_max_kpa'] = p['p_max_psi'] * PSI_TO_KPA
        p['p_min_kpa'] = None if p['p_min_psi'] is None else p['p_min_psi'] * PSI_TO_KPA
        by_family, unknown = {}, 0
        for r in rows:
            v = inside(p, r)
            if v is None:
                unknown += 1
            elif v:
                d = by_family.setdefault(r['family'], {'tests': 0, 'gravity_levels': set(), 'outcomes': {}})
                d['tests'] += 1
                d['gravity_levels'].add(r['gravity_level_g'] or 'not stated')
                d['outcomes'][r['outcome_class']] = d['outcomes'].get(r['outcome_class'], 0) + 1
        for d in by_family.values():
            d['gravity_levels'] = sorted(d['gravity_levels'])
        p['tests_inside_by_family'] = by_family
        p['tests_inside_total'] = sum(d['tests'] for d in by_family.values())
        p['tests_without_oxygen_or_pressure'] = unknown
        p['p_max_kpa'] = round(p['p_max_kpa'], 2)
        p['p_min_kpa'] = None if p['p_min_kpa'] is None else round(p['p_min_kpa'], 2)
        out['profiles'].append(p)
    out['tests_considered'] = len(rows)
    (ROOT / 'data/processed/mission_profiles.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return out


if __name__ == '__main__':
    o = build()
    for p in o['profiles']:
        print(p['id'], p['p_max_kpa'], 'kPa;', p['tests_inside_total'], 'tests inside;', p['tests_inside_by_family'])
