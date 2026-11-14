"""Tests for the M2 harmonization pipeline. Run from the repo root:  python -m unittest discover -s tests -t ."""
import collections
import json
import unittest
from unittest import mock

from pipeline import build, checks
from pipeline.common import KPA_PER_BAR, KPA_PER_MMHG, KPA_PER_PSI, parse_float, parse_with_unit
from pipeline.materials import normalize_material
from pipeline.outcome import cfig_outcome, flex_outcome
from pipeline.schema import OUTCOME_CLASSES, validate_row


class Conversions(unittest.TestCase):
    def test_pressure_factors(self):
        self.assertAlmostEqual(760 * KPA_PER_MMHG, 101.325, places=9)
        self.assertAlmostEqual(14.7 * KPA_PER_PSI, 101.353, places=3)
        self.assertAlmostEqual(10.2 * KPA_PER_PSI, 70.327, places=3)
        self.assertEqual(1.0 * KPA_PER_BAR, 100.0)

    def test_parsers(self):
        self.assertEqual(parse_float('.21'), 0.21)
        for t in ('', '?', '-', 'n/a', 'Insignificant', '~ 21.5'):
            self.assertIsNone(parse_float(t))
        self.assertEqual(parse_with_unit('20 cm/s', ('cm/s',)), (20.0, 'cm/s'))
        self.assertEqual(parse_with_unit('420', ('s',)), (420.0, ''))
        self.assertEqual(parse_with_unit('0.27 mm', ('cm', 'mm')), (0.27, 'mm'))
        self.assertEqual(parse_with_unit('Insignificant', ('s',)), (None, None))


class Outcomes(unittest.TestCase):
    def test_flex_outcome_from_test_end_label(self):
        self.assertEqual(flex_outcome('Extinction')[0], 'self_extinguished')
        self.assertEqual(flex_outcome('Completion')[0], 'burned_to_completion')
        self.assertEqual(flex_outcome('Disruption')[0], 'other')
        for t in ('', None, '?', '0.89'):
            self.assertEqual(flex_outcome(t)[0], 'unknown', t)

    def test_flex_label_diameter_disagreement(self):
        from pipeline.outcome import flex_label_diameter_disagree as d
        self.assertTrue(d('Extinction', '0'))
        self.assertFalse(d('Extinction', '1.2'))
        self.assertTrue(d('Completion', '0.9'))
        self.assertFalse(d('Completion', '0'))

    def test_cfig_rules(self):
        self.assertEqual(cfig_outcome('Yes', 'SE', '50', '')[0], 'self_extinguished')
        self.assertEqual(cfig_outcome('Yes', 'FT', '30', '')[0], 'externally_terminated')
        self.assertEqual(cfig_outcome('No', '-', '0', '')[0], 'no_ignition')
        cls, fl = cfig_outcome('Yes', 'SE', '40', 'Manually stopped the flow.')
        self.assertEqual(cls, 'externally_terminated')
        self.assertIn('class_from_comment', fl)
        cls, fl = cfig_outcome('No', '-', '', 'direct cool - no hot ignition')
        self.assertEqual(cls, 'other')
        self.assertIn('class_from_comment', fl)
        self.assertEqual(cfig_outcome('No', '-', '', '')[0], 'unknown')

    def test_flash_is_unknown(self):  # decision D10
        cls, fl = cfig_outcome('flash', 'SE', '3', '')
        self.assertEqual(cls, 'unknown')
        self.assertIn('hot_ignition_value_flash_undocumented', fl)

    def test_censored_never_extinction(self):
        self.assertNotEqual(cfig_outcome('Yes', 'FT', '100', '')[0], 'self_extinguished')


class Materials(unittest.TestCase):
    def test_examples(self):
        m = normalize_material('1/4" clear rod')
        self.assertEqual(m['material_class'], 'solid_rod')
        self.assertAlmostEqual(float(m['ext']['rod_diameter_mm']), 6.35)
        m = normalize_material('100 micron PMMA film   2 cm wide')
        self.assertEqual((m['material_class'], m['thickness_mm'], m['width_cm']), ('film', 0.1, 2.0))
        m = normalize_material('2 cm SIBAL')
        self.assertEqual(m['material_class'], 'fabric')
        self.assertIn('dimension_meaning_unclear', m['flags'])
        self.assertEqual(normalize_material('Japan Wax candle')['material_class'], 'other')
        self.assertIn('non_burn_procedure', normalize_material('SOOT Cleaning')['flags'])
        self.assertEqual(normalize_material('PMMA 2 cm')['material_class'], 'unknown')


class FullBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.notes, cls.problems = build.build()
        cls.by_id = {r['test_id']: r for r in cls.rows}

    def test_no_check_problems(self):
        self.assertEqual(self.problems, [])

    def test_row_counts(self):
        c = collections.Counter(r['family'] for r in self.rows)
        self.assertEqual(c['FLEX'], 280)  # 274 PSI rows + tests 275-280 transcribed from the report (D11)
        self.assertEqual(c['CFI-G'], 333)  # 179 normal + 154 populated inverse (861 empty rows dropped)
        self.assertEqual(c['BASS-II'], 129)
        self.assertEqual(c['Saffire'], 23)  # 2 + 10 (9 samples, card 2-7 split) + 9 one-g rows + 2
        self.assertEqual(c['partial_gravity_literature'], 29)
        self.assertEqual(c['screening_1g'], 91)
        self.assertNotIn('BASS', c)  # decision D13

    def test_unique_ids_and_traceability(self):
        ids = [r['test_id'] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for r in self.rows:
            self.assertTrue(r['source_ref'])
            self.assertIn('quality_flags', r)
            self.assertIn(r['outcome_class'], OUTCOME_CLASSES)
            self.assertTrue(r['data_origin'])

    def test_cfig_outcome_counts(self):
        c = collections.Counter(r['outcome_class'] for r in self.rows if r['family'] == 'CFI-G')
        self.assertEqual(dict(c), {'self_extinguished': 173, 'externally_terminated': 91, 'no_ignition': 56, 'other': 3, 'unknown': 10})

    def test_flex_outcomes_from_test_end(self):
        flex = [r for r in self.rows if r['family'] == 'FLEX']
        self.assertEqual(collections.Counter(r['outcome_class'] for r in flex),
                         {'self_extinguished': 191, 'burned_to_completion': 28, 'other': 61})
        for r in flex:
            self.assertIn(r['outcome_raw'], ('Extinction', 'Completion', 'Disruption'))

    def test_saffire_corrections_and_conflict(self):
        by = {r['test_id']: r for r in self.rows}
        conf = [r for r in self.rows if 'source_conflict' in r['quality_flags'] and r['alt_value_report'].startswith('flow_velocity_cm_s=25')]
        self.assertEqual(len(conf), 1)
        self.assertEqual(float(conf[0]['flow_velocity_cm_s']), 20.0)
        for r in self.rows:
            if 'corrected_value' in json.loads(r['orig_values']).get('sample_thickness_mm', {}):
                self.assertAlmostEqual(float(r['sample_thickness_mm']), 0.37)

    def test_bass2_llm_proposals_not_used_until_approved(self):
        b2 = [r for r in self.rows if r['family'] == 'BASS-II']
        self.assertTrue(all(r['outcome_class'] == 'unknown' for r in b2))
        self.assertEqual(sum(1 for r in b2 if r['outcome_review_status'] == 'proposed'), 126)
        self.assertEqual(sum(1 for r in b2 if r['outcome_review_status'] == 'not_applicable'), 3)  # O20-O22
        for t in ('PSI-25:O20', 'PSI-25:O21', 'PSI-25:O22'):
            self.assertEqual(self.by_id[t]['outcome_class'], 'unknown')
            self.assertEqual(self.by_id[t]['outcome_raw'], '')

    def test_bass2_review_approval_flows_through(self):
        fake = {'PSI-25:B6': {'test_id': 'PSI-25:B6', 'decision': 'approved', 'approved_class': '', 'reviewer': 'x', 'reviewed_on': '', 'note': ''}}
        with mock.patch('pipeline.psi._load_review', return_value=fake):
            rows, _, problems = build.build()
        r = next(x for x in rows if x['test_id'] == 'PSI-25:B6')
        self.assertEqual((r['outcome_class'], r['outcome_review_status']), ('burned_to_completion', 'approved'))
        self.assertEqual([p for p in problems if 'count check' not in p], [])

    def test_bass2_numeric_flow_only_for_table_5_1(self):
        for r in self.rows:
            if r['family'] != 'BASS-II':
                continue
            has = r['flow_velocity_cm_s'] != ''
            self.assertEqual(has, r['test_id'] in {'PSI-25:M1', 'PSI-25:M5', 'PSI-25:M9', 'PSI-25:M15', 'PSI-25:M20'}, r['test_id'])
        self.assertEqual(self.by_id['PSI-25:M2']['flow_velocity_cm_s'], '')
        self.assertIn('multiple_flow_steps', self.by_id['PSI-25:M2']['quality_flags'])

    def test_bass2_pressure_only_where_stated(self):
        filled = [r['test_id'] for r in self.rows if r['family'] == 'BASS-II' and r['pressure_kpa'] != '']
        self.assertEqual(len(filled), 31)
        r = self.by_id['PSI-25:B3']
        self.assertEqual(r['pressure_kpa'], '101.325')
        self.assertIn('nominal', r['quality_flags'])
        self.assertEqual(json.loads(r['orig_values'])['pressure_kpa']['origin'], 'transcribed_from_text')

    def test_saffire_pairs(self):
        pairs = collections.defaultdict(list)
        for r in self.rows:
            if r['pair_id']:
                pairs[r['pair_id']].append(r)
        self.assertEqual(len(pairs), 9)
        for rs in pairs.values():
            self.assertEqual(sorted(r['gravity_level_g'] for r in rs), ['0', '1'])
        self.assertEqual(self.by_id['PSI-99:2-2:1g']['spread_rate'], '1.2')
        # "Insignificant" burn time stays in outcome_raw and burn_duration_s is empty (D14)
        r = self.by_id['PSI-99:2-1']
        self.assertEqual(r['burn_duration_s'], '')
        self.assertIn('Insignificant', r['outcome_raw'])
        self.assertIn('header_corrected', self.by_id['PSI-99:2-5']['quality_flags'])
        self.assertEqual(self.by_id['PSI-99:2-5']['spread_rate'], '2.1')

    def test_gravity_decision_d15(self):
        for r in self.rows:
            if r['psi_id'] and r['gravity_level_g'] == '0':
                self.assertEqual(r['gravity_source'], 'nominal')
        lunar = [r for r in self.rows if r['gravity_level_g'] == '0.165']
        self.assertEqual(len(lunar), 5)
        self.assertTrue(all(r['gravity_source'] == 'nominal' for r in lunar))

    def test_originals_kept_next_to_converted_values(self):
        for r in self.rows:
            if r['data_origin'] != 'psi_table':
                continue
            o = json.loads(r['orig_values'])
            for f in ('pressure_kpa', 'oxygen_fraction', 'oxygen_fraction_final', 'burn_duration_s', 'flow_velocity_cm_s', 'spread_rate'):
                if r[f] != '':
                    self.assertIn(f, o, f"{r['test_id']}: {f} has no recorded original")

    def test_transcribed_conversions_have_originals(self):
        for r in self.rows:
            if r['data_origin'] == 'psi_table':
                continue
            o = json.loads(r['orig_values'])
            if 'thickness_unit_converted' in r['quality_flags'] or 'thickness_from_table' in r['quality_flags']:
                self.assertIn('sample_thickness_mm', o, r['test_id'])
            if 'width_unit_converted' in r['quality_flags']:
                self.assertIn('sample_width_cm', o, r['test_id'])
            if 'pressure_unit_converted' in r['quality_flags']:
                self.assertIn('pressure_kpa', o, r['test_id'])

    def test_excluded_sources(self):
        self.assertFalse(any(r['psi_id'] in ('PSI-10', 'PSI-26') for r in self.rows))

    def test_deterministic(self):
        again, _, _ = build.build()
        self.assertEqual(self.rows, again)

    def test_checks_fail_loudly(self):
        bad = [dict(r) for r in self.rows]
        bad[0]['oxygen_fraction'] = '21.0'               # percent instead of fraction
        bad[1]['source_ref'] = ''                        # missing source
        bad[2]['test_id'] = bad[3]['test_id']            # duplicate id
        bad[4]['outcome_class'] = 'extinct'              # not an allowed value
        problems = checks.run_checks(bad)
        text = '\n'.join(problems)
        for needle in ('outside', 'empty source_ref', 'duplicate test_id', 'outcome_class'):
            self.assertIn(needle, text)

    def test_count_check_detects_drift(self):
        shifted = [dict(r) for r in self.rows]
        shifted[0]['outcome_class'] = 'other' if shifted[0]['outcome_class'] != 'other' else 'unknown'
        self.assertTrue(any('count check failed' in p for p in checks.run_checks(shifted)))

    def test_pipeline_exit_status_on_failure(self):
        with mock.patch('pipeline.build.build', return_value=([], {}, ['synthetic failure'])):
            self.assertEqual(build.main([]), 1)

    def test_validator_catches_bad_rows(self):
        bad = dict(self.rows[0], outcome_class='extinct', oxygen_fraction='1.5')
        self.assertGreaterEqual(len(validate_row(bad)), 2)


if __name__ == '__main__':
    unittest.main()
