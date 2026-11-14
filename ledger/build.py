"""Orchestration: extraction -> verification -> status -> grouping -> output files. Everything is a function of
(sources, pages, cache, human review decisions), so a rerun without API calls (offline) reproduces the same ledger."""
import collections
import csv
import json

from . import config
from .extract import chunks_for, extract_chunk
from .group import assign_groups
from .llm import STOPS, CacheMiss, log_event
from .pages import load_pages, read_sources
from .schema import claim_id, norm
from .verify import check_conditions, check_gravity, check_numbers, check_span, check_support, decide

FAIL_REASONS = {'span_not_found', 'support_unsupported', 'number_not_in_span', 'condition_value_not_in_span', 'fuzzy_span',
                'gravity_class_not_in_text', 'support_partial', 'support_check_error'}


def prompt(name):
    return (config.PROMPTS_DIR / f'{name}.md').read_text(encoding='utf-8')


def load_decisions():
    """Human decisions from data/review/claim_review.csv: claim_id -> (decision, reviewer, note)."""
    out = {}
    if config.REVIEW_CSV.exists():
        with open(config.REVIEW_CSV, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                d = (r.get('decision') or '').strip().lower()
                if d in ('approved', 'rejected'):
                    out[r['claim_id']] = d
    return out


def load_review_edits():
    """Reviewer edits of approved rows in claim_review.csv: claim_id -> {statement, gravity_class, gravity_label, reviewer, reviewed_on, note}."""
    out = {}
    if config.REVIEW_CSV.exists():
        with open(config.REVIEW_CSV, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if (r.get('decision') or '').strip().lower() == 'approved':
                    out[r['claim_id']] = {k: (r.get(k) or '').strip() for k in ('statement', 'span', 'gravity_class', 'gravity_label', 'reviewer', 'reviewed_on', 'note')}
    return out


def load_relabels():
    """Reviewer relabels of claims outside the review queue: data/review/gravity_relabel.csv (claim_id, gravity_class, gravity_label, reviewer, reviewed_on, note)."""
    out = {}
    path = config.REVIEW_CSV.parent / 'gravity_relabel.csv'
    if path.exists():
        with open(path, encoding='utf-8') as f:
            out = {r['claim_id']: r for r in csv.DictReader(f)}
    return out


def apply_relabel(c, r):
    """Change only the gravity class and label shown for a claim; its status, statement and span stay as they were."""
    if r['gravity_class'] and r['gravity_class'] != c['conditions']['gravity_class']:
        c['original_gravity_class'] = c['conditions']['gravity_class']
        c['conditions']['gravity_class'] = r['gravity_class']
    c['gravity_label'] = r['gravity_label']
    c['gravity_relabel'] = {'reviewer': r['reviewer'], 'reviewed_on': r['reviewed_on'], 'note': r['note']}


def apply_review(c, edit, pages):
    """Record the reviewer's acceptance on the claim and apply a corrected statement / gravity class / gravity label.
    A span is only ever EXTENDED (the new span must start with the old one and be found exactly on the page); it is never replaced by other text.
    The code checks (span, numbers, conditions) are re-run on a corrected statement or extended span and stored."""
    c['review'] = {'reviewer': edit['reviewer'], 'reviewed_on': edit['reviewed_on'], 'note': edit['note'], 'basis': 'reviewed_and_verified_by_reviewer'}
    new_span, span_changed = (edit.get('span') or '').strip(), False
    if new_span and norm(new_span) != norm(c['span']) and norm(new_span).startswith(norm(c['span'])) and check_span(new_span, c['page'], pages)['result'] == 'exact':
        c['original_span'] = c['span']
        c['span'] = new_span
        c['verification']['span'] = check_span(new_span, c['page'], pages)
        span_changed = True
    if (edit['statement'] and edit['statement'] != c['statement']) or span_changed:
        if edit['statement'] and edit['statement'] != c['statement']:
            c['original_statement'] = c['statement']
            c['statement'] = edit['statement']
        c['verification']['review_recheck'] = {
            'span': check_span(c['span'], c['page'], pages)['result'],
            'numbers': check_numbers([c['statement'], c['magnitude_text']], c['span'])['result'],
            'conditions': check_conditions(c['conditions'], c['span'])['result']}
    if edit['gravity_class'] and edit['gravity_class'] != c['conditions']['gravity_class']:
        c['original_gravity_class'] = c['conditions']['gravity_class']
        c['conditions']['gravity_class'] = edit['gravity_class']
    if edit['gravity_label']:
        c['gravity_label'] = edit['gravity_label']
    # an approved claim whose reworded statement fails a code check was approved by manual override of that check
    rc = c['verification'].get('review_recheck', {})
    c['review']['code_check_override'] = any(v not in ('exact', 'pass') for v in rc.values())
    # a correction = reworded statement or corrected gravity class; a gravity label alone (simulated partial gravity) is a relabel, not a correction
    c['review']['corrected'] = 'original_statement' in c or ('original_gravity_class' in c and not edit['gravity_label'])


def verify_claim(client, src, c, doc_pages, vprompt, vversion, use_llm=True):
    pg = c['page']
    c['doc_id'] = src['doc_id']
    sp = check_span(c['span'], pg, doc_pages)
    c['page'] = sp['page']
    page_text = doc_pages.get(c['page'], '')
    c['verification'] = {
        'span': sp,
        'numbers': check_numbers([c['statement'], c['magnitude_text']], c['span']),
        'conditions': check_conditions(c['conditions'], c['span']),
        'gravity': check_gravity(c['conditions']['gravity_class'], c['span'], page_text),
        'support': {'result': 'skipped'},
    }
    if sp['result'] != 'fail' and use_llm == 'skip':
        c['verification']['support'] = {'result': 'pending_verification', 'reason': 'no verifier key available'}
    elif sp['result'] != 'fail' and use_llm:
        c['verification']['support'] = check_support(client, src['sha256'], c, page_text, vprompt, vversion)
    c['verify_prompt_version'] = vversion
    return c


def assign_ids(claims):
    seen = collections.defaultdict(list)
    for c in claims:
        seen[(c['doc_id'], c['page'], norm(c['span']))].append(c)
    out = []
    for key, items in seen.items():
        items.sort(key=lambda c: norm(c['statement']))
        for i, c in enumerate(items):
            c['claim_id'] = claim_id(c['doc_id'], c['page'], c['span'], i)
            out.append(c)
    return out


def run(client, doc_ids=None, eprompt=None, vprompt=None, quiet=False, verify=True):
    """Extract and verify. Returns (claims, stats). Stops cleanly (stats['stopped']) on budget or rate-limit exhaustion."""
    eprompt = eprompt or config.EXTRACT_PROMPT_VERSION
    vprompt = vprompt or config.VERIFY_PROMPT_VERSION
    etext, vtext = prompt(eprompt), prompt(vprompt)
    pages = load_pages()
    srcs = [s for s in read_sources() if doc_ids is None or s['ntrs_id'] in doc_ids or s['doc_id'] in doc_ids]
    if doc_ids:
        order = {d: i for i, d in enumerate(doc_ids)}
        srcs.sort(key=lambda s: order.get(s['ntrs_id'], order.get(s['doc_id'], 99)))
    stats = {'documents': [s['doc_id'] for s in srcs], 'extract_prompt': eprompt, 'verify_prompt': vprompt, 'pending_chunks': [], 'split_chunks': [],
             'failed_chunks': [], 'chunks_done': 0, 'pending_verifications': 0, 'stopped': None, 'chunks_total': 0}
    raw = []
    try:
        for s in srcs:
            dp = pages[s['doc_id']]
            for cid, pg in chunks_for(s, dp):
                stats['chunks_total'] += 1
                for c in extract_chunk(client, s, dp, pg, etext, eprompt, stats):
                    c['doc_id'] = s['doc_id']
                    raw.append((s, c))
            if not quiet:
                print(f"extracted {s['doc_id']}: {sum(1 for x, _ in raw if x is s)} raw claims", flush=True)
    except STOPS as e:
        stats['stopped'] = f'{type(e).__name__}: {e}'
        log_event('stopped', reason=stats['stopped'], phase='extract')
    claims = assign_ids([c for _, c in raw])
    by_doc = {s['doc_id']: s for s in srcs}
    out = []
    stop = stats['stopped'] is not None
    for c in sorted(claims, key=lambda c: (c['doc_id'], c['page'], c['claim_id'])):
        s = by_doc[c['doc_id']]
        try:
            if stop:
                raise CacheMiss('stopped')
            verify_claim(client, s, c, pages[s['doc_id']], vtext, vprompt, use_llm=True if verify else 'skip')
        except CacheMiss:
            verify_claim(client, s, c, pages[s['doc_id']], vtext, vprompt, use_llm=False)
            c['verification']['support'] = {'result': 'pending'}
            stats['pending_verifications'] += 1
        except STOPS as e:
            stop = True
            stats['stopped'] = f'{type(e).__name__}: {e}'
            log_event('stopped', reason=stats['stopped'], phase='verify')
            verify_claim(client, s, c, pages[s['doc_id']], vtext, vprompt, use_llm=False)
            c['verification']['support'] = {'result': 'pending'}
            stats['pending_verifications'] += 1
        out.append(c)
    decisions = load_decisions()
    edits = load_review_edits()
    for c in out:
        if c['verification']['support']['result'] == 'pending':
            c['status'], c['reasons'] = 'needs_review', ['support_check_pending']
            continue
        c['status'], c['reasons'] = decide(c)
        d = decisions.get(c['claim_id'])
        if d == 'approved' and c['status'] in ('needs_review', 'pending_verification'):
            c['status'] = 'approved'
            if c['claim_id'] in edits:
                apply_review(c, edits[c['claim_id']], pages[c['doc_id']])
        elif d == 'rejected':
            c['status'], c['reasons'] = 'rejected', c['reasons'] + ['human_rejected']
    relabels = load_relabels()
    for c in out:
        if c['claim_id'] in relabels:
            apply_relabel(c, relabels[c['claim_id']])
    assign_groups(out, {s['doc_id']: s for s in read_sources()})
    return out, stats


def write_outputs(claims):
    def row(c):
        return json.dumps(c, ensure_ascii=False, sort_keys=True)
    config.LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    keep = [c for c in claims if c['status'] in ('verified_auto', 'approved', 'pending_verification', 'needs_review')]
    rej = [c for c in claims if c['status'] == 'rejected']
    with open(config.CLAIMS_JSONL, 'w', encoding='utf-8', newline='\n') as f:
        for c in keep:
            f.write(row(c) + '\n')
    with open(config.REJECTED_JSONL, 'w', encoding='utf-8', newline='\n') as f:
        for c in rej:
            f.write(row(c) + '\n')


def pilot_failure_rate(claims):
    if not claims:
        return 0.0, 0
    bad = [c for c in claims if set(c['reasons']) & FAIL_REASONS]
    return len(bad) / len(claims), len(bad)
