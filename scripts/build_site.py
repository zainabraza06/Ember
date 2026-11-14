"""Build the static dashboard: site/index.html from data/catalog.csv, data/raw/psi/*/info.md, data/processed/tests.csv and
data/processed/mission_profiles.json (run `python -m pipeline` and `python -m pipeline.profiles` first).

Everything shown is read from those files or from docs/CHALLENGE.md (official text). Anything not in them is shown as
"not documented in the catalog"; nothing is guessed. Run from the repo root: python scripts/build_site.py"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = 'https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/'
ND = 'not documented in the catalog'

# ---- Tags (G2). Reasons come from the official Background / Potential Considerations text, or from the investigation metadata.
TAGS = {
    'PSI-26': [('prevention', 'official Background: solid materials were studied in BASS, BASS-II, Saffire-I, -II, -III')],
    'PSI-25': [('prevention', 'official Background: solid materials were studied in BASS, BASS-II, Saffire-I, -II, -III')],
    'PSI-98': [('prevention', 'official Background: solid materials were studied in BASS, BASS-II, Saffire-I, -II, -III')],
    'PSI-99': [('prevention', 'official Background: solid materials were studied in BASS, BASS-II, Saffire-I, -II, -III')],
    'PSI-100': [('prevention', 'official Background: solid materials were studied in BASS, BASS-II, Saffire-I, -II, -III')],
    'PSI-20': [('prevention', 'official Potential Considerations: BRE studies materials flammability in still atmospheres as a function of material properties')],
    'PSI-62': [('prevention', 'investigation metadata: models concurrent flame spread and compares it with BASS data')],
    'PSI-102': [('detection', 'official Background: detection is SAME and SAME-R')],
    'PSI-101': [('detection', 'official Background: detection is SAME and SAME-R')],
    'PSI-47': [('detection', 'official Potential Considerations: DAFT and DAFT-2 are dust detection with the SAME instrument')],
    'PSI-115': [('detection', 'investigation metadata: simulates pyrolysis smoke growth in a geometry similar to the SAME experiments')],
    'PSI-69': [('suppression', 'official Background: suppression is FLEX (dilution with carbon dioxide and helium)')],
    'PSI-68': [('suppression', 'investigation metadata: FLEX-2 extends FLEX and studies flame extinction mechanisms and their boundaries')],
}
# ---- Hardware groups (G1), from the official Potential Considerations; others from the catalog platform column.
HW = {}
for i in ('PSI-10', 'PSI-20', 'PSI-21', 'PSI-22', 'PSI-23', 'PSI-159'):
    HW[i] = ('ACME / CIR', 'official: ACME is six experiments with gaseous fuels in the Combustion Integrated Rack (CIR)')
for i in ('PSI-69', 'PSI-68', 'PSI-39'):
    HW[i] = ('MDCA / CIR', 'official: FLEX, FLEX-2 and CFI burn liquid droplets in the Multi-user Droplet Combustion Apparatus (MDCA) in the CIR')
for i in ('PSI-25', 'PSI-26', 'PSI-107', 'PSI-106'):
    HW[i] = ('MSG flow duct', 'official: BASS, BASS-II, SPICE and SLICE use the Microgravity Science Glovebox (MSG); fan-driven flow duct built for SPICE')
for i in ('PSI-98', 'PSI-99', 'PSI-100'):
    HW[i] = ('Saffire (Cygnus)', 'catalog platform column (Saffire flew on Cygnus; not one of the official hardware groups)')
for i in ('PSI-101', 'PSI-102'):
    HW[i] = ('MSG (SAME)', 'catalog platform column: Microgravity Science Glovebox, SAME hardware (not one of the official hardware groups)')
HW['PSI-47'] = ('ISS (SAME precursor)', 'catalog platform column: "ISS" only (not one of the official hardware groups)')
for i in ('PSI-60', 'PSI-62', 'PSI-115', 'PSI-117', 'PSI-142'):
    HW[i] = ('Ground analysis', 'catalog platform column: ground analysis or modelling, no flight hardware')


def read_csv(p):
    with open(ROOT / p, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def sections(md):
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(r'## (.+)', line)
        if m:
            cur = re.sub(r' \(.*', '', m.group(1)).strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: '\n'.join(v).strip() for k, v in out.items()}


def header(md, key):
    m = re.search(rf'^- {re.escape(key)}: (.+)$', md, re.M)
    return m.group(1).strip() if m else ''


def rng(vals, fmt='{:g}'):
    v = [float(x) for x in vals if x not in ('', None)]
    return None if not v else (fmt.format(min(v)) if min(v) == max(v) else fmt.format(min(v)) + ' to ' + fmt.format(max(v)))


def summarize_tests(rows):
    if not rows:
        return None
    t = [r for r in rows if r['record_type'] == 'test']
    mats = {}
    for r in t:
        if r['material_or_fuel']:
            mats[r['material_or_fuel']] = mats.get(r['material_or_fuel'], 0) + 1
    geoms = sorted({r['sample_geometry'] for r in t if r['sample_geometry']})
    oc = {}
    for r in t:
        oc[r['outcome_class']] = oc.get(r['outcome_class'], 0) + 1
    size = {}
    for k, lab in (('sample_thickness_mm', 'thickness mm'), ('sample_width_cm', 'width cm'), ('sample_length_cm', 'length cm')):
        v = rng([r[k] for r in t])
        if v:
            size[lab] = v
    return {'tests': len(t), 'o2': rng([r['oxygen_fraction'] for r in t], '{:.3g}'), 'pressure_kpa': rng([r['pressure_kpa'] for r in t], '{:.4g}'),
            'flow_cm_s': rng([r['flow_velocity_cm_s'] for r in t], '{:.3g}'), 'gravity_g': sorted({r['gravity_level_g'] or 'not stated' for r in t}),
            'fuels': sorted(mats, key=lambda m: -mats[m])[:12], 'n_fuels': len(mats), 'geometry': geoms, 'sizes': size, 'outcomes': oc,
            'source_refs': sorted({r['source_ref'].split('#')[0] for r in t})[:4]}


def main():
    catalog = {r['item_id'].split(' ')[0]: r for r in read_csv('data/catalog.csv') if r['source'] == 'NASA PSI'}
    tests = read_csv('data/processed/tests.csv')
    by_psi = {}
    for r in tests:
        pid = r['psi_id'] or ('PSI-69' if r['family'] == 'FLEX' else '')
        if pid:
            by_psi.setdefault(pid, []).append(r)
    invs = []
    for d in sorted((ROOT / 'data/raw/psi').glob('PSI-*'), key=lambda p: int(p.name.split('-')[1])):
        pid = d.name
        md = (d / 'info.md').read_text(encoding='utf-8')
        sec = sections(md)
        cat = catalog.get(pid, {})
        title = re.sub(r'^# PSI-\d+: ', '', md.splitlines()[0])
        table_files = [f.name for f in d.glob('*.csv')]
        hw = HW.get(pid, (ND, ''))
        invs.append({
            'id': pid, 'title': title, 'acronym': header(md, 'Acronym'), 'platform': header(md, 'Platform') or cat.get('platform', ND),
            'license': header(md, 'License (PSI record)'), 'doi': header(md, 'DOI'),
            'psi_url': header(md, 'Source URL'), 'objective': sec.get('Objective', ND), 'approach': sec.get('Approach', ND),
            'conditions_varied': sec.get('Conditions varied', ND), 'outcomes_measured': sec.get('Outcomes measured', ND),
            'known_problems': sec.get('Known problems', ''), 'hardware': hw[0], 'hardware_basis': hw[1],
            'tags': [{'tag': t, 'reason': r} for t, r in TAGS.get(pid, [])],
            'table_type': cat.get('has_test_table', ND), 'approx_tests': cat.get('approx_test_count', ND), 'material_class': cat.get('material_class', ND),
            'table_files': table_files, 'tests_summary': summarize_tests(by_psi.get(pid)), 'catalog_notes': cat.get('notes', '')})
    # ---- partial gravity (G4)
    pairs = {}
    for r in tests:
        if r['pair_id']:
            pairs.setdefault(r['pair_id'], {})['1g' if r['test_id'].endswith(':1g') else '0g'] = {
                k: r[k] for k in ('test_id', 'material_or_fuel', 'oxygen_fraction', 'pressure_kpa', 'flow_velocity_cm_s', 'gravity_level_g', 'outcome_raw',
                                  'outcome_class', 'spread_rate', 'spread_rate_basis', 'burn_duration_s', 'source_ref', 'quality_flags', 'alt_value_report')}
    lit = [{k: r[k] for k in ('test_id', 'record_type', 'material_or_fuel', 'gravity_level_g', 'oxygen_fraction', 'pressure_kpa', 'uloi_vol_pct', 'moc_vol_pct',
                              'o2_margin_vs_1g_pct', 'limit_criterion', 'outcome_raw', 'outcome_class', 'source_ref')}
           for r in tests if r['family'] == 'partial_gravity_literature' and r['gravity_level_g'] in ('0.165', '0.38')]
    grav_counts = {}
    for r in tests:
        k = r['gravity_level_g'] or 'not stated'
        grav_counts.setdefault(k, {'psi': 0, 'outside_psi': 0})
        grav_counts[k]['psi' if r['psi_id'] else 'outside_psi'] += 1   # rows without a PSI id come from NTRS reports or the 1 g screening tables
    profiles = json.loads((ROOT / 'data/processed/mission_profiles.json').read_text(encoding='utf-8'))
    atmos = [{k: r[k] for k in ('item_id', 'title', 'license', 'url')} for r in read_csv('data/catalog.csv') if r['item_id'] in ('20260002050', '20130013505', '20150021491', 'NASA/TP-2010-216134')]
    pil = next((i for i in invs if i['id'] == 'PSI-20'), {})
    quote = ''
    m = re.search(r'NASA - considered atmosphere[^\n]*?34 % oxygen', pil.get('objective', ''))
    if m:
        quote = m.group(0)
    # ---- atmosphere map points, ranking, interpretations, ledger claims (all produced by the pipeline and the ledger)
    points = [{'id': r['test_id'], 'f': r['family'], 'psi': r['psi_id'], 'o': float(r['oxygen_fraction']), 'p': float(r['pressure_kpa']),
               'g': r['gravity_level_g'] or '?', 'c': r['outcome_class'], 's': r['source_ref'], 'org': r['data_origin']}
              for r in tests if r['record_type'] == 'test' and r['oxygen_fraction'] and r['pressure_kpa']]
    no_atm = sum(1 for r in tests if r['record_type'] == 'test') - len(points)
    # oxygen-limit rows (MOC: the oxygen share at the flammability limit for that pressure) are drawn as bars, labelled as limits
    for r in tests:
        if r['record_type'] == 'limit' and r['moc_vol_pct'] and r['pressure_kpa']:
            points.append({'id': r['test_id'], 'f': r['family'], 'psi': '', 'o': float(r['moc_vol_pct']) / 100.0, 'p': float(r['pressure_kpa']), 'g': r['gravity_level_g'] or '?',
                           'c': 'limit', 's': r['source_ref'], 'org': r['data_origin']})
    def fl(v):
        try:
            return float(v) if v not in ('', None) else None
        except ValueError:
            return None
    # compact copy of the unified table for the Ask page (tests and oxygen-limit rows; limits use the limit oxygen share)
    ask_rows = [{'i': r['psi_id'] or ('PSI-69' if r['family'] == 'FLEX' else ''), 'f': r['family'], 'm': r['material_or_fuel'],
                 'o': fl(r['oxygen_fraction']) if r['record_type'] == 'test' else (fl(r['moc_vol_pct']) / 100.0 if fl(r['moc_vol_pct']) is not None else None),
                 'p': fl(r['pressure_kpa']), 'g': r['gravity_level_g'] or '?', 'c': r['outcome_class'], 's': r['source_ref'], 't': r['record_type'], 'org': r['data_origin']}
                for r in tests if r['record_type'] in ('test', 'limit')]
    ranking = json.loads((ROOT / 'data/processed/ranking.json').read_text(encoding='utf-8'))
    interp = json.loads((ROOT / 'data/processed/interpretations.json').read_text(encoding='utf-8'))
    claims, ledger_stats, srcs = [], {}, {}
    cp = ROOT / 'data/ledger/claims.jsonl'
    if cp.exists():
        import sys
        sys.path.insert(0, str(ROOT))
        from ledger import config as lcfg
        from ledger import display as ldisp
        with open(lcfg.SOURCES_CSV, encoding='utf-8') as f:
            srcs = {r['doc_id']: {k: r[k] for k in ('doc_id', 'ntrs_id', 'title', 'year', 'url', 'display_verbatim', 'rights_determination')} for r in csv.DictReader(f)}
        allc = ldisp.load_claims(cp)
        for c in allc:
            ledger_stats[c['status']] = ledger_stats.get(c['status'], 0) + 1
        rp = ROOT / 'data/ledger/rejected.jsonl'
        ledger_stats['rejected'] = sum(1 for _ in open(rp, encoding='utf-8')) if rp.exists() else 0
        pub = ldisp.public_claims(allc, ldisp.load_sources())
        gmap = {c['claim_id']: c['conditions']['gravity_class'] for c in allc}
        for v in pub:
            v['gravity_class'] = gmap[v['claim_id']]
            v['doc'] = next(c['doc_id'] for c in allc if c['claim_id'] == v['claim_id'])
        claims = pub
    conflicts_md = (ROOT / 'docs/CONFLICTS.md').read_text(encoding='utf-8') if (ROOT / 'docs/CONFLICTS.md').exists() else ''
    data = {'points': points, 'points_without_atmosphere': no_atm, 'ranking': ranking, 'interpretations': interp, 'claims': claims,
            'ledger_stats': ledger_stats, 'sources': srcs, 'conflicts': [l for l in conflicts_md.splitlines() if l.startswith('| PSI-')],
            'official': OFFICIAL, 'nd': ND, 'investigations': invs, 'pairs': [dict(id=k, **v) for k, v in sorted(pairs.items())], 'literature': lit,
            'tests': ask_rows, 'gravity_counts': grav_counts, 'profiles': profiles, 'atmos_reports': atmos, 'bre_quote': quote,
            'build': {'tests_rows': len(tests), 'investigations': len(invs)}}
    tpl = (ROOT / 'scripts/site_template.html').read_text(encoding='utf-8')
    out = ROOT / 'site' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    parser_js = (ROOT / 'scripts/ask_parser.js').read_text(encoding='utf-8').replace('</', '<\\/')
    out.write_text(tpl.replace('/*__ASK_PARSER__*/', parser_js).replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
    print('wrote', out, len(invs), 'investigations;', len(pairs), 'pairs;', len(lit), 'literature rows;', quote[:80])


if __name__ == '__main__':
    main()
