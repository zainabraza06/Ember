"""Shared helpers: CSV reading with row tracking, number parsing, conversions, row building."""
import csv
import io
import json
import re
from pathlib import Path

from .schema import COLUMNS

ROOT = Path(__file__).resolve().parent.parent
RAW_PSI = ROOT / 'data' / 'raw' / 'psi'
TRANSCRIBED = ROOT / 'data' / 'transcribed'
PROCESSED = ROOT / 'data' / 'processed'

# Unit conversions (exact definitions; the factor quoted in docs/DATA_DICTIONARY.md is rounded)
KPA_PER_MMHG = 101.325 / 760.0
KPA_PER_BAR = 100.0
KPA_PER_ATM = 101.325
KPA_PER_PSI = 6.894757293168
MM_PER_CM = 10.0
MM_PER_MICRON = 0.001


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def norm_header(h):
    """Collapse internal whitespace so headers with irregular spacing can be looked up reliably."""
    return ' '.join(h.split())


def read_records(path):
    """Read a CSV into (header, records). Each record is (data_row_number, list_of_cells).

    data_row_number is 1-based over ALL records after the header, empty ones included, so spreadsheet row = number + 1.
    The decoding tries UTF-8 then cp1252 (the PSI files contain Windows-1252 characters).
    """
    raw = Path(path).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    rows = list(csv.reader(io.StringIO(text, newline='')))
    header = [norm_header(h) for h in rows[0]]
    return header, [(i, r) for i, r in enumerate(rows[1:], 1)]


class Rec:
    """Accessor for one source record by (stripped) header name."""

    def __init__(self, header, cells):
        self.header = header
        self.cells = cells + [''] * (len(header) - len(cells))
        self._idx = {}
        for i, h in enumerate(header):
            self._idx.setdefault(h, i)

    def get(self, name, default=''):
        i = self._idx.get(norm_header(name))
        return default if i is None else self.cells[i].strip()

    def has(self, name):
        return norm_header(name) in self._idx

    def empty(self):
        return not any(c.strip() for c in self.cells)


def parse_float(text):
    """Parse a plain decimal number. Returns None for blanks, '?', '-', 'n/a' and anything else that is not a number."""
    t = (text or '').strip()
    if t in ('', '?', '-', '--', 'n/a', 'NA', 'none'):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def parse_with_unit(text, units):
    """Parse '20 cm/s' or '145 s' or '0.27 mm'. Returns (value, unit) or (None, None). A bare number gives unit ''."""
    t = (text or '').strip()
    m = re.fullmatch(r'(-?\d*\.?\d+)\s*(' + '|'.join(re.escape(u) for u in units) + r')?', t, flags=re.I)
    if not m:
        return None, None
    return float(m.group(1)), (m.group(2) or '').lower()


def fmt(v, nd=6):
    if v is None or v == '':
        return ''
    if isinstance(v, str):
        return v
    return f'{round(v, nd):.{nd}f}'.rstrip('0').rstrip('.') or '0'


class RowBuilder:
    """Collects one unified row with originals and flags."""

    def __init__(self, **kw):
        self.f = {c: '' for c in COLUMNS}
        self.f.update(record_type='test', gravity_source='assumed', flow_direction='unknown', outcome_class='unknown',
                      data_origin='psi_table')
        self.flags = set()
        self.orig = {}
        self.ext = {}
        self.f.update(kw)

    def set(self, field, value, orig_text=None, column=None, unit=None):
        """Set a unified field; record the original cell text next to it."""
        self.f[field] = fmt(value) if not isinstance(value, str) else value
        if orig_text is not None:
            o = {'value': orig_text}
            if column:
                o['column'] = column
            if unit:
                o['unit'] = unit
            self.orig[field] = o

    def flag(self, *names):
        self.flags.update(names)

    def x(self, name, value, orig=True):
        """Family-specific extension field (kept as originally written)."""
        if value != '':
            self.ext[name] = value

    def row(self):
        r = dict(self.f)
        r['quality_flags'] = ';'.join(sorted(self.flags))
        r['orig_values'] = json.dumps(self.orig, sort_keys=True, ensure_ascii=False)
        r['ext'] = json.dumps(self.ext, sort_keys=True, ensure_ascii=False)
        return r


def source_ref(path, n):
    return f'{rel(path)}#data_row={n}'
