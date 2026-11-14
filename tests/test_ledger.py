"""Unit tests for the evidence ledger (M3). No network: the provider transport is mocked."""
import csv
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.error
from pathlib import Path

from ledger import build, config, display, llm, schema, verify
from ledger.group import assign_groups

PAGE = ("Figure 3. In microgravity the flame spread rate over thin PMMA sheets decreased from 2.4 mm/s to 1.1 mm/s as the oxygen "
        "concentration was reduced from 21% to 17%. The flow velocity was 5 cm/s.")


class Spans(unittest.TestCase):
    def test_exact_after_normalisation(self):
        pages = {7: 'Intro text. In micro-\ngravity the flame went out\nat 17% O2. More text.'}
        r = verify.check_span('In microgravity the flame went out at 17% O2.', 7, pages)
        self.assertEqual((r['result'], r['page_corrected']), ('exact', False))

    def test_wrong_page_is_corrected_from_text(self):
        pages = {7: 'nothing here at all', 8: 'The flame went out at 17% O2 in the test.'}
        r = verify.check_span('The flame went out at 17% O2 in the test.', 7, pages)
        self.assertEqual((r['result'], r['page'], r['page_corrected']), ('exact', 8, True))

    def test_fuzzy_and_fail(self):
        text = 'The flame went out at 17 percent oxygen in the second test of the series run on orbit.'
        pages = {1: text}
        near = 'The flame went out at 17 percent oxygen in the second test of the series run on orbt.'
        self.assertEqual(verify.check_span(near, 1, pages)['result'], 'fuzzy')
        self.assertEqual(verify.check_span('The flame never went out in any of the tests that were done.', 1, pages)['result'], 'fail')

    def test_invented_span_is_not_found(self):
        self.assertEqual(verify.check_span('Completely invented sentence about lunar fires.', 1, {1: PAGE})['result'], 'fail')


class Numbers(unittest.TestCase):
    span = 'The flame spread rate decreased from 2.4 mm/s to 1.1 mm/s as oxygen fell from 21% to 17%.'

    def test_numbers_present(self):
        self.assertEqual(verify.check_numbers(['Spread rate fell from 2.4 to 1.1 mm/s as oxygen fell from 21 to 17 percent'], self.span)['result'], 'pass')

    def test_number_not_in_span(self):
        r = verify.check_numbers(['Spread rate fell by 1.3 mm/s'], self.span)
        self.assertEqual((r['result'], r['missing']), ('fail', [1.3]))

    def test_fraction_of_a_percent_allowed(self):
        self.assertEqual(verify.check_numbers(['oxygen 0.21'], self.span)['result'], 'pass')

    def test_conditions_need_a_printed_source(self):
        self.assertEqual(verify.check_conditions({'oxygen_fraction_min': 0.17, 'oxygen_fraction_max': 0.21}, self.span)['result'], 'pass')
        self.assertEqual(verify.check_conditions({'pressure_kpa_min': 55.0}, self.span)['result'], 'fail')
        self.assertEqual(verify.check_conditions({'pressure_kpa_min': 101.325}, 'at 1 atm in air')['result'], 'pass')

    def test_gravity_word_check(self):
        self.assertEqual(verify.check_gravity('lunar', 'On the Moon the flame spread faster.', '')['result'], 'pass')
        self.assertEqual(verify.check_gravity('lunar', 'The flame spread faster.', 'Lunar gravity tests were run')['result'], 'context')
        self.assertEqual(verify.check_gravity('mars', 'The flame spread faster.', 'microgravity only')['result'], 'fail')


class Ids(unittest.TestCase):
    def test_stable_and_independent_of_wording(self):
        a = schema.claim_id('NTRS-1', 5, 'The flame  went out at 17% O2.')
        b = schema.claim_id('NTRS-1', 5, 'The flame went\nout at 17% O2.')
        self.assertEqual(a, b)
        self.assertNotEqual(a, schema.claim_id('NTRS-1', 6, 'The flame went out at 17% O2.'))
        self.assertNotEqual(a, schema.claim_id('NTRS-2', 5, 'The flame went out at 17% O2.'))
        self.assertTrue(schema.claim_id('NTRS-1', 5, 'x y', 1).endswith('-b'))

    def test_assign_ids_two_claims_one_span(self):
        base = {'doc_id': 'D', 'page': 1, 'span': 'Same sentence here.'}
        cs = build.assign_ids([dict(base, statement='B finding'), dict(base, statement='A finding')])
        ids = {c['statement']: c['claim_id'] for c in cs}
        self.assertTrue(ids['A finding'] + '-b' == ids['B finding'])


