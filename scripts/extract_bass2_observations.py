"""Extract the "Test observations and anomalies" column of NTRS 20210011385 Appendix A (Tables A.1-A.6).

Development-time tool. Requires PyMuPDF (pip install pymupdf; AGPL/commercial licence, not a runtime dependency of
the product, see docs/THIRD_PARTY.md). Its OUTPUT (data/transcribed/sidecars/bass2_observations.csv) is what the
pipeline reads. Tests listed in PSI-25 but not found in the appendix are written with an empty observation.

Usage (repo root):  python scripts/extract_bass2_observations.py
"""
import csv
import io
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / 'data' / 'raw' / 'ntrs' / '20210011385' / 'TM-20210011385.pdf'
PSI25 = next((ROOT / 'data' / 'raw' / 'psi' / 'PSI-25').glob('*Experimental table*.csv'))
OUT = ROOT / 'data' / 'transcribed' / 'sidecars' / 'bass2_observations.csv'
FIRST, LAST = 111, 121          # PDF pages of Appendix A tables A.1-A.6
OBS_LEFT = 970.0                # left edge of the observations column (points); numeric columns end before 967
ID_MAX_X = 400.0                # test numbers sit near x = 170
TABLES = {111: 'A.1', 112: 'A.1', 113: 'A.2', 114: 'A.3', 115: 'A.3', 116: 'A.4', 117: 'A.4', 118: 'A.5', 119: 'A.5', 120: 'A.6', 121: 'A.6'}


def psi_ids():
    raw = PSI25.read_bytes().decode('utf-8-sig')
    return [r[1] for r in list(csv.reader(io.StringIO(raw)))[1:] if r[1]]


def row_borders(page):
    """y positions of the horizontal cell borders that span the observations column."""
    ys = set()
    for dr in page.get_drawings():
        r = dr['rect']
        if r.width > 100 and r.height < 1.5 and r.x0 < OBS_LEFT + 30 and r.x1 > 1100:
            ys.add(round(r.y0, 1))
        for it in dr['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if abs(a.y - b.y) < 0.5 and abs(a.x - b.x) > 100 and min(a.x, b.x) < OBS_LEFT + 30 and max(a.x, b.x) > 1100:
                    ys.add(round(a.y, 1))
    return sorted(ys)


def main():
    ids = psi_ids()
    idset = set(ids)
    doc = fitz.open(str(PDF))
    found = {}
    for pn in range(FIRST, LAST + 1):
        page = doc[pn - 1]
        words = page.get_text('words')
        ys = row_borders(page)
        cells = list(zip(ys[:-1], ys[1:]))[1:]  # the first interval is the table header
        toks = [w for w in words if w[4] in idset and w[0] < ID_MAX_X]
        for w in toks:
            c = (w[1] + w[3]) / 2
            cell = next(((lo, hi) for lo, hi in cells if lo <= c < hi), None)
            if cell is None:
                print(f'WARNING: no cell for {w[4]} on page {pn}', file=sys.stderr)
                continue
            lo, hi = cell
            obs = [x for x in words if x[0] >= OBS_LEFT and lo <= (x[1] + x[3]) / 2 < hi]
            obs.sort(key=lambda x: (round((x[1] + x[3]) / 2 / 3), x[0]))
            text = re.sub(r'\s+', ' ', ' '.join(x[4] for x in obs)).strip()
            found[w[4]] = (pn, TABLES[pn], text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f, lineterminator='\n')
        wr.writerow(['test_id', 'observation_text', 'source_ref', 'extraction_note'])
        for t in ids:
            if t in found:
                pn, tab, text = found[t]
                wr.writerow([f'PSI-25:{t}', text, f'NTRS 20210011385, PDF p.{pn}, Table {tab}, column "Test observations and anomalies"',
                             'extracted by word position from the PDF text layer; whitespace normalized' + ('' if text else '; cell empty or not captured')])
            else:
                wr.writerow([f'PSI-25:{t}', '', 'not found in NTRS 20210011385 Appendix A (PDF p.111-121)', 'test id not found in the appendix text'])
    print(f'{len(found)} of {len(ids)} PSI-25 tests found in Appendix A; empty observations: {sum(1 for v in found.values() if not v[2])}')
    missing = [t for t in ids if t not in found]
    print('not found:', missing)


if __name__ == '__main__':
    sys.exit(main())
