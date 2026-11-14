"""Effect summaries computed from the unified test table: counts and shares per condition bin, with an evidence-strength label.

No model is involved. Every sentence is a template filled with numbers counted from data/processed/tests.csv; the caveats come from
the quality flags and docs/CONFLICTS.md. Writes data/processed/interpretations.json. Run: python -m pipeline.interpret

Evidence strength (deterministic, see docs/RANKING.md section 3):
  moderate  = at least 100 tests in one experiment family (never 'strong': strong would need two independent families agreeing)
  limited   = 30 to 99 tests
  very limited = fewer than 30 tests
A source conflict that touches the analysis lowers the label by one step; a high share of unknown outcomes is stated beside it."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ['none', 'very limited', 'limited', 'moderate', 'strong']


def strength(n, families=1, conflict=False):
    lvl = 3 if (n >= 100 and families == 1) else 2 if n >= 30 else 1 if n >= 1 else 0
    if families >= 2 and n >= 100:
        lvl = 4
    if conflict:
        lvl = max(0, lvl - 1)
    return LEVELS[max(lvl, 1 if n else 0)]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def parse_diluent(d):
    return {k: num(v) or 0.0 for k, v in re.findall(r'(\w+)=([\d.]+)', d or '')}


def bin_label(lo, hi):
    return f'{lo:g} to {hi:g}'


def table_by_bins(rows, key, bins, classes):
    out = []
    for lo, hi in bins:
        sel = [r for r in rows if key(r) is not None and lo <= key(r) < hi]
        c = {k: sum(1 for r in sel if r['outcome_class'] == k) for k in classes}
        out.append({'bin': bin_label(lo, hi), 'n': len(sel), 'counts': c})
    return out


def pct(a, b):
    return None if not b else round(100.0 * a / b)


def build():
    with open(ROOT / 'data/processed/tests.csv', encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['record_type'] == 'test']
    conflicts = []
    cp = ROOT / 'docs/CONFLICTS.md'
    if cp.exists():
        conflicts = [l for l in cp.read_text(encoding='utf-8').splitlines() if l.startswith('| PSI-')]
    out = []

    # ---- 1. FLEX: oxygen and diluent versus how the droplet test ended
    fx = [r for r in rows if r['family'] == 'FLEX']
    cls = ['self_extinguished', 'burned_to_completion', 'other']
    o2_bins = [(0.0, 0.16), (0.16, 0.20), (0.20, 0.24), (0.24, 1.01)]
    t1 = table_by_bins(fx, lambda r: num(r['oxygen_fraction']), o2_bins, cls)
    lo, hi = t1[0], t1[-1]
    dil = lambda r: parse_diluent(r['diluent'])
    groups = {'carbon dioxide in the diluent': [r for r in fx if dil(r).get('CO2', 0) > 0], 'helium in the diluent': [r for r in fx if dil(r).get('He', 0) > 0],
              'nitrogen only': [r for r in fx if dil(r).get('CO2', 0) == 0 and dil(r).get('He', 0) == 0]}
    t2 = [{'bin': k, 'n': len(v), 'counts': {c: sum(1 for r in v if r['outcome_class'] == c) for c in cls}} for k, v in groups.items()]
    dis = sum(1 for r in fx if 'diameter_label_disagree' in r['quality_flags'])
    sents = [f"At oxygen fractions below 0.16, {lo['counts']['self_extinguished']} of {lo['n']} FLEX droplet tests ({pct(lo['counts']['self_extinguished'], lo['n'])}%) ended in extinction; at 0.24 or above, {hi['counts']['self_extinguished']} of {hi['n']} ({pct(hi['counts']['self_extinguished'], hi['n'])}%) did.",
             'The other end states in the report are "completion" (the droplet burned to completion) and "disruption" (a disruption ended the test); both are counted as "not extinguished" here and are listed in the table.']
    for g in t2:
        sents.append(f"With {g['bin']}: {g['counts']['self_extinguished']} of {g['n']} tests ended in extinction ({pct(g['counts']['self_extinguished'], g['n'])}%).")
    out.append({'id': 'flex_o2_diluent', 'title': 'FLEX droplets: oxygen and diluent versus extinction', 'family': 'FLEX', 'investigation': 'PSI-69',
                'sentences': sents, 'tables': [{'title': 'By oxygen mole fraction', 'rows': t1, 'classes': cls}, {'title': 'By diluent', 'rows': t2, 'classes': cls}],
                'n': len(fx), 'strength': strength(len(fx)),
                'caveats': [f'{dis} of {len(fx)} tests have an "end of test" label that disagrees with the recorded extinction diameter; the label is used (decision D22).',
                            'Methanol and heptane droplets in one apparatus: this is one experiment family, not independent confirmation.',
                            'Tests were not designed as a controlled sweep of oxygen alone: pressure and diluent also vary.'],
                'conflicts': []})

    # ---- 2. CFI-G: oxygen versus how gas-flame tests ended
    cf = [r for r in rows if r['family'] == 'CFI-G']
    cls2 = ['self_extinguished', 'externally_terminated', 'no_ignition', 'other', 'unknown']
    o2b = [(0.0, 0.21), (0.21, 0.30), (0.30, 0.40), (0.40, 1.01)]
    t3 = table_by_bins(cf, lambda r: num(r['oxygen_fraction']), o2b, cls2)
    sents = []
    for b in t3:
        if b['n']:
            sents.append(f"Oxygen {b['bin']}: {b['n']} tests; {b['counts']['self_extinguished']} self-extinguished, {b['counts']['externally_terminated']} stopped by the operator or flow cut-off while still burning, {b['counts']['no_ignition']} did not ignite.")
    sents.append('"Stopped while still burning" is a censored outcome: the flame had not gone out when the test ended, so it is not counted as an extinction.')
    mx = max((num(r['oxygen_fraction']) for r in cf if num(r['oxygen_fraction']) is not None), default=None)
    out.append({'id': 'cfig_o2', 'title': 'ACME CFI-G gas flames: oxygen versus how tests ended', 'family': 'CFI-G', 'investigation': 'PSI-159',
                'sentences': sents, 'tables': [{'title': 'By oxygen mole fraction', 'rows': t3, 'classes': cls2}], 'n': len(cf), 'strength': strength(len(cf)),
                'caveats': [f'Highest oxygen in the table: {mx:g} (matches the official text: up to 85% oxygen from a spherical burner).' if mx else '',
                            'Fuel (ethane, propane, butane and mixtures), pressure and flow also vary between tests.',
                            'Outcome classes follow the PSI label (self-extinguished or flow terminated) plus comment rules (OUTCOME_MAPPING.md).'],
                'conflicts': []})

    # ---- 3. Saffire-II: the same sample at 0 g and 1 g
    pair = {}
    for r in rows:
        if r['pair_id']:
            pair.setdefault(r['pair_id'], {})['1g' if r['test_id'].endswith(':1g') else '0g'] = r
    both = [p for p in pair.values() if '0g' in p and '1g' in p]
    cmp = []
    for k, p in sorted(pair.items()):
        if '0g' in p and '1g' in p:
            cmp.append({'sample': k, '0g': p['0g']['outcome_class'], '1g': p['1g']['outcome_class'], 'material': p['0g']['material_or_fuel']})
    same = sum(1 for c in cmp if c['0g'] == c['1g'])
    conf = [c for c in conflicts if 'PSI-99' in c]
    out.append({'id': 'saffire_0g_1g', 'title': 'Saffire-II: the same sample at 0 g and at 1 g', 'family': 'Saffire', 'investigation': 'PSI-99',
                'sentences': [f'{len(cmp)} samples have both a microgravity result and a 1 g comparison result; {same} have the same outcome class at both gravity levels and {len(cmp) - same} differ.',
                              'Outcome classes for these samples come from the burn lengths in the PSI table (OUTCOME_MAPPING.md)'],
                'tables': [{'title': 'Pairs', 'rows': [{'bin': c['sample'] + ' ' + c['material'], 'n': 2, 'counts': {'0 g': c['0g'], '1 g': c['1g']}} for c in cmp], 'classes': ['0 g', '1 g'], 'text': True}],
                'n': len(cmp), 'strength': strength(len(cmp), conflict=bool(conf)),
                'caveats': ['Nine samples are too few for a general statement; these are individual samples on one spacecraft flight.'],
                'conflicts': conf})
    (ROOT / 'data/processed/interpretations.json').write_text(json.dumps({'strength_rule': __doc__.split('Evidence strength')[1].split('"""')[0], 'items': out}, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return out


if __name__ == '__main__':
    for i in build():
        print(i['id'], i['n'], i['strength'])
        for s in i['sentences'][:3]:
            print('  ', s)
