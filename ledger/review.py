"""Human review files: data/review/claim_review.csv (claims needing review) and docs/CLAIM_AUDIT.md (30 random verified claims)."""
import csv
import random
import re

from . import config

REVIEW_FIELDS = ['claim_id', 'doc_id', 'page', 'reasons', 'gravity_class', 'statement', 'span', 'decision', 'reviewer', 'reviewed_on', 'note', 'original_statement', 'gravity_label']
AUDIT_SEED = 20261019


def write_review_csv(claims):
    """Rows for every needs_review claim (and every claim a human already decided), keeping earlier decisions."""
    old = {}
    if config.REVIEW_CSV.exists():
        with open(config.REVIEW_CSV, encoding='utf-8') as f:
            old = {r['claim_id']: r for r in csv.DictReader(f)}
    rows = []
    for c in sorted(claims, key=lambda c: (c['doc_id'], c['page'], c['claim_id'])):
        prev = old.get(c['claim_id'], {})
        if c['status'] == 'needs_review' or prev.get('decision'):
            rows.append({'claim_id': c['claim_id'], 'doc_id': c['doc_id'], 'page': c['page'], 'reasons': ';'.join(c['reasons']),
                         'gravity_class': c['conditions']['gravity_class'], 'statement': c['statement'], 'span': c['span'],
                         'decision': prev.get('decision', ''), 'reviewer': prev.get('reviewer', ''), 'reviewed_on': prev.get('reviewed_on', ''),
                         'note': prev.get('note', ''), 'original_statement': c.get('original_statement', prev.get('original_statement', '')),
                         'gravity_label': c.get('gravity_label', prev.get('gravity_label', ''))})
    config.REVIEW_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(config.REVIEW_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def _esc(s):
    return (s or '').replace('|', '\\|').replace('\n', ' ')


def parse_audit():
    """Existing audit table -> {claim_id: (correct, reviewer, note)}. Empty dict if the file does not exist."""
    out = {}
    if config.AUDIT_MD.exists():
        for line in config.AUDIT_MD.read_text(encoding='utf-8').splitlines():
            m = re.match(r'\|\s*\d+\s*\|\s*(C-[0-9a-f]+(?:-[b-j])?)\s*\|', line)
            if m:
                cells = [x.strip() for x in line.strip().strip('|').split('|')]
                out[m.group(1)] = tuple(cells[-3:])
    return out


def write_audit(claims, n=30):
    """Seeded sample of verified_auto claims. If the file already exists its claim list (and any entries) are kept."""
    by_id = {c['claim_id']: c for c in claims}
    existing = parse_audit()
    if existing:
        ids = [i for i in existing if i in by_id] or list(existing)
    else:
        pool = sorted(c['claim_id'] for c in claims if c['status'] == 'verified_auto')
        ids = random.Random(AUDIT_SEED).sample(pool, min(n, len(pool)))
    L = ['# Claim audit (M3 acceptance: at least 90% of 30 random verified claims judged correct)', '',
         f'{len(ids)} claims drawn with a seeded random sample (seed {AUDIT_SEED}) from the claims with status `verified_auto`. For each row read the span in the source '
         '(PDF page number is the PDF page index) and answer in `correct?`: **yes** if the statement is supported by the span and its conditions (gravity class, material, numbers) are right, '
         '**no** if not, with a short note. Fill in `reviewer` too. Statistics are computed by `python -m ledger report` from the filled rows.', '',
         '| # | claim_id | document | page | gravity | statement | span | correct? | reviewer | note |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, cid in enumerate(ids, 1):
        c = by_id.get(cid)
        prev = existing.get(cid, ('', '', ''))
        if c is None:
            L.append(f'| {i} | {cid} | (claim no longer in the ledger) | | | | | {prev[0]} | {prev[1]} | {prev[2]} |')
            continue
        L.append(f"| {i} | {cid} | {c['doc_id']} | {c['page']} | {c['conditions']['gravity_class']} | {_esc(c['statement'])} | {_esc(c['span'])} | {prev[0]} | {prev[1]} | {prev[2]} |")
    config.AUDIT_MD.write_text('\n'.join(L) + '\n', encoding='utf-8')
    return len(ids)


def audit_stats():
    done = [v for v in parse_audit().values() if v[0].strip().lower() in ('yes', 'no')]
    yes = sum(1 for v in done if v[0].strip().lower() == 'yes')
    return len(done), yes
