"""Random spot check of data/processed/tests.csv against the sources (M2 acceptance criterion).

Run:  python -m pipeline.spot_check [--n 20] [--seed 20261019] [--out data/processed/spot_check_results.md]
      add --stratified for one row per source file, or --n 99999 to check every row.

For each sampled row the check re-reads the source WITHOUT using the pipeline's mapping code:
  PSI rows         : opens the CSV named in source_ref, takes the record at data_row, and verifies
                     (1) the test_id key, (2) that every recorded original value equals the source cell,
                     (3) every converted value against an independent recomputation, (4) the material label,
                     (5) the outcome_class against an independent small rule table (D10, D11, D14), (6) for BASS-II the
                     enrichment from the report (observation words, Table 5.1 line, stated pressure) on the cited PDF page,
                     (7) pair_id partners.
  transcribed rows : extracts the cited PDF page (or slides) text and verifies that every transcribed number
                     appears there; pdf text needs the optional package pypdf (development tool, not a dependency).
Exit status 1 if any check fails.
"""
import argparse
import csv
import io
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / 'data' / 'processed' / 'tests.csv'


CONVERTIBLE = {'pressure_kpa', 'oxygen_fraction', 'oxygen_fraction_final', 'sample_thickness_mm', 'sample_length_cm',
               'sample_width_cm', 'burn_duration_s', 'flow_velocity_cm_s', 'spread_rate'}


def norm(h):
    return ' '.join(h.split())


def read_source(path):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    rows = list(csv.reader(io.StringIO(text, newline='')))
    return [norm(h) for h in rows[0]], rows[1:]


def tofloat(text):
    t = text.strip().lstrip('~').strip()
    t = re.sub(r'\s*(mmHg|bar|atm|s|cm/s|cm|mm|mm/s|W)$', '', t)
    return float(t)


# expected converted value from the ORIGINAL cell text and the recorded unit
def expected(field, unit, orig):
    v = tofloat(orig)
    if field == 'pressure_kpa':
        return {'mmHg': v * 101.325 / 760.0, 'bar': v * 100.0, 'atm': v * 101.325}[unit]
    if field in ('oxygen_fraction', 'oxygen_fraction_final'):
        return {'vol%': v / 100.0, 'mole fraction': v}[unit]
    if field == 'sample_thickness_mm':
        return {'cm': v * 10.0, 'mm': v}[unit]
    if field in ('sample_length_cm', 'sample_width_cm'):
        return {'cm': v, 'mm': v / 10.0}[unit]
    if field in ('burn_duration_s', 'flow_velocity_cm_s', 'spread_rate'):
        return v
    raise KeyError((field, unit))


def cfig_expected_class(hot, end, bt, cm):
    hot, cm = hot.strip().lower(), cm.lower()
    if hot == 'flash':
        return 'unknown'
    if end == 'SE':
        return 'externally_terminated' if ('hit burner t limit' in cm or 'manually stopped' in cm) else 'self_extinguished'
    if end == 'FT':
        return 'externally_terminated'
    if 'direct cool' in cm or ('abort' in cm and 'did not ignite' not in cm):
        return 'other'
    if hot == 'no' and bt.strip() in ('0', '0.0'):
        return 'no_ignition'
    return 'unknown'


def flex_expected_class(test_end):
    return {'extinction': 'self_extinguished', 'completion': 'burned_to_completion', 'disruption': 'other'}.get(test_end.strip().lower(), 'unknown')


def flex_expected_disagree(test_end, diameter_text):
    lab = test_end.strip().lower()
    try:
        positive = float(diameter_text.strip()) > 0
    except ValueError:
        positive = False
    return (not positive) if lab == 'extinction' else positive if lab in ('completion', 'disruption') else False


_READERS, _PAGE_TEXT = {}, {}


def pdf_pages_text(pdf, pages):
    from pypdf import PdfReader  # optional development tool
    out = []
    for p in pages:
        key = (str(pdf), p)
        if key not in _PAGE_TEXT:
            rd = _READERS.setdefault(str(pdf), PdfReader(str(pdf)))
            _PAGE_TEXT[key] = (rd.pages[p - 1].extract_text() or '') if 1 <= p <= len(rd.pages) else ''
        out.append(_PAGE_TEXT[key])
    return ' '.join(out)


def expand_pages(spec):
    pages = set()
    for part in re.split(r'[,\s]+', spec.strip()):
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-')
            pages.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            pages.add(int(part))
    return sorted(pages)


