"""What may reach the UI (rules 1 and 2 of the ledger).

1. Only claims with status verified_auto or approved are public. needs_review and rejected claims never are.
2. Copyright: a verbatim span is shown only for documents flagged display_verbatim = yes in sources.csv (US Government works, NTRS
   determination GOV_PUBLIC_USE_PERMITTED). For every other document the claim is shown as the plain-language statement plus a
   citation (document, page, locator); the span stays in the ledger for verification and audit but is not displayed."""
import csv
import json

from . import config

PUBLIC_STATUSES = ('verified_auto', 'approved', 'pending_verification')   # pending_verification is shown labelled 'unreviewed'


def load_sources():
    with open(config.SOURCES_CSV, encoding='utf-8') as f:
        return {r['doc_id']: r for r in csv.DictReader(f)}


def load_claims(path=None):
    with open(path or config.CLAIMS_JSONL, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def citation(claim, source):
    loc = f", {claim['locator']}" if claim.get('locator') else ''
    return f"{source['title']} ({source['year']}), NTRS {source['ntrs_id']}, PDF p.{claim['page']}{loc}"


def public_view(claim, source):
    """The UI-safe view of one claim, or None if the claim must not be shown."""
    if claim['status'] not in PUBLIC_STATUSES:
        return None
    allowed = source.get('display_verbatim') == 'yes'
    return {'claim_id': claim['claim_id'], 'statement': claim['statement'], 'status': claim['status'], 'variables': claim['variables'],
            'conditions': claim['conditions'], 'effect_direction': claim['effect_direction'], 'evidence_type': claim['evidence_type'],
            'group_id': claim.get('group_id'), 'independent_sources': claim.get('independent_sources', 0),
            'citation': citation(claim, source), 'source_url': source['url'], 'page': claim['page'],
            'review_label': 'unreviewed' if claim['status'] == 'pending_verification' else ('human-approved' if claim['status'] == 'approved' else 'auto-verified'),
            'span': claim['span'] if allowed else None, 'span_hidden_reason': None if allowed else 'source is not a US Government work (copyright)'}


def public_claims(claims, sources):
    return [v for c in claims if (v := public_view(c, sources[c['doc_id']])) is not None]
