"""Load the hand-transcribed report tables (data/transcribed/*.csv) into the unified schema.

The files already use the unified field names. Rows are passed through unchanged except that
(1) the source_ref is extended with the transcribed file and row, and (2) ext is initialised.
"""
import csv
import json

from .common import TRANSCRIBED, rel
from .schema import COLUMNS


def build_transcribed():
    rows, info = [], {}
    for path in sorted(TRANSCRIBED.glob('NTRS*.csv')):
        with open(path, newline='', encoding='utf-8') as f:
            rd = csv.DictReader(f)
            unknown = [c for c in rd.fieldnames if c not in COLUMNS]
            if unknown:
                raise ValueError(f'{path.name}: columns not in unified schema: {unknown}')
            n_file = 0
            for n, rec in enumerate(rd, 1):
                row = {c: rec.get(c, '') for c in COLUMNS}
                row['source_ref'] = f"{rec['source_ref']} | {rel(path)}#data_row={n}"
                row['ext'] = row['ext'] or '{}'
                row['orig_values'] = row['orig_values'] or '{}'
                rows.append(row)
                n_file += 1
        info[path.name] = {'rows': n_file}
    return rows, info
