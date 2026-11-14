"""python -m ledger [pages|pilot|extract|report|all] [--offline]

Default (`all`): text layer -> pilot on FLEX and BASS-II (skipped when it already passed for this prompt version) -> full extraction ->
verification -> grouping -> data/ledger/claims.jsonl, rejected.jsonl, data/review/claim_review.csv, docs/CLAIM_AUDIT.md, docs/LEDGER_REPORT.md.
Interrupted runs (rate limits, token/request limits) resume from the cache without repeating calls. --offline never calls the API."""
import argparse
import sys

from . import build, config, report, review
from .llm import Client
from .pages import PAGES_JSONL, build_pages

PILOT_DOCS = ['20150023456', '20210011385']


def finish(claims, stats):
    build.write_outputs(claims)
    n = review.write_review_csv(claims)
    a = review.write_audit(claims)
    report.write_report(stats)
    from collections import Counter
    c = Counter(x['status'] for x in claims)
    print(f"claims: {dict(c)}; review rows {n}; audit rows {a}")
    if stats.get('stopped') or stats.get('pending_chunks') or stats.get('pending_verifications'):
        print(f"INCOMPLETE: {stats.get('stopped')}; pending chunks {len(stats['pending_chunks'])}, pending verifications {stats['pending_verifications']}. Rerun to resume.")
        return 2
    return 0


def run_pilot(client):
    claims, stats = build.run(client, PILOT_DOCS)
    rate, bad = build.pilot_failure_rate(claims)
    versions = sorted({c['model_version'] for c in claims if c.get('model_version')})
    complete = not (stats['stopped'] or stats['pending_chunks'] or stats['pending_verifications'])
    entry = {'prompt_version': config.EXTRACT_PROMPT_VERSION, 'verify_prompt': config.VERIFY_PROMPT_VERSION, 'claims': len(claims), 'failed': bad,
             'fail_rate': rate, 'passed': complete and len(claims) > 0 and rate <= 0.30, 'model_versions': versions, 'complete': complete}
    if complete:
        report.save_pilot(entry)
    print(f"pilot {config.EXTRACT_PROMPT_VERSION}: {len(claims)} claims, {bad} failing a check ({rate:.1%}); {'PASSED' if entry['passed'] else 'NOT passed'}")
    return claims, stats, entry


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m ledger')
    ap.add_argument('command', nargs='?', default='all', choices=['smoke', 'pages', 'pilot', 'extract', 'rate', 'report', 'all'])
    ap.add_argument('--offline', action='store_true', help='use the cache only; never call the API')
    ap.add_argument('--skip-pilot', action='store_true')
    ap.add_argument('--docs', default='', help='comma-separated NTRS ids in priority order (default: all in sources.csv)')
    ap.add_argument('--no-verify', action='store_true', help='skip the LLM support check (automatic when GROQ_API_KEY is not set)')
    ap.add_argument('--stop-at', default='', help='HH:MM local time; stop cleanly at that time')
    a = ap.parse_args(argv)
    if a.stop_at:
        import os
        os.environ['LEDGER_STOP_AT'] = a.stop_at
    if a.command == 'smoke':
        from .smoke import smoke
        return smoke()
    client = Client(offline=a.offline)
    if a.command == 'rate':
        from . import second_rater
        rows, pending, stopped = second_rater.rate_all(client)
        n, agree, kappa = second_rater.write_outputs(rows, pending, stopped)
        print(f'second rater: {n} compared, {agree} agree, kappa {kappa:.3f}; pending {pending} {stopped or ""}')
        return 2 if pending else 0
    if a.command == 'pages' or not PAGES_JSONL.exists():
        build_pages()
        if a.command == 'pages':
            return 0
    if a.command == 'report':
        report.write_report()
        return 0
    if a.command == 'pilot':
        claims, stats, entry = run_pilot(client)
        report.write_report(stats)
        return 0 if entry['passed'] else 1
    if a.command in ('all', 'extract') and not a.skip_pilot and not report.pilot_passed(config.EXTRACT_PROMPT_VERSION):
        claims, stats, entry = run_pilot(client)
        report.write_report(stats)
        if not entry['passed']:
            print('Pilot did not pass: write a new prompt version (prompts/extract_vN.md, note it in prompts/CHANGELOG.md) and set LEDGER_EXTRACT_PROMPT.')
            return 1
    import os
    verify = not a.no_verify and bool(os.environ.get('GROQ_API_KEY'))
    docs = [d for d in a.docs.split(',') if d] or None
    claims, stats = build.run(client, docs, verify=verify)
    return finish(claims, stats)


if __name__ == '__main__':
    sys.exit(main())
