"""Unit tests for scripts/ask_parser.js (the Ask page's deterministic query parser), run through Node. Skipped when Node is not installed."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which('node')
VOCAB = ['pmma', 'methanol', 'heptane', 'rod', 'sibal', 'silicone', 'nomex', 'film']

ROWS = [  # compact test rows as embedded in the site: i investigation, m material, o O2 fraction, p kPa, g gravity, c outcome, t record type
    {'i': 'PSI-39', 'm': 'Methanol', 'o': 0.30, 'p': 70.3, 'g': '0', 'c': 'self_extinguished', 't': 'test'},
    {'i': 'PSI-39', 'm': 'Methanol', 'o': 0.21, 'p': 101.3, 'g': '0', 'c': 'externally_terminated', 't': 'test'},
    {'i': 'PSI-25', 'm': 'PMMA', 'o': 0.50, 'p': 50.0, 'g': '0', 'c': 'no_ignition', 't': 'test'},
    {'i': 'PSI-25', 'm': 'PMMA', 'o': 0.21, 'p': None, 'g': '0', 'c': 'burned_to_completion', 't': 'test'},
    {'i': 'x', 'm': 'PMMA', 'o': 0.21, 'p': 101.3, 'g': '1', 'c': 'burned_to_completion', 't': 'test'},
    {'i': 'x', 'm': 'PMMA', 'o': 0.19, 'p': 101.4, 'g': '1', 'c': 'unknown', 't': 'limit'},
]


def run(js):
    r = subprocess.run([NODE, '-e', js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


def parse(q):
    return run("const A=require('./scripts/ask_parser.js');const r=A.parseQuery(%s,new Set(%s));console.log(JSON.stringify(r))" % (json.dumps(q), json.dumps(VOCAB)))


@unittest.skipUnless(NODE, 'node not installed')
class AskParser(unittest.TestCase):
    def approx(self, a, b, tol=1e-6):
        self.assertAlmostEqual(a, b, delta=tol)

    def test_oxygen_percent_equals_has_tolerance(self):
        r = parse('which materials burn at 30% oxygen')
        self.assertTrue(r['numeric'])
        self.approx(r['o']['min'], 0.295)
        self.approx(r['o']['max'], 0.305)
        self.assertIsNone(r['p'])

    def test_pressure_units_convert_to_kpa(self):
        for q, kpa in (('at 10.2 psi', 70.33), ('at 10.2 psia', 70.33), ('at 70 kPa', 70.0), ('at 1 atm', 101.325), ('at 760 mmHg', 101.325), ('at 760 torr', 101.325)):
            r = parse(q)
            self.approx(r['p']['eq'], kpa, 0.05)
            self.approx(r['p']['max'] - r['p']['min'], 2 * 0.03 * r['p']['eq'], 1e-6)

    def test_at_least_and_above(self):
        r = parse('at least 30% oxygen')
        self.approx(r['o']['min'], 0.30)
        self.assertNotIn('max', r['o'])
        self.assertFalse(r['o'].get('minEx'))
        r = parse('oxygen above 30%')
        self.approx(r['o']['min'], 0.30)
        self.assertTrue(r['o']['minEx'])
        r = parse('O2 >= 30')
        self.approx(r['o']['min'], 0.30)
        self.assertFalse(r['o'].get('minEx'))
        r = parse('30% oxygen or more')
        self.approx(r['o']['min'], 0.30)
        self.assertNotIn('max', r['o'])
        r = parse('pressure above 10.2 psi')
        self.approx(r['p']['min'], 70.33, 0.05)
        self.assertTrue(r['p']['minEx'])

    def test_below_and_at_most(self):
        r = parse('below 21% oxygen')
        self.approx(r['o']['max'], 0.21)
        self.assertTrue(r['o']['maxEx'])
        self.assertNotIn('min', r['o'])
        r = parse('at most 21% O2')
        self.approx(r['o']['max'], 0.21)
        self.assertFalse(r['o'].get('maxEx'))
        r = parse('under 0.5 atm')
        self.approx(r['p']['max'], 50.66, 0.05)
        self.assertTrue(r['p']['maxEx'])
        r = parse('pressure up to 70 kPa')
        self.approx(r['p']['max'], 70.0)
        self.assertFalse(r['p'].get('maxEx'))

    def test_ranges(self):
        r = parse('between 25 and 35% oxygen')
        self.approx(r['o']['min'], 0.25)
        self.approx(r['o']['max'], 0.35)
        r = parse('pressure 10 to 14.7 psia')
        self.approx(r['p']['min'], 68.95, 0.05)
        self.approx(r['p']['max'], 101.35, 0.05)
        r = parse('oxygen 25-35%')
        self.approx(r['o']['min'], 0.25)
        self.approx(r['o']['max'], 0.35)

    def test_oxygen_without_unit(self):
        self.approx(parse('O2 at 30 in microgravity')['o']['min'], 0.295)
        self.approx(parse('oxygen 0.3')['o']['min'], 0.295)

    def test_gravity_material_and_outcome_words(self):
        r = parse('what happens to PMMA at 21% oxygen in microgravity')
        self.assertEqual(r['g'], '0')
        self.assertEqual(r['materials'], ['pmma'])
        self.assertEqual(parse('lunar gravity flammability')['g'], '0.165')
        self.assertEqual(parse('Mars gravity flammability')['g'], '0.38')
        self.assertEqual(parse('PMMA in 1 g')['g'], '1')
        self.assertEqual(parse('which rods did not ignite at 30% oxygen')['outcomes'], ['no_ignition'])
        self.assertEqual(parse('self-extinguish at 21% oxygen')['outcomes'], ['self_extinguished'])
        r = parse('which fuels ignite above 25% oxygen')
        self.assertNotIn('no_ignition', r['outcomes'])
        self.assertIn('externally_terminated', r['outcomes'])
        r = parse('which materials burn at 30% oxygen')
        self.assertEqual(r['outcomes'], [])          # "burn" is not an outcome filter
        self.assertTrue(r['plainBurn'])

    def test_no_numeric_condition(self):
        self.assertFalse(parse('Mars gravity flammability')['numeric'])
        r = parse('who won the cricket match')
        self.assertFalse(r['numeric'])
        self.assertEqual(r['chips'], [])

    def test_filters_counts_and_censoring(self):
        js = ("const A=require('./scripts/ask_parser.js');const rows=%s;const v=A.vocabFrom(rows);"
              "const f=A.parseQuery('PMMA at 21%% oxygen',v);const a=A.applyFilters(rows,f);"
              "const g=A.parseQuery('21%% oxygen at 101 kPa in microgravity',v);const b=A.applyFilters(rows,g);"
              "const n=A.nearest(rows,A.parseQuery('Methanol at 40%% oxygen at 70 kPa',v),2);"
              "console.log(JSON.stringify({hit:a.hit.length,split:A.split(a.hit),b:b.hit.length,nearest:n.map(x=>x.r.o)}))") % json.dumps(ROWS)
        o = run(js)
        self.assertEqual(o['hit'], 2)                       # the two PMMA 21% tests; the limit row is not a test
        self.assertEqual(o['split']['burned_to_completion'], 2)
        self.assertEqual(o['b'], 1)                         # 21% at 101 kPa in microgravity: only the methanol test
        self.assertEqual(o['nearest'][0], 0.30)             # nearest tested O2 to 40% at 70 kPa
        s = run("const A=require('./scripts/ask_parser.js');console.log(JSON.stringify(A.split(%s)))" % json.dumps(ROWS[:2]))
        self.assertEqual(s['externally_terminated'], 1)     # censored outcomes stay their own class, never "no ignition"
        self.assertEqual(s['no_ignition'], 0)

    def test_rows_without_pressure_do_not_match_a_pressure_filter(self):
        js = ("const A=require('./scripts/ask_parser.js');const rows=%s;const f=A.parseQuery('PMMA at 21%% oxygen at 1 atm',A.vocabFrom(rows));"
              "const a=A.applyFilters(rows,f);console.log(JSON.stringify({hit:a.hit.length,noP:a.noP}))") % json.dumps(ROWS)
        o = run(js)
        self.assertEqual(o['hit'], 1)
        self.assertEqual(o['noP'], 1)


if __name__ == '__main__':
    unittest.main()
