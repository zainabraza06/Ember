"""Claim record: controlled vocabularies, normalization, stable IDs, validation of the model's raw output. See docs/LEDGER_SCHEMA.md."""
import hashlib
import re
import unicodedata

VARIABLES = ['oxygen_concentration', 'pressure', 'flow_velocity', 'flow_direction', 'gravity_level', 'material', 'sample_thickness',
             'sample_geometry', 'ignition', 'flame_spread_rate', 'burn_time', 'extinction', 'flame_temperature', 'blowoff', 'radiation',
             'fuel_type', 'diluent', 'other']
GRAVITY_CLASSES = ['microgravity', 'lunar', 'mars', 'partial_other', 'earth_1g', 'not_stated']
EFFECTS = ['increases', 'decreases', 'no_effect', 'threshold', 'not_applicable']
EVIDENCE_TYPES = ['measurement', 'observation', 'model', 'review']
CONFIDENCE = ['high', 'medium', 'low']
STATUSES = ['verified_auto', 'needs_review', 'approved', 'rejected']
COND_NUM = ['gravity_g', 'oxygen_fraction_min', 'oxygen_fraction_max', 'pressure_kpa_min', 'pressure_kpa_max', 'flow_cm_s_min', 'flow_cm_s_max']
COND_TXT = ['material', 'geometry']
MAX_SPAN = 600


def norm(s):
    """Matching form of a text: NFKC, lowercase, only letters, digits and '.' kept. Whitespace, hyphens, line-break hyphenation,
    quotes and the replacement character of broken PDF encodings all disappear, identically on both sides of a comparison."""
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[^a-z0-9.]+', '', s)


def claim_id(doc_id, page, span, ordinal=0):
    """Stable ID from document, page and the normalized span only (not the model's wording). Claims that share one span get a
    letter suffix in the order of their normalized statements."""
    h = hashlib.sha1(f'{doc_id}|{page}|{norm(span)}'.encode('utf-8')).hexdigest()[:10]
    return f'C-{h}' + ('' if ordinal == 0 else '-' + 'bcdefghij'[ordinal - 1])


def _num(v):
    if v is None or v == '' or isinstance(v, bool):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return 'bad'


def clean_raw_claim(raw, pages_in_chunk):
    """Validate one raw claim from the model. Returns (claim_dict or None, [problems]). Never fills in missing content."""
    problems = []
    if not isinstance(raw, dict):
        return None, ['not_an_object']
    span = raw.get('span')
    statement = raw.get('statement')
    if not isinstance(span, str) or not span.strip():
        return None, ['missing_span']
    if not isinstance(statement, str) or not statement.strip():
        return None, ['missing_statement']
    try:
        page = int(raw.get('page'))
    except (TypeError, ValueError):
        return None, ['missing_page']
    if page not in pages_in_chunk:
        problems.append('page_outside_chunk')
    if len(span) > MAX_SPAN:
        problems.append('span_too_long')
    vars_ = [v for v in (raw.get('variables') or []) if isinstance(v, str)]
    unk = [v for v in vars_ if v not in VARIABLES]
    if unk:
        problems.append('variable_not_in_vocabulary:' + ','.join(unk))
    vars_ = [v if v in VARIABLES else 'other' for v in vars_] or ['other']
    cond_in = raw.get('conditions') if isinstance(raw.get('conditions'), dict) else {}
    cond = {}
    for k in COND_NUM:
        v = _num(cond_in.get(k))
        if v == 'bad':
            problems.append(f'condition_not_numeric:{k}')
            v = None
        cond[k] = v
    for k in COND_TXT:
        v = cond_in.get(k)
        cond[k] = v.strip() if isinstance(v, str) and v.strip() else None
    gc = cond_in.get('gravity_class')
    if gc not in GRAVITY_CLASSES:
        problems.append('gravity_class_invalid')
        gc = 'not_stated'
    cond['gravity_class'] = gc

    def enum(key, allowed, default):
        v = raw.get(key)
        if v not in allowed:
            problems.append(f'{key}_invalid')
            return default
        return v

    def text(key):
        v = raw.get(key)
        return v.strip() if isinstance(v, str) else ''
    claim = {
        'page': page, 'locator': text('locator'), 'span': span.strip(), 'statement': statement.strip(), 'variables': vars_,
        'conditions': cond, 'effect_direction': enum('effect_direction', EFFECTS, 'not_applicable'), 'magnitude_text': text('magnitude_text'),
        'evidence_type': enum('evidence_type', EVIDENCE_TYPES, 'observation'),
        'extraction_confidence': enum('extraction_confidence', CONFIDENCE, 'low'),
    }
    return claim, problems
