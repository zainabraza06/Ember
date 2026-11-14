"""Tests for the mission profiles and the static site data (no network)."""
import json
import re
import unittest
from pathlib import Path

from pipeline.profiles import PROFILES, PSI_TO_KPA, build
from pipeline import interpret, ranking

ROOT = Path(__file__).resolve().parent.parent


class Profiles(unittest.TestCase):
    def test_kpa_is_computed_from_official_psi(self):
        out = build()
        by = {p['id']: p for p in out['profiles']}
        self.assertAlmostEqual(by['lunar_base']['p_max_kpa'], round(10.2 * PSI_TO_KPA, 2))
        self.assertAlmostEqual(by['spacesuit']['p_min_kpa'], round(4.3 * PSI_TO_KPA, 2))
        self.assertEqual(by['lunar_base']['tests_inside_by_family'], by['pressurized_rover']['tests_inside_by_family'])
        self.assertEqual(sorted(p['id'] for p in PROFILES), sorted(by))

    def test_every_row_inside_meets_the_envelope(self):
        import csv
        with open(ROOT / 'data/processed/tests.csv', encoding='utf-8') as f:
            rows = [r for r in csv.DictReader(f) if r['record_type'] == 'test' and r['oxygen_fraction'] and r['pressure_kpa']]
        inside = [r for r in rows if float(r['oxygen_fraction']) >= 0.30 and float(r['pressure_kpa']) <= 10.2 * PSI_TO_KPA]
        self.assertEqual(len(inside), build()['profiles'][0]['tests_inside_total'])


class Site(unittest.TestCase):
    def data(self):
        s = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
        return json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', s, re.S).group(1).replace('<\/', '</'))

    def test_all_24_investigations_with_sources(self):
        d = self.data()
        self.assertEqual(len(d['investigations']), 24)
        for i in d['investigations']:
            self.assertTrue(i['psi_url'].startswith('https://psi.nasa.gov/'), i['id'])
            for t in i['tags']:
                self.assertIn(t['tag'], ('prevention', 'detection', 'suppression'))
                self.assertTrue(t['reason'])

    def test_partial_gravity_gap_is_labelled(self):
        d = self.data()
        self.assertEqual(sum(1 for r in d['literature'] if r['gravity_level_g'] == '0.165'), 5)
        self.assertEqual(sum(1 for r in d['literature'] if r['gravity_level_g'] == '0.38'), 3)
        self.assertEqual(d['gravity_counts']['0.165']['psi'], 0)
        self.assertEqual(len(d['pairs']), 9)


class RankingAndInterpretation(unittest.TestCase):
    def test_weights_sum_to_one_and_ranking_is_deterministic(self):
        self.assertAlmostEqual(sum(ranking.WEIGHTS.values()), 1.0)
        a, b = ranking.build(), ranking.build()
        self.assertEqual(a, b)
        for p in a['profiles'].values():
            self.assertEqual([i['rank'] for i in p['items']], list(range(1, 25)))
            for it in p['items']:
                self.assertAlmostEqual(it['score'], sum(it['points'].values()), delta=0.2)
                self.assertTrue(0 <= it['score'] <= 100)

    def test_lunar_and_rover_share_the_official_envelope(self):
        r = ranking.build()['profiles']
        self.assertEqual(r['lunar_base']['envelope'], r['pressurized_rover']['envelope'])
        self.assertAlmostEqual(r['spacesuit']['envelope']['p_max_kpa'], round(4.3 * PSI_TO_KPA, 2))

    def test_evidence_strength_rule(self):
        self.assertEqual(interpret.strength(280), 'moderate')
        self.assertEqual(interpret.strength(50), 'limited')
        self.assertEqual(interpret.strength(9), 'very limited')
        self.assertEqual(interpret.strength(9, conflict=True), 'very limited')
        self.assertEqual(interpret.strength(280, conflict=True), 'limited')
        self.assertEqual(interpret.strength(150, families=2), 'strong')

    def test_interpretation_counts_match_the_table(self):
        items = {i['id']: i for i in interpret.build()}
        flex = items['flex_o2_diluent']
        self.assertEqual(flex['n'], 280)
        self.assertEqual(sum(r['n'] for r in flex['tables'][0]['rows']), 280)


class NoSecretsOrNetwork(unittest.TestCase):
    def test_site_has_no_keys_and_makes_no_network_calls(self):
        html = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
        import re
        self.assertIsNone(re.search(r'AQ\.[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{20,}', html))
        for bad in ('GEMINI_API_KEY', 'GROQ_API_KEY', 'fetch(', 'XMLHttpRequest', 'api.groq.com', 'googleapis.com'):
            self.assertNotIn(bad, html, bad)

    def test_unreviewed_claims_are_labelled(self):
        from ledger import verify
        base = {'extraction_confidence': 'high', 'flags': [], 'verification': {'span': {'result': 'exact'}, 'numbers': {'result': 'pass'}, 'conditions': {'result': 'pass'},
                                                                           'gravity': {'result': 'pass'}, 'support': {'result': 'pending_verification'}}}
        self.assertEqual(verify.decide(base)[0], 'pending_verification')
        base['verification']['numbers'] = {'result': 'fail'}
        self.assertEqual(verify.decide(base)[0], 'needs_review')
        base['verification']['numbers'] = {'result': 'pass'}
        base['verification']['span'] = {'result': 'fuzzy'}
        self.assertEqual(verify.decide(base)[0], 'needs_review')


if __name__ == '__main__':
    unittest.main()
