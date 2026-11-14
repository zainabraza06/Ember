"""Orchestrates the M2 harmonization: raw PSI tables + transcribed CSVs -> data/processed/tests.{csv,parquet}.

Deterministic: no timestamps, stable ordering, so reruns produce byte-identical CSV and report files.
Usage (repo root):  python -m pipeline [--write-expected]
"""
import collections
import csv
import hashlib
import json
import sys

from .checks import EXPECTED, counts, run_checks
from .common import PROCESSED, RAW_PSI, ROOT, TRANSCRIBED, fmt, rel
from .psi import build_bass2, build_cfig, build_flex, build_saffire
from .schema import COLUMNS, NUMERIC
from .transcribed import build_transcribed

FAMILY_ORDER = ['FLEX', 'CFI-G', 'BASS-II', 'BASS', 'Saffire', 'partial_gravity_literature', 'screening_1g']
HASHED_DIRS = ['data/transcribed', 'data/llm', 'data/review']


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    rows, notes = [], {}
    for name, fn in (('FLEX', build_flex), ('CFI-G', build_cfig), ('BASS-II', build_bass2),
                     ('Saffire', build_saffire), ('transcribed', build_transcribed)):
        r, info = fn()
        rows.extend(r)
        notes[name] = info
    for r in rows:  # canonical numeric text (e.g. 0.0 and 0 both become 0)
        for c in NUMERIC:
            if r.get(c) not in ('', None):
                r[c] = fmt(float(r[c]))
    for r in rows:  # source anomalies are flagged, never corrected
        if r['oxygen_fraction'] != '' and r['oxygen_fraction_final'] != '' and r['record_type'] == 'test' and r['data_origin'] == 'psi_table':
            if abs(float(r['oxygen_fraction_final']) - float(r['oxygen_fraction'])) > 0.03:
                r['quality_flags'] = ';'.join(sorted(set(r['quality_flags'].split(';')) - {''} | {'o2_final_differs_from_initial_by_more_than_3pct'}))
    rows.sort(key=lambda r: (FAMILY_ORDER.index(r['family']), r['test_id']))
    return rows, notes, run_checks(rows)


def write_parquet(rows, path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    cols = {}
    for c in COLUMNS:
        if c in NUMERIC:
            cols[c] = pa.array([float(r[c]) if r[c] != '' else None for r in rows], type=pa.float64())
        else:
            cols[c] = pa.array([r[c] for r in rows], type=pa.string())
    pq.write_table(pa.table(cols), path, compression='zstd')


def write(rows, notes):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / 'tests.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    write_parquet(rows, PROCESSED / 'tests.parquet')
    flags = collections.Counter(q for r in rows for q in r['quality_flags'].split(';') if q)
    inputs = {}
    for p in sorted(RAW_PSI.glob('PSI-*/*Experimental table*.csv')):
        inputs[rel(p)] = sha256(p)
    for d in HASHED_DIRS:
        for p in sorted((ROOT / d).rglob('*.csv')):
            inputs[rel(p)] = sha256(p)
    report = {
        'output': rel(out), 'output_sha256': sha256(out), 'parquet': 'data/processed/tests.parquet',
        **{k: v for k, v in counts(rows).items() if k != 'rows'}, 'rows': len(rows),
        'rows_by_record_type': dict(collections.Counter(r['record_type'] for r in rows)),
        'rows_by_gravity_level_g': {k or '(empty)': v for k, v in sorted(collections.Counter(r['gravity_level_g'] for r in rows).items())},
        'bass2_outcome_proposals': {
            'proposed_class_by_confidence': {f'{k[0]}|{k[1]}': v for k, v in sorted(collections.Counter(
                (r['outcome_class_proposed'], r['outcome_proposal_confidence']) for r in rows if r['family'] == 'BASS-II').items())},
            'review_status': dict(collections.Counter(r['outcome_review_status'] for r in rows if r['family'] == 'BASS-II')),
        },
        'quality_flag_counts': dict(sorted(flags.items())),
        'source_notes': notes,
        'input_sha256': inputs,
        'excluded': {'PSI-10': 'decision D6 (license unknown)', 'PSI-26 (BASS)': 'decision D13 (evidence ledger only)'},
    }
    with open(PROCESSED / 'build_report.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write('\n')
    return report


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        import pyarrow  # noqa: F401  (required for the Parquet output)
    except ImportError:
        print('pyarrow is required for the Parquet output: pip install -r requirements.txt', file=sys.stderr)
        return 2
    if '--write-expected' in argv:  # explicit human act after reviewing the counts
        rows, notes, problems = build()
        problems = [p for p in problems if not p.startswith('count check failed') and 'expected_counts.json is missing' not in p]
        if problems:
            print(f'{len(problems)} problem(s); not writing expected counts:', *problems[:30], sep='\n  ', file=sys.stderr)
            return 1
        EXPECTED.write_text(json.dumps(counts(rows), indent=1, sort_keys=True) + '\n', encoding='utf-8')
        print(f'wrote {EXPECTED.name}')
        return 0
    rows, notes, problems = build()
    if problems:
        print(f'DATA CHECKS FAILED: {len(problems)} problem(s); nothing written.', file=sys.stderr)
        for p in problems[:60]:
            print('  ', p, file=sys.stderr)
        return 1
    rep = write(rows, notes)
    print(f"wrote {rep['output']} and tests.parquet: {rep['rows']} rows; all data checks passed")
    for k, v in rep['by_family'].items():
        print(f'  {k}: {v}')
    return 0