def good_claim(**kw):
    c = {'page': 1, 'locator': 'Figure 3', 'span': PAGE.split('. ')[1] + '.', 'statement': 'In microgravity the spread rate over thin PMMA fell from 2.4 to 1.1 mm/s when oxygen was reduced from 21 to 17 percent.',
         'variables': ['flame_spread_rate', 'oxygen_concentration'], 'effect_direction': 'decreases', 'magnitude_text': '', 'evidence_type': 'measurement',
         'extraction_confidence': 'high',
         'conditions': {'gravity_class': 'microgravity', 'gravity_g': None, 'oxygen_fraction_min': 0.17, 'oxygen_fraction_max': 0.21, 'pressure_kpa_min': None,
                        'pressure_kpa_max': None, 'flow_cm_s_min': None, 'flow_cm_s_max': None, 'material': 'PMMA', 'geometry': None}}
    c.update(kw)
    return c


class MockApi:
    """Transport(provider, url, headers, payload) -> (json, headers); canned extraction (gemini) / verification (groq) answers."""
    def __init__(self, claims=None, verdict='supported', fail_first=0, daily_after=None):
        self.claims, self.verdict, self.calls, self.fail_first, self.daily_after = claims or [], verdict, 0, fail_first, daily_after
        self.providers = []

    def __call__(self, provider, url, headers, payload):
        self.calls += 1
        self.providers.append(provider)
        if self.daily_after is not None and self.calls > self.daily_after:
            raise urllib.error.HTTPError(url, 429, 'Too Many Requests', {'Retry-After': '40000'}, io.BytesIO(b'{"error": "quota exceeded: requests per day"}'))
        if self.fail_first > 0:
            self.fail_first -= 1
            raise urllib.error.HTTPError(url, 429, 'Too Many Requests', {'Retry-After': '0'}, io.BytesIO(b'slow down'))
        if provider == 'gemini':
            content = json.dumps({'claims': self.claims})
            return {'candidates': [{'content': {'parts': [{'text': content}]}, 'finishReason': 'STOP'}], 'modelVersion': 'gemini-test-001',
                    'usageMetadata': {'promptTokenCount': 100, 'totalTokenCount': 150}}, {}
        content = json.dumps({'verdict': self.verdict, 'reason': 'ok'})
        return {'id': 'r1', 'model': 'llama-3.3-70b-versatile', 'choices': [{'message': {'content': content}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150}}, {'x-ratelimit-remaining-requests': '99'}


class Sandbox(unittest.TestCase):
    """Redirects every ledger path into a temp directory."""
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = {k: getattr(config, k) for k in ('LEDGER_DIR', 'CACHE_DIR', 'SOURCES_CSV', 'PAGES_JSONL', 'CLAIMS_JSONL', 'REJECTED_JSONL', 'REVIEW_CSV', 'MAX_TOKENS')}
        self.saved_prov = {k: dict(v) for k, v in config.PROVIDERS.items()}
        self.saved_usage, self.saved_run = llm.USAGE_LOG, llm.RUN_LOG
        config.LEDGER_DIR = self.tmp
        config.CACHE_DIR = self.tmp / 'cache'
        config.SOURCES_CSV = self.tmp / 'sources.csv'
        config.PAGES_JSONL = self.tmp / 'pages.jsonl'
        config.CLAIMS_JSONL = self.tmp / 'claims.jsonl'
        config.REJECTED_JSONL = self.tmp / 'rejected.jsonl'
        config.REVIEW_CSV = self.tmp / 'claim_review.csv'
        for p in config.PROVIDERS.values():
            p.update(rpm=0, rpd=0, tpm=0, tpd=0)
        config.PROVIDERS['gemini']['model'] = 'gemini-test'
        os.environ['GEMINI_API_KEY'] = os.environ['GROQ_API_KEY'] = 'test-not-a-real-key'
        llm.USAGE_LOG, llm.RUN_LOG = self.tmp / 'usage.jsonl', self.tmp / 'run_log.jsonl'
        import ledger.pages as pg
        self.pg, self.saved_pg = pg, pg.PAGES_JSONL
        pg.PAGES_JSONL = config.PAGES_JSONL
        pg.SOURCES_CSV = config.SOURCES_CSV
        fields = ['doc_id', 'ntrs_id', 'title', 'year', 'display_verbatim', 'study_family', 'url', 'sha256', 'scope_pages']
        with open(config.SOURCES_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerow({'doc_id': 'NTRS-1', 'ntrs_id': '1', 'title': 'Gov report', 'year': '2003', 'display_verbatim': 'yes', 'study_family': 'NTRS-1', 'url': 'u', 'sha256': 'abc', 'scope_pages': ''})
            w.writerow({'doc_id': 'NTRS-2', 'ntrs_id': '2', 'title': 'Contractor report', 'year': '2005', 'display_verbatim': 'no', 'study_family': 'NTRS-2', 'url': 'u', 'sha256': 'def', 'scope_pages': ''})
        with open(config.PAGES_JSONL, 'w', encoding='utf-8') as f:
            for d in ('NTRS-1', 'NTRS-2'):
                f.write(json.dumps({'doc_id': d, 'page': 1, 'text': PAGE}) + '\n')
        for name in ('extract_v1', 'verify_v1'):
            self.assertTrue((config.PROMPTS_DIR / f'{name}.md').exists())

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(config, k, v)
        for k, v in self.saved_prov.items():
            config.PROVIDERS[k].clear()
            config.PROVIDERS[k].update(v)
        llm.USAGE_LOG, llm.RUN_LOG = self.saved_usage, self.saved_run
        self.pg.PAGES_JSONL = self.saved_pg
        self.pg.SOURCES_CSV = self.saved['SOURCES_CSV']
        shutil.rmtree(self.tmp, ignore_errors=True)


class EndToEnd(Sandbox):
    def test_pipeline_statuses(self):
        bad_span = good_claim(span='This sentence is not in the document at all.', statement='Something with no number.')
        bad_num = good_claim(statement='Spread rate fell by 9.9 mm/s.')
        api = MockApi([good_claim(), bad_span, bad_num])
        cl = llm.Client(transport=api, sleep=lambda s: None)
        claims, stats = build.run(cl, ['1'], quiet=True)
        st = {c['statement'][:20]: c['status'] for c in claims}
        self.assertEqual(sorted(c['status'] for c in claims), ['needs_review', 'rejected', 'verified_auto'])
        self.assertEqual(stats['stopped'], None)
        bad = [c for c in claims if c['status'] == 'needs_review'][0]
        self.assertIn('number_not_in_span', bad['reasons'])
        self.assertEqual(claims[0]['model_version'], 'gemini-test-001')
        self.assertEqual(sorted(set(api.providers)), ['gemini', 'groq'])   # extraction and verification use different families

    def test_unsupported_verdict_is_rejected_and_partial_needs_review(self):
        for verdict, status in (('unsupported', 'rejected'), ('partial', 'needs_review'), ('supported', 'verified_auto')):
            shutil.rmtree(config.CACHE_DIR, ignore_errors=True)
            llm.USAGE_LOG.unlink(missing_ok=True)
            claims, _ = build.run(llm.Client(transport=MockApi([good_claim()], verdict), sleep=lambda s: None), ['1'], quiet=True)
            self.assertEqual(claims[0]['status'], status, verdict)

    def test_api_keys_are_never_written(self):
        build.run(llm.Client(transport=MockApi([good_claim()]), sleep=lambda s: None), ['1'], quiet=True)
        for f in self.tmp.rglob('*'):
            if f.is_file():
                self.assertNotIn('test-not-a-real-key', f.read_text(encoding='utf-8'), f.name)

    def test_cache_reuse_makes_no_second_call(self):
        api = MockApi([good_claim()])
        build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        first = api.calls
        self.assertEqual(first, 2)                                  # one extraction, one verification
        claims, _ = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        self.assertEqual(api.calls, first)
        self.assertEqual(len(claims), 1)
        offline, stats = build.run(llm.Client(offline=True), ['1'], quiet=True)   # no transport needed at all
        self.assertEqual(offline[0]['claim_id'], claims[0]['claim_id'])

    def test_changed_prompt_version_does_not_reuse_cache(self):
        a = llm.cache_key('extract', 'abc', 'c1', 'extract_v1', 'm', 'gemini')
        self.assertNotEqual(a, llm.cache_key('extract', 'abc', 'c1', 'extract_v2', 'm', 'gemini'))
        self.assertNotEqual(a, llm.cache_key('extract', 'abd', 'c1', 'extract_v1', 'm', 'gemini'))
        self.assertNotEqual(a, llm.cache_key('verify', 'abc', 'c1', 'extract_v1', 'm', 'gemini'))
        self.assertNotEqual(a, llm.cache_key('extract', 'abc', 'c1', 'extract_v1', 'm', 'groq'))

    def test_rate_limit_backoff_then_success(self):
        api = MockApi([good_claim()], fail_first=2)
        cl = llm.Client(transport=api, sleep=lambda s: None)
        claims, _ = build.run(cl, ['1'], quiet=True)
        self.assertEqual(len(claims), 1)
        events = [json.loads(x) for x in open(llm.RUN_LOG, encoding='utf-8')]
        self.assertEqual(sum(1 for e in events if e['event'] == 'retry'), 2)

    def test_daily_request_limit_stops_cleanly_and_resumes(self):
        config.PROVIDERS['groq']['rpd'] = 0
        api = MockApi([good_claim()], daily_after=1)       # the provider says "requests per day" from the second call on
        claims, stats = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        self.assertIn('DailyLimit', stats['stopped'])
        self.assertEqual(claims[0]['status'], 'needs_review')       # pending verification is never published
        self.assertEqual(claims[0]['reasons'], ['support_check_pending'])
        api.daily_after = None                                       # next day
        (config.LEDGER_DIR / 'exhausted.json').unlink(missing_ok=True)   # the exhausted-models record is per calendar day
        claims, stats = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        self.assertEqual((claims[0]['status'], stats['stopped']), ('verified_auto', None))
        self.assertEqual(api.calls, 4)                               # 1 extraction + 2 refused (same quota message twice) + 1 verification; extraction not repeated

    def test_own_daily_counter_stops_before_calling(self):
        config.PROVIDERS['groq']['rpd'] = 1
        api = MockApi([good_claim(), good_claim(span='The flow velocity was 5 cm/s.', statement='The flow velocity was 5 cm/s.')])
        claims, stats = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        self.assertIn('DailyLimit', stats['stopped'])
        self.assertEqual(api.providers.count('groq'), 1)
        self.assertEqual(stats['pending_verifications'], 1)

    def test_token_limit(self):
        config.MAX_TOKENS = 100
        api = MockApi([good_claim()])
        _, stats = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        self.assertIsNotNone(stats['stopped'])

    def test_rejected_claims_are_written_apart_and_never_public(self):
        api = MockApi([good_claim(), good_claim(span='Not in the text at all, invented.', statement='Invented finding.')])
        claims, _ = build.run(llm.Client(transport=api, sleep=lambda s: None), ['1'], quiet=True)
        build.write_outputs(claims)
        kept = display.load_claims(config.CLAIMS_JSONL)
        rej = display.load_claims(config.REJECTED_JSONL)
        self.assertEqual((len(kept), len(rej)), (1, 1))
        self.assertEqual(rej[0]['status'], 'rejected')
        pub = display.public_claims(kept, display.load_sources())
        self.assertEqual(len(pub), 1)


class Display(Sandbox):
    def claim(self, doc, status):
        c = good_claim()
        c.update(doc_id=doc, status=status, claim_id='C-x', group_id=None)
        return c

    def test_verbatim_only_for_us_government_works(self):
        src = display.load_sources()
        gov = display.public_view(self.claim('NTRS-1', 'verified_auto'), src['NTRS-1'])
        other = display.public_view(self.claim('NTRS-2', 'verified_auto'), src['NTRS-2'])
        self.assertIn('microgravity', gov['span'])
        self.assertIsNone(other['span'])
        self.assertIn('Contractor report', other['citation'])
        self.assertIn('PDF p.1', other['citation'])

    def test_unverified_never_public(self):
        src = display.load_sources()
        for st in ('needs_review', 'rejected'):
            self.assertIsNone(display.public_view(self.claim('NTRS-1', st), src['NTRS-1']))
        self.assertIsNotNone(display.public_view(self.claim('NTRS-1', 'approved'), src['NTRS-1']))


class SecondRater(unittest.TestCase):
    def test_kappa(self):
        from ledger.second_rater import cohens_kappa
        a = ['unknown', 'unknown', 'self_extinguished', 'self_extinguished']
        self.assertAlmostEqual(cohens_kappa(a, a), 1.0)
        self.assertAlmostEqual(cohens_kappa(a, ['unknown', 'self_extinguished', 'unknown', 'self_extinguished']), 0.0)
        self.assertAlmostEqual(cohens_kappa(['unknown'] * 3 + ['self_extinguished'], ['unknown'] * 2 + ['self_extinguished'] * 2), 0.5)


class Groups(unittest.TestCase):
    def test_independent_sources_counts_families(self):
        def c(i, doc, text):
            return {'claim_id': f'C-{i}', 'doc_id': doc, 'status': 'verified_auto', 'statement': text, 'variables': ['extinction', 'oxygen_concentration'],
                    'effect_direction': 'threshold', 'conditions': {'gravity_class': 'lunar'}}
        cs = [c(1, 'A', 'Flames extinguished below 17 percent oxygen at lunar gravity'), c(2, 'B', 'Flames extinguished below 17 percent oxygen at lunar gravity in tests'),
              c(3, 'C', 'Flames extinguished below 17 percent oxygen at lunar gravity'), c(4, 'A', 'Totally different finding about heptane droplets')]
        assign_groups(cs, {'A': {'study_family': 'F1'}, 'B': {'study_family': 'F1'}, 'C': {'study_family': 'F2'}})
        self.assertEqual({cs[0]['group_id'], cs[1]['group_id'], cs[2]['group_id']}, {cs[0]['group_id']})
        self.assertEqual(cs[0]['independent_sources'], 2)
        self.assertEqual(cs[0]['group_size'], 3)
        self.assertEqual(cs[3]['group_size'], 1)


if __name__ == '__main__':
    unittest.main()
