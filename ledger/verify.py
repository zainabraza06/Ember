"""Automatic verification of a claim against the source text: span check, number check, condition check, gravity check, LLM support check."""
import difflib
import json
import re

from . import config
from .schema import norm

_NUM = re.compile(r'(?<![\w.])\d[\d,]*(?:\.\d+)?|(?<![\w.])\.\d+')
# factors by which a printed value may legitimately be converted to the normalized condition fields (prompt rule 5):
# percent -> fraction, psia -> kPa, atm -> kPa, mmHg -> kPa, mm/s or m/s -> cm/s, and the identity
FACTORS = (1.0, 0.01, 6.894757, 101.325, 0.133322, 0.1, 100.0)
COND_KEYS = ('gravity_g', 'oxygen_fraction_min', 'oxygen_fraction_max', 'pressure_kpa_min', 'pressure_kpa_max', 'flow_cm_s_min', 'flow_cm_s_max')


def numbers_in(text):
    out = []
    for m in _NUM.finditer(text or ''):
        try:
            out.append(float(m.group(0).replace(',', '')))
        except ValueError:
            pass
    return out


def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def check_span(span, page, doc_pages):
    """-> {'result': exact|fuzzy|fail, 'score', 'page', 'page_corrected'}; doc_pages = {page_no: text}."""
    ns = norm(span)
    if not ns:
        return {'result': 'fail', 'score': 0.0, 'page': page, 'page_corrected': False}
    if page in doc_pages and ns in norm(doc_pages[page]):
        return {'result': 'exact', 'score': 1.0, 'page': page, 'page_corrected': False}
    for p in sorted(doc_pages):  # the model named the wrong page, but the span exists in the document
        if p != page and ns in norm(doc_pages[p]):
            return {'result': 'exact', 'score': 1.0, 'page': p, 'page_corrected': True}
    best, best_p = 0.0, page
    order = ([page] if page in doc_pages else []) + [q for q in sorted(doc_pages) if q != page]
    n = len(ns)
    for p in order:
        t = norm(doc_pages[p])
        if len(t) < n * 0.8:
            continue
        step = max(1, n // 8)
        for i in range(0, max(1, len(t) - n + 1), step):
            sm = difflib.SequenceMatcher(None, ns, t[i:i + n], autojunk=False)
            if sm.real_quick_ratio() < config.FUZZY_THRESHOLD or sm.quick_ratio() < config.FUZZY_THRESHOLD:
                continue
            r = sm.ratio()
            if r > best:
                best, best_p = r, p
    if best >= config.FUZZY_THRESHOLD:
        return {'result': 'fuzzy', 'score': round(best, 4), 'page': best_p, 'page_corrected': best_p != page}
    return {'result': 'fail', 'score': round(best, 4), 'page': page, 'page_corrected': False}


def check_numbers(texts, span):
    """Every number in the claim texts must appear in the span with the same value (a percent value may be written as a fraction)."""
    sp = numbers_in(span)
    pct = '%' in span or 'percent' in span.lower()
    missing = []
    for t in texts:
        for v in numbers_in(t):
            ok = any(_close(v, s) for s in sp) or (pct and any(_close(v, s / 100.0) for s in sp))
            if not ok and v not in missing:
                missing.append(v)
    return {'result': 'pass' if not missing else 'fail', 'missing': missing}


def check_conditions(cond, span):
    """Each numeric condition value must be derivable from a printed number through one fixed conversion factor."""
    sp = numbers_in(span)
    bad = []
    for k in COND_KEYS:
        v = cond.get(k)
        if v is None:
            continue
        if not any(_close(v, s * f, 0.02) or _close(v, s / f, 0.02) for s in sp for f in FACTORS):
            bad.append(k)
    return {'result': 'pass' if not bad else 'fail', 'fields': bad}


_GRAV = {
    'lunar': re.compile(r'(\blunar|\bmoon\b|0\.16\d?\s*g|1/6\s*g)', re.I),
    'mars': re.compile(r'(\bmars\b|martian|0\.38\s*g)', re.I),
    'microgravity': re.compile(r'(micro-?\s?gravity|low-?\s?gravity|zero[- ]g|weightless|reduced gravity|free[- ]?fall|µ\s?g|\bug\b|\b0\s?g\b)', re.I),
    'earth_1g': re.compile(r'(\b1\s?g\b|normal gravity|earth gravity|terrestrial|ground[- ]based|normal-g|1-g)', re.I),
}


def check_gravity(gclass, span, page_text):
    """lunar/mars/microgravity/earth_1g need a matching word in the span (pass) or on the page (context); else fail."""
    rx = _GRAV.get(gclass)
    if rx is None:
        return {'result': 'pass'}
    if rx.search(span):
        return {'result': 'pass'}
    if rx.search(page_text or ''):
        return {'result': 'context'}
    return {'result': 'fail'}


def context_around(span, page_text, width=None):
    """A window of the page around the span (the whole page text if it is short); keeps the verifier's token use low."""
    width = width or config.VERIFY_CONTEXT_CHARS
    text = page_text or ''
    if len(text) <= 2 * width + len(span):
        return text
    words = span.split()
    i = text.find(' '.join(words[:4])) if words else -1
    if i < 0 and words:
        i = text.find(words[0])
    i = max(i, 0)
    return text[max(0, i - width):i + len(span) + width]


def check_support(client, doc_checksum, claim, page_text, prompt_text, prompt_version):
    user = json.dumps({'claim_statement': claim['statement'], 'claim_variables': claim['variables'], 'claim_conditions': claim['conditions'],
                       'claim_effect_direction': claim['effect_direction'], 'span': claim['span']}, ensure_ascii=False) \
        + '\n\nPAGE TEXT (context):\n' + context_around(claim['span'], page_text)
    e = client.complete('verify', doc_checksum, claim['claim_id'], prompt_version, prompt_text, user, max_tokens=300, tag=claim['doc_id'])
    try:
        o = json.loads(e['content'])
        v = o.get('verdict')
        if v not in ('supported', 'partial', 'unsupported'):
            raise ValueError(v)
        return {'result': v, 'reason': str(o.get('reason', ''))[:300], 'model_version': e['model_version']}
    except (ValueError, TypeError, AttributeError):
        return {'result': 'error', 'reason': 'unparseable verifier output', 'model_version': e.get('model_version', '')}


def decide(c):
    """Status and reasons from the verification record. rejected = span not found or the verifier says unsupported;
    needs_review = any other check not clean; verified_auto = all checks pass."""
    v = c['verification']
    if v['span']['result'] == 'fail':
        return 'rejected', ['span_not_found']
    if v['support']['result'] == 'unsupported':
        return 'rejected', ['support_unsupported']
    reasons = []
    if v['span']['result'] == 'fuzzy':
        reasons.append('fuzzy_span')
    if v['numbers']['result'] == 'fail':
        reasons.append('number_not_in_span')
    if v['conditions']['result'] == 'fail':
        reasons.append('condition_value_not_in_span')
    if v['gravity']['result'] == 'fail':
        reasons.append('gravity_class_not_in_text')
    if v['support']['result'] == 'partial':
        reasons.append('support_partial')
    if v['support']['result'] == 'error':
        reasons.append('support_check_error')
    if c['extraction_confidence'] == 'low':
        reasons.append('low_extraction_confidence')
    if 'span_too_long' in c.get('flags', []):
        reasons.append('span_too_long')
    return ('verified_auto' if not reasons else 'needs_review'), reasons
