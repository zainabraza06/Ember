"""Draws a seeded random sample of 10 transcribed values for a person to verify against the PDFs.

Writes docs/HUMAN_SPOT_CHECK.md with an empty "verified by / result" column. Run from the repo root:
    python scripts/make_human_spot_check.py [--seed 20261019] [--n 10]
Pool: every printed value in the transcribed report tables (data/transcribed/NTRS*.csv) and in the BASS-II sidecars
(Table 5.1, stated pressure). Converted values (kPa etc.) are not in the pool; the value shown is what the report prints.
"""
import argparse
import csv
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'HUMAN_SPOT_CHECK.md'
FIELDS = [('uloi_vol_pct', 'ULOI (vol% O2)'), ('moc_vol_pct', 'MOC (vol% O2)'), ('o2_margin_vs_1g_pct', 'oxygen margin vs 1 g (vol% O2)'),
          ('spread_rate', 'spread rate (mm/s)'), ('burn_duration_s', 'burn time (s)'), ('oxygen_orig', 'oxygen as printed'),
          ('pressure_orig', 'pressure as printed')]
EXT_FIELDS = [('droplet_initial_diameter_mm', 'initial droplet diameter (mm)'), ('extinction_diameter_mm', 'visible flame extinction diameter (mm)'),
              ('burning_rate_mm2_s', 'burning rate (mm2/s)')]


def where(source_ref):
    m = re.match(r'NTRS (\d+), (.+?)(?: \||;|$)', source_ref)
    return (m.group(1), m.group(2)) if m else ('', source_ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20261019)
    ap.add_argument('--n', type=int, default=10)
    a = ap.parse_args()
    pool = []
    for f in sorted((ROOT / 'data/transcribed').glob('NTRS*.csv')):
        with open(f, newline='', encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                rid, loc = where(r['source_ref'])
                for k, label in FIELDS:
                    if r.get(k, ''):
                        pool.append((f'{f.name} / {r["test_id"]}', rid, loc, label, r[k]))
                ext = json.loads(r.get('ext') or '{}')
                for k, label in EXT_FIELDS:
                    if ext.get(k):
                        pool.append((f'{f.name} / {r["test_id"]}', rid, loc, label, ext[k]))
    sc = ROOT / 'data/transcribed/sidecars'
    with open(sc / 'bass2_table5_1.csv', newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            for k, label in (('burn_time_min', 'burn time (min)'), ('initial_o2_vol_pct', 'initial O2 (vol%)'), ('final_o2_vol_pct', 'final O2 (vol%)'),
                             ('velocity_cm_s_list', 'velocity list (cm/s)'), ('spread_rate_mm_s_text', 'spread rate text (mm/s)')):
                pool.append((f'sidecars/bass2_table5_1.csv / {r["test_id"]}', '20210011385', 'PDF p.65 (printed p.57), Table 5.1', label, r[k]))
    rng = random.Random(a.seed)
    sample = rng.sample(pool, a.n)
    L = ['# Human spot check of transcribed values', '',
         f'Seeded random sample (seed {a.seed}) of {a.n} of {len(pool)} printed values transcribed by hand from NASA reports. '
         'For each row, open the report (NTRS id: https://ntrs.nasa.gov/citations/<id>; the PDFs are in `data/raw/ntrs/<id>/`, the two large ones are git-ignored, see their `info.md`), '
         'go to the page and table, and compare the value as printed. Fill in the last two columns (initials and date; OK / mismatch with the value you read). '
         'Any mismatch: correct the transcribed CSV and rerun `python -m pipeline`.', '',
         '| # | file / test | NTRS report | page (PDF page; printed page where known) and table, figure or slide | field | transcribed value | verified by | result |',
         '|---|---|---|---|---|---|---|---|']
    for i, (src, rid, loc, label, val) in enumerate(sample, 1):
        L.append(f'| {i} | `{src}` | {rid} | {loc} | {label} | {val} |  |  |')
    OUT.write_text('\n'.join(L) + '\n', encoding='utf-8')
    print(f'wrote {OUT.relative_to(ROOT)} ({a.n} of {len(pool)} values)')


if __name__ == '__main__':
    main()