def num_present(txt, value, allow_no_decimal=False):
    """True if the number appears in txt (tolerating trailing zeros, a dropped leading zero and, optionally, a dropped decimal point)."""
    v = float(value)
    cands = {value, f'{v:g}', f'{v:.1f}', f'{v:.2f}', f'{v:.3f}'}
    cands |= {c[1:] for c in cands if c.startswith('0.')}  # slides print ".92" for 0.92
    if any(re.search(r'(?<![\d.])' + re.escape(c) + r'(?![\d])', txt) for c in cands):
        return True
    if allow_no_decimal:  # some PDF text layers drop the decimal point in figure legends (e.g. "0340 ATM")
        nd = f'{v:.3f}'.replace('.', '')
        return re.search(r'(?<![\d.])' + re.escape(nd) + r'(?![\d])', txt) is not None
    return False


def report_pdf(rid):
    pdfs = sorted((ROOT / 'data' / 'raw' / 'ntrs' / rid).glob('*.pdf'))
    return pdfs[0] if pdfs else None


def check_psi(row, by_id):
    fails, passes = [], []
    m = re.fullmatch(r'(.+\.csv)#data_row=(\d+)', row['source_ref'])
    if not m:
        return [f"source_ref not parseable: {row['source_ref']}"], []
    path, n = ROOT / m.group(1), int(m.group(2))
    header, recs = read_source(path)
    cells = recs[n - 1] + [''] * (len(header) - len(recs[n - 1]))
    def cell(col):
        return cells[header.index(norm(col))].strip()
    fam, tid = row['family'], row['test_id']
    is_1g = tid.endswith(':1g')
    base_tid = tid[:-3] if is_1g else tid
    # (1) key
    if fam == 'FLEX':
        key = f"PSI-69:{int(cell('FLEX Test #')):03d}"
    elif fam == 'CFI-G':
        key = f"PSI-159:{'normal' if 'Normal' in path.name else 'inverse'}:{cell('Test').replace(' ', '')}"
    elif fam == 'BASS-II':
        key = f"PSI-25:{cell('Test #')}"
    else:
        base = f"{row['psi_id']}:{cell('Sample Number')}"
        key = base_tid if base_tid.startswith(base + '-') else base  # a split card keeps a suffix
    (passes if key == base_tid else fails).append(f'test_id {tid} vs source key {key}')
    # (2) originals equal the source cells; (3) conversions
    oj = json.loads(row['orig_values'])
    for field, o in oj.items():
        if 'column' not in o or 'origin' in o:   # report-sourced enrichment: checked in (6)
            continue
        src = cell(o['column'])
        (passes if src == o['value'] else fails).append(f"orig {field}: recorded {o['value']!r} vs source cell {src!r}")
        if field in CONVERTIBLE and row[field] != '' and o.get('unit') not in (None, 'parsed from text'):
            try:
                if 'corrected_value' in o:   # D24: clear error corrected from the report; compare with the stored corrected value
                    got = float(row[field])
                    ok = abs(got - float(o['corrected_value'])) < 1e-9 and o.get('origin') and o.get('source')
                    (passes if ok else fails).append(f"{field}: corrected value {o['corrected_value']} (source cell {o['value']!r}) recorded with origin and source")
                    continue
                ov = o['value']
                if ' and ' in ov:  # card with two materials: value by position (PMMA first, Nomex second)
                    first, second = re.split(r'\s+and\s+', ov, maxsplit=1)
                    ov = first if '-PMMA' in row['test_id'] else second
                exp = expected(field, o['unit'], ov)
            except (KeyError, ValueError) as e:
                fails.append(f'cannot recompute {field}: {e}')
                continue
            got = float(row[field])
            ok = abs(got - exp) <= 1e-4 + 1e-9 * abs(exp)
            (passes if ok else fails).append(f'{field}: pipeline {got:g} vs recomputed {exp:.6g} ({o["value"]} {o["unit"]})')
    for field in ('pressure_kpa', 'oxygen_fraction', 'burn_duration_s', 'flow_velocity_cm_s'):
        if row[field] != '' and field not in oj:
            fails.append(f'{field} has a value but no recorded original')
    # (4) labels
    if fam in ('FLEX', 'CFI-G', 'BASS-II'):
        src_mat = cell('Fuel') if 'Fuel' in header else cell('Fuel Sample Material')
        (passes if row['material_or_fuel'] == src_mat else fails).append(f"material_or_fuel {row['material_or_fuel']!r} vs source cell {src_mat!r}")
    # (5) outcome
    if fam == 'FLEX':
        lab, dx = cell('Test end'), cell('Visible flame extinction diameter; mm')
        exp = flex_expected_class(lab)
        ok = row['outcome_class'] == exp and row['outcome_raw'] == lab
        (passes if ok else fails).append(f"outcome from Test end {lab!r} -> {row['outcome_class']} (expected {exp})")
        dis = flex_expected_disagree(lab, dx)
        (passes if dis == ('diameter_label_disagree' in row['quality_flags']) else fails).append(f"diameter {dx!r} vs label {lab!r}: disagree={dis} matches the flag")
    elif fam == 'CFI-G':
        end = cell('Self -ext or flow term') if 'Self -ext or flow term' in header else cell('Self-ext or flow term')
        exp = cfig_expected_class(cell('Hot ignition'), end, cell('burn time (sec)'), cell('Comments'))
        ok = row['outcome_class'] == exp and f'end={end}' in row['outcome_raw']
        (passes if ok else fails).append(f"outcome end={end} hot={cell('Hot ignition')} -> {row['outcome_class']} (expected {exp})")
    elif fam == 'BASS-II':
        ok = row['outcome_class'] == 'unknown' and row['outcome_review_status'] in ('proposed', 'not_applicable')
        (passes if ok else fails).append('outcome_class unknown until a human approves the LLM proposal')
    elif row['psi_id'] == 'PSI-99':
        if is_1g:
            g1 = cell('1-g Burn Length').lstrip('~ ').lower()
            exp = 'burned_to_completion' if g1 == 'complete' else 'unknown'
            (passes if row['outcome_class'] == exp else fails).append(f"1 g outcome {cell('1-g Burn Length')!r} -> {row['outcome_class']} (expected {exp})")
            rate = cell('1-g Spread Rate')
            if re.fullmatch(r'[\d.]+ mm/s', rate):
                (passes if abs(float(row['spread_rate']) - float(rate.split()[0])) < 1e-9 else fails).append(f'1 g spread_rate {rate!r} -> {row["spread_rate"]}')
            elif row['spread_rate'] != '':
                fails.append(f'1 g spread_rate {row["spread_rate"]} but source cell is {rate!r}')
        elif '-PMMA' not in tid and '-Nomex' not in tid:
            ug = cell('?-g Burn Length')
            length = cell('Sample Length')
            exp = 'burned_to_completion' if (ug == length and ug) else 'unknown'
            (passes if row['outcome_class'] == exp else fails).append(f"outcome ug burn length {ug!r} vs sample length {length!r} -> {row['outcome_class']} (expected {exp})")
            sp = cell('?-g Spread Length')
            if re.fullmatch(r'[\d.]+ mm/s', sp):
                ok = row['spread_rate'] != '' and abs(float(row['spread_rate']) - float(sp.split()[0])) < 1e-9 and 'header_corrected' in row['quality_flags']
                (passes if ok else fails).append(f'spread_rate from column "?-g Spread Length" {sp!r} -> {row["spread_rate"]} with header_corrected')
            bt = cell('Burn Time (s)')
            if not re.fullmatch(r'\d+(\.\d+)?( s)?', bt):
                ok = row['burn_duration_s'] == '' and bt in row['outcome_raw']
                (passes if ok else fails).append(f'non-numeric burn time {bt!r} kept in outcome_raw, burn_duration_s empty')
    # (6) BASS-II enrichment from the report
    if fam == 'BASS-II':
        fails_e, passes_e = check_bass2_enrichment(row, oj)
        fails += fails_e
        passes += passes_e
    # (6b) Saffire corrections and conflicts (D24) against the report
    if row['psi_id'] in ('PSI-98', 'PSI-99') and ('corrected_from_report' in row['quality_flags'] or 'source_conflict' in row['quality_flags']):
        fe, pe = check_saffire_report(row, oj)
        fails += fe
        passes += pe
    # (7) pair partner
    if row['pair_id']:
        partners = [r for r in by_id.values() if r['pair_id'] == row['pair_id']]
        ok = len(partners) == 2 and sorted(r['gravity_level_g'] for r in partners) == ['0', '1']
        (passes if ok else fails).append(f"pair_id {row['pair_id']} has one 0 g and one 1 g row")
    return fails, passes


