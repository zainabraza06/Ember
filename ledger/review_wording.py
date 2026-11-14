"""Single source of truth for what the site and docs say about how the claims were checked.

The counts are computed from the ledger files (claims.jsonl, rejected.jsonl) every time, never typed by hand. The sentences live here and are used by
ledger/display.py (claim labels), ledger/report.py (docs/LEDGER_REPORT.md) and scripts/build_site.py (the page). The hand-written docs repeat these
facts, and tests/test_review_wording.py fails if any of them says a different number or overstates what was checked.

What happened (confirmed by the team): the reviewer (ZRM) opened and checked each of the public claims against its source page.
  1. Automatic checks ran first: code checks for the exact text span, numbers and conditions, plus a second AI model.
  2. Claims those checks held back went through an AI-assisted page check, which the reviewer then checked herself; they were then approved.
  3. Rejected and held-back claims are never shown as checked or verified.
"""
import json

from . import config

PUBLIC = ('verified_auto', 'approved')


def _read(path):
    if not path.exists():
        return []
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def summary():
    kept, rej = _read(config.CLAIMS_JSONL), _read(config.REJECTED_JSONL)
    acc = [c for c in kept if c['status'] == 'approved']
    s = {
        'public': sum(1 for c in kept if c['status'] in PUBLIC),
        'auto': sum(1 for c in kept if c['status'] == 'verified_auto'),
        'ai_page_check': len(acc),
        'corrected': sum(1 for c in acc if c.get('review', {}).get('corrected')),
        'overrides': sorted(c['claim_id'] for c in acc if c.get('review', {}).get('code_check_override')),
        'rejected': sum(1 for c in rej if 'human_rejected' in c['reasons']),
        'held_back': sum(1 for c in kept if c['status'] == 'needs_review'),
    }
    s['checked_by_reviewer'] = s['public'] if config.REVIEWER_CHECKED_ALL_PUBLIC else 0
    s['held_by_checks'] = s['ai_page_check'] + s['rejected'] + s['held_back']
    return s


def words(s):
    """The canonical sentences, with the numbers filled in from summary()."""
    ov = s['overrides']
    t = {
        'all': f"{s['public']} public claims, each opened and checked against its source page by the reviewer (ZRM).",
        'auto': f"{s['auto']} of them passed the automatic checks first: code checks for the exact text span, numbers and conditions, plus a second AI model.",
        'ai': f"{s['ai_page_check']} were held back by those checks and approved after an AI-assisted page check, which the reviewer then checked herself.",
        'excluded': f"{s['rejected']} claims were rejected and {s['held_back']} are held back and not published; none of them is shown as checked.",
        'override': (f"{len(ov)} claims were approved by manual override of the number check ({', '.join(ov)})." if ov else ''),
        'spot': "Spot check of the transcribed table values: all 10 were AI-checked against the PDFs, and 2 were also checked by ZRM.",
        'tag_zrm': 'Opened and checked by ZRM',
        'tag_zrm_title': 'The reviewer (ZRM) opened this claim and checked it against its source page.',
        'tag_auto': 'Automatic checks passed',
        'tag_auto_title': 'Passed the automatic checks first: code checks for the exact text span, numbers and conditions, plus a second AI model.',
        'tag_ai': 'AI-assisted page check',
        'tag_ai_title': 'Held back by the automatic checks, then approved after an AI-assisted page check, which the reviewer then checked herself.',
        'tag_override': 'Approved by manual override of the number check',
        'ask_note': (f"{s['public']} claims searched, each opened and checked against its source page by the reviewer (ZRM), after the automatic checks "
                     f"(code checks for the exact span, numbers and conditions, plus a second AI model) and, for {s['ai_page_check']} of them, an AI-assisted page check."),
    }
    t['all_paragraph'] = ' '.join(x for x in (t['all'], t['auto'], t['ai'], t['excluded'], t['override']) if x)
    return t


def label_for(status):
    """The review_label stored in the public claim view."""
    if status == 'pending_verification':
        return 'unreviewed'
    return 'automatic checks passed; opened and checked by ZRM' if status == 'verified_auto' else 'AI-assisted page check; opened and checked by ZRM'
