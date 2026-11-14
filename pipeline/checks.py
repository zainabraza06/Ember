"""Automated data checks run on every build (M2). Any failure stops the build loudly and nothing is written.

Checks: allowed values and numeric parsing (schema.validate_row), plausible ranges (unit sanity), unique test_id,
no row without source_ref, pair_id integrity, the human-review rule for LLM proposals, and row counts per family and per
outcome class against pipeline/expected_counts.json (update that file deliberately with `python -m pipeline --write-expected`
after reviewing a change).
"""
import collections
import json
from pathlib import Path

from .schema import validate_row

EXPECTED = Path(__file__).resolve().parent / 'expected_counts.json'

# Plausible ranges per numeric field (unit sanity: catches mmHg/kPa, %/fraction or cm/mm mix-ups)
RANGES = {
    'oxygen_fraction': (0.0, 1.0), 'oxygen_fraction_final': (0.0, 1.0),
    'pressure_kpa': (5.0, 400.0), 'gravity_level_g': (0.0, 1.1),
    'flow_velocity_cm_s': (0.0, 100.0), 'burn_duration_s': (0.0, 7200.0), 'spread_rate': (0.0, 50.0),
    'sample_thickness_mm': (0.0, 100.0), 'sample_width_cm': (0.0, 200.0), 'sample_length_cm': (0.0, 200.0),
    'uloi_vol_pct': (0.0, 100.0), 'moc_vol_pct': (0.0, 100.0), 'o2_margin_vs_1g_pct': (-30.0, 30.0),
}
# Tighter ranges per family for the structured families: values outside mean a unit or column mix-up
FAMILY_RANGES = {
    'FLEX': {'oxygen_fraction': (0.10, 0.40), 'pressure_kpa': (65.0, 320.0), 'burn_duration_s': (0.0, 60.0)},
    'CFI-G': {'oxygen_fraction': (0.10, 0.90), 'pressure_kpa': (45.0, 340.0), 'burn_duration_s': (0.0, 400.0)},
    'BASS-II': {'oxygen_fraction': (0.10, 0.25), 'pressure_kpa': (95.0, 105.0)},
    'Saffire': {'oxygen_fraction': (0.20, 0.23), 'flow_velocity_cm_s': (15.0, 35.0), 'burn_duration_s': (0.0, 1000.0)},
}


def counts(rows):
    return {
        'rows': len(rows),
        'by_family': dict(sorted(collections.Counter(r['family'] for r in rows).items())),
        'by_outcome_class': dict(sorted(collections.Counter(r['outcome_class'] for r in rows).items())),
        'by_family_and_outcome_class': {f'{k[0]}|{k[1]}': v for k, v in sorted(collections.Counter((r['family'], r['outcome_class']) for r in rows).items())},
    }


def run_checks(rows):
    problems = []
    seen = collections.Counter(r['test_id'] for r in rows)
    problems += [f'duplicate test_id {k} (x{v})' for k, v in seen.items() if v > 1]
    for r in rows:
        problems += validate_row(r)
        if not r['source_ref'].strip():
            problems.append(f"{r['test_id']}: empty source_ref")
        for field, (lo, hi) in RANGES.items():
            v = r.get(field, '')
            if v not in ('', None) and not lo <= float(v) <= hi:
                problems.append(f"{r['test_id']}: {field}={v} outside plausible range {lo}..{hi}")
        for field, (lo, hi) in FAMILY_RANGES.get(r['family'], {}).items():
            v = r.get(field, '')
            if r['data_origin'] == 'psi_table' and v not in ('', None) and not lo <= float(v) <= hi:
                problems.append(f"{r['test_id']}: {field}={v} outside the expected range for {r['family']} ({lo}..{hi})")
        # only human-approved LLM proposals may set an outcome class (D12)
        if r['family'] == 'BASS-II' and r['outcome_class'] != 'unknown' and r['outcome_review_status'] not in ('approved', 'changed'):
            problems.append(f"{r['test_id']}: BASS-II outcome_class {r['outcome_class']} without an approved review")
    pairs = collections.defaultdict(list)
    for r in rows:
        if r['pair_id']:
            pairs[r['pair_id']].append(r)
    for pid, rs in pairs.items():
        g = sorted(r['gravity_level_g'] for r in rs)
        if len(rs) != 2 or g != ['0', '1']:
            problems.append(f'pair_id {pid}: expected one 0 g and one 1 g row, got {[(r["test_id"], r["gravity_level_g"]) for r in rs]}')
    if EXPECTED.exists():
        exp = json.loads(EXPECTED.read_text(encoding='utf-8'))
        got = counts(rows)
        for key in ('rows', 'by_family', 'by_outcome_class', 'by_family_and_outcome_class'):
            if exp.get(key) != got[key]:
                problems.append(f'count check failed for {key}: expected {exp.get(key)} got {got[key]}')
    else:
        problems.append(f'{EXPECTED.name} is missing: run `python -m pipeline --write-expected` once after reviewing the counts')
    return problems