def check_saffire_report(row, oj):
    """Slide 29 of NTRS 20170008805 must show the corrected values and the conflicting report values."""
    fails, passes = [], []
    pdf = report_pdf('20170008805')
    if pdf is None:
        return ['NTRS 20170008805 PDF missing'], []
    try:
        txt = pdf_pages_text(pdf, [29])
    except ImportError:
        return ['pypdf not installed: pip install pypdf to check report-sourced fields'], []
    sid = row['test_id'].split(':')[1].split(':')[0]
    need = []
    if row['psi_id'] == 'PSI-98':
        need += ['40.6 cm', '94 cm']
    for fld, o in oj.items():
        if 'corrected_value' in o:
            if fld == 'sample_thickness_mm':
                need.append(f"{float(o['corrected_value']):g} mm")
            if fld == 'material_or_fuel':
                need.append(o['corrected_value'])
    if row['alt_value_report']:
        m = re.search(r'=(\S+ ?cm/s|~ ?10 cm)', row['alt_value_report'])
        if m:
            need.append(m.group(1).replace('~10', '~ 10'))
    for n in need:
        (passes if n in txt else fails).append(f'report slide 29 contains {n!r}')
    return fails, passes


def check_bass2_enrichment(row, oj):
    fails, passes = [], []
    ext = json.loads(row['ext'])
    pdf = report_pdf('20210011385')
    if pdf is None:
        return ['BASS-II report PDF missing (git-ignored): download it per data/raw/ntrs/20210011385/info.md to run this check'], []
    try:
        if row['outcome_raw']:
            m = re.search(r'PDF p\.(\d+)', ext.get('observation_source', ''))
            txt = pdf_pages_text(pdf, [int(m.group(1))])
            toks = set(re.findall(r"[A-Za-z0-9.%/'\-]+", txt))
            words = re.findall(r"[A-Za-z0-9.%/'\-]+", row['outcome_raw'])
            missing = [w for w in words if w not in toks and w.strip('.,;') not in toks]
            ok = len(missing) <= max(1, len(words) // 25)
            (passes if ok else fails).append(f'observation words found on PDF p.{m.group(1)} (missing {missing[:5]})')
        if 'table_5_1' in ext:
            line = ' '.join(ext['table_5_1_source'].split())
            txt = pdf_pages_text(pdf, [65])
            t51 = ext['table_5_1']
            tid = row['test_id'].split(':')[1]
            pat = re.compile(r'(?m)^' + re.escape(tid) + r'\s+' + r'\s+'.join(re.escape(x) for x in (t51['thickness_mm'], t51['width_cm'], t51['sides_burning'])) + r'\s')
            (passes if pat.search(txt) else fails).append(f'Table 5.1 row {tid} (thickness, width, sides) present on PDF p.65')
            if row['flow_velocity_cm_s'] != '':
                ok = t51['velocity_cm_s_list'] == f"{float(row['flow_velocity_cm_s']):g}"
                (passes if ok else fails).append(f"flow {row['flow_velocity_cm_s']} equals the single Table 5.1 velocity {t51['velocity_cm_s_list']!r}")
        pk = oj.get('pressure_kpa', {})
        if pk.get('origin') == 'transcribed_from_text':
            m = re.search(r'PDF p\.(\d+)', pk['source'])
            txt = pdf_pages_text(pdf, [int(m.group(1))])
            ok = '1 atm' in txt and abs(float(row['pressure_kpa']) - 101.325) < 1e-9
            (passes if ok else fails).append(f'stated pressure "1 atm" on PDF p.{m.group(1)} -> {row["pressure_kpa"]} kPa (flag nominal: {"nominal" in row["quality_flags"]})')
        elif row['pressure_kpa'] != '':
            fails.append('BASS-II pressure filled without a stated-in-report origin')
    except ImportError:
        fails.append('pypdf not installed: pip install pypdf to check report-sourced fields')
    return fails, passes


def check_transcribed(row):
    fails, passes = [], []
    m = re.match(r'NTRS (\d+), (.+?)(?: \||$)', row['source_ref'])
    if not m:
        return ['source_ref not parseable'], []
    rid, where = m.group(1), m.group(2)
    pdf = report_pdf(rid)
    if pdf is None:
        return [f'no PDF for NTRS {rid} (git-ignored large file?): download it per its info.md'], []
    try:
        if 'slide' in where:
            sp = re.search(r'slides? ([0-9,\- ]+)', where)
            pages = expand_pages(sp.group(1)) if sp else []
        else:
            pages = sorted({q for g in re.findall(r'PDF p\.(\d+(?:-\d+)?)', where) for q in expand_pages(g)})
        if rid == '20170004702':
            pages = [3, 4]
        txt = pdf_pages_text(pdf, pages)
    except ImportError:
        return ['pypdf not installed: pip install pypdf to check transcribed rows'], []
    (passes if pages else fails).append(f'cited pages/slides {pages}')
    for fld in ('uloi_vol_pct', 'moc_vol_pct', 'o2_margin_vs_1g_pct', 'spread_rate', 'oxygen_fraction_final'):
        v = row[fld]
        if v == '':
            continue
        val = float(v) * (100 if fld == 'oxygen_fraction_final' else 1)
        if fld == 'spread_rate' and rid == '20250010653':
            ok = num_present(txt, f'{val:g}') or num_present(txt, f'{val/10:g}')  # slides give mm/s, cm/s or both
        else:
            ok = num_present(txt, f'{val:g}')
        (passes if ok else fails).append(f'{fld}={v} {"found" if ok else "NOT found"} in cited text')
    po = row['pressure_orig']
    mm = re.match(r'([\d.]+) ATM', po)
    if mm:
        (passes if num_present(txt, mm.group(1), allow_no_decimal=True) else fails).append(f'legend pressure {mm.group(1)} atm in cited page (decimal point may be missing in the text layer)')
    mp = re.match(r'([\d.]+) psia', po)
    if mp and rid != '20170004702':
        (passes if num_present(txt, mp.group(1)) else fails).append(f'pressure {mp.group(1)} psia in cited page')
    mh = re.match(r'([\d.]+) mmHg', po)
    if mh:
        (passes if num_present(txt, mh.group(1)) else fails).append(f'pressure {mh.group(1)} mmHg in cited page')
    if row['sample_length_cm'] != '' and rid == '20170004702':
        (passes if num_present(txt, row['sample_length_cm']) else fails).append(f'sample length {row["sample_length_cm"]} cm in cited text')
    ext = json.loads(row['ext'] or '{}')
    for k in ('droplet_initial_diameter_mm', 'extinction_diameter_mm', 'burning_rate_mm2_s', 'cir_identifier'):
        if k in ext and ext[k]:
            ok = ext[k] in txt or num_present(txt, ext[k]) if k != 'cir_identifier' else ext[k] in txt
            (passes if ok else fails).append(f'{k}={ext[k]} found in cited page')
    if rid == '20150023456':  # FLEX report rows: oxygen, burn time and test end
        for fld, lab in (('oxygen_fraction', 'O2'), ('burn_duration_s', 'burn time')):
            if row[fld] != '':
                (passes if num_present(txt, row[fld]) else fails).append(f'{lab} {row[fld]} found in cited page')
        te = ext.get('test_end_raw')
        if te:
            (passes if te in txt else fails).append(f'Test end {te!r} found in cited page (kept raw)')
        dx = ext.get('extinction_diameter_mm', '')
        exp = flex_expected_class(te or '')
        (passes if row['outcome_class'] == exp else fails).append(f'outcome from Test end {te!r} -> {row["outcome_class"]} (expected {exp})')
        dis = flex_expected_disagree(te or '', dx)
        (passes if dis == ('diameter_label_disagree' in row['quality_flags']) else fails).append(f'diameter {dx!r} vs label {te!r}: disagree={dis} matches the flag')
    return fails, passes


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=20)
    ap.add_argument('--seed', type=int, default=20261019)
    ap.add_argument('--out', default=str(ROOT / 'data' / 'processed' / 'spot_check_results.md'))
    ap.add_argument('--stratified', action='store_true', help='one row per source file instead of a simple random sample')
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(TESTS, encoding='utf-8')))
    by_id = {r['test_id']: r for r in rows}
    rng = random.Random(a.seed)
    if a.stratified:
        groups = {}
        for r in rows:
            key = r['source_ref'].split(' | ')[-1].split('#')[0] if r['data_origin'] != 'psi_table' else r['source_ref'].split('#')[0]
            groups.setdefault(key, []).append(r)
        sample = [rng.choice(v) for k, v in sorted(groups.items())]
    else:
        sample = rng.sample(rows, min(a.n, len(rows)))
    mode = 'stratified one-per-source-file' if a.stratified else 'simple random'
    lines = [f'# Spot check results (seed {a.seed}, {mode}, {len(sample)} rows of {len(rows)})', '',
             '| # | test_id | family | data_origin | checks passed | checks failed |', '|---|---|---|---|---|---|']
    detail, bad = [], 0
    for i, r in enumerate(sample, 1):
        f, p = (check_psi(r, by_id) if r['data_origin'] == 'psi_table' else check_transcribed(r))
        bad += bool(f)
        lines.append(f"| {i} | {r['test_id']} | {r['family']} | {r['data_origin']} | {len(p)} | {len(f)} |")
        detail.append(f"### {i}. {r['test_id']}  \nsource_ref: `{r['source_ref']}`  ")
        detail += [f'- PASS {x}' for x in p] + [f'- **FAIL** {x}' for x in f]
        detail.append('')
    lines += ['', f'**Rows with at least one failed check: {bad} of {len(sample)}**', '', '## Details', ''] + detail
    Path(a.out).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(sample)} rows checked; rows with failures: {bad}; details in {a.out}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
