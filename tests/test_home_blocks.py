"""Oxygen dial and spacecraft-fire timeline: built only from rows and claims that exist and are allowed."""
import csv, importlib.util, json, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts' / 'build_site.py')
bs = importlib.util.module_from_spec(spec); spec.loader.exec_module(bs)
CAPTION = ('Limits from the standard 1 g upward-burn test, mostly at 14.7 psia. The planned lunar base is 30% oxygen at 10.2 psi. '
           'Pressure and gravity change the result; this is a warning, not a design value.')


def site_data():
    html = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
    return html, json.loads(re.search(r'"oxygen_dial": (\[.*?\]), "timeline_ids"', html, re.S).group(1))


class HomeBlocks(unittest.TestCase):
    def test_timeline_uses_only_public_claims_about_spacecraft_fires(self):
        claims = {}
        with open(ROOT / 'data' / 'ledger' / 'claims.jsonl', encoding='utf-8') as f:
            for line in f:
                c = json.loads(line); claims[c['claim_id']] = c
        self.assertTrue(bs.TIMELINE_IDS)
        for cid in bs.TIMELINE_IDS:
            self.assertIn(claims[cid]['status'], ('verified_auto', 'approved'), cid)
            self.assertIn(claims[cid]['doc_id'], ('NTRS-20240002981', 'NTRS-20210011521'), cid)
        shown = {c['claim_id'] for c in json.loads((ROOT / 'site' / 'data' / 'ledger_claims.json').read_text(encoding='utf-8'))['claims']}
        self.assertTrue(set(bs.TIMELINE_IDS) <= shown)

    def test_dial_rows_have_a_printed_numeric_limit_and_a_stated_pressure(self):
        html, rows = site_data()
        self.assertGreater(len(rows), 50)
        src = {}
        for name in ('NTRS20110008636_limits', 'NTRS20170004702_limits'):
            for r in csv.DictReader(open(ROOT / 'data' / 'transcribed' / f'{name}.csv', encoding='utf-8')):
                src[r['test_id']] = r
        for r in rows:
            s = src[r['id']]
            self.assertTrue(s['pressure_kpa'], r['id'])
            self.assertEqual((r['u'], r['c']), (float(s['uloi_vol_pct']), float(s['moc_vol_pct'])), r['id'])
            self.assertEqual(s['gravity_level_g'], '1.0')
            self.assertLess(r['c'], r['u'] + 0.001)
            self.assertIn(r['psia'], (10.2, 14.7))
        # rows without a numeric limit or without a stated pressure are not used
        skipped = [i for i, s in src.items() if not s['pressure_kpa'] or not s['uloi_vol_pct'] or not s['moc_vol_pct']]
        self.assertFalse({r['id'] for r in rows} & set(skipped))

    def test_caption_is_on_the_page_verbatim(self):
        html, _ = site_data()
        self.assertIn(CAPTION, html)


if __name__ == '__main__':
    unittest.main()
