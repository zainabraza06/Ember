"""Tests for the mission profiles and the static site data (no network)."""
import json
import re
import unittest
from pathlib import Path

from pipeline.profiles import PROFILES, PSI_TO_KPA, build

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


if __name__ == '__main__':
    unittest.main()
