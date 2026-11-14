"""Guards the wording about how the claims were checked: one number everywhere, and no 'checked/verified' said about rejected or held-back claims."""
import json, re, unittest
from pathlib import Path

from ledger import config, review_wording

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / 'site' / 'index.html', ROOT / 'README.md', ROOT / 'STATUS.md'] + sorted((ROOT / 'docs').glob('*.md')) + [ROOT / 'data' / 'review' / 'claim_review.csv']
BANNED = ('verified by a person', 'reviewed and verified', 'peer-reviewed', 'peer reviewed', 'expert review', 'expert-review', 'verified by an expert', 'human-verified')
NEG = re.compile(r"\b(not|neither|never|nor|none|no)\b|n't", re.I)


def texts():
    for p in FILES:
        if p.exists():
            yield p, p.read_text(encoding='utf-8')


def sentences(t):
    return [x for x in re.split(r'(?<=[.!?])\s+|\n', re.sub(r'<[^>]+>', ' ', t)) if x.strip()]


class ReviewWording(unittest.TestCase):
    def setUp(self):
        self.s = review_wording.summary()

    def test_counts_are_the_ones_in_the_ledger(self):
        s = self.s
        self.assertEqual((s['public'], s['auto'], s['ai_page_check'], s['rejected'], s['held_back']), (255, 181, 74, 7, 3))
        self.assertEqual(s['public'], s['auto'] + s['ai_page_check'])
        self.assertTrue(config.REVIEWER_CHECKED_ALL_PUBLIC)

    def test_no_text_says_another_number_of_public_claims(self):
        for p, t in texts():
            if p.name == 'LEDGER_REPORT.md' or 'data' in p.parts:
                continue
            for m in re.finditer(r'(\d+)\s+(?:of them\s+)?(?:public|reviewed|checked)\s+claims', t):
                self.assertEqual(int(m.group(1)), self.s['public'], f'{p.name}: "{m.group(0)}"')
            for m in re.finditer(r'(?:all|each of the)\s+(\d+)\s+public claims', t):
                self.assertEqual(int(m.group(1)), self.s['public'], f'{p.name}: "{m.group(0)}"')

    def test_banned_phrases_are_absent(self):
        for p, t in texts():
            low = t.lower()
            for b in BANNED:
                if b in low:
                    self.fail(f'{p.name} contains "{b}" near: ...{low[max(0, low.index(b) - 60):low.index(b) + 80]}...')

    def test_nothing_is_called_checked_or_verified_about_rejected_or_held_back_claims(self):
        for p, t in texts():
            if 'data' in p.parts:
                continue
            for sent in sentences(t):
                low = sent.lower()
                if re.search(r'\b(rejected|held back|held-back|needs[_ ]review|unpublished)\b', low) and re.search(r'\b(verified|opened and checked|checked by zrm|reviewed by zrm)\b', low):
                    self.assertRegex(low, NEG, f'{p.name}: "{sent.strip()[:160]}"')

    def test_generated_sentences_pass_the_same_rules(self):
        w = review_wording.words(self.s)
        for k, v in w.items():
            self.assertNotIn('verified by a person', v.lower(), k)
        for k in ('excluded',):
            self.assertRegex(w[k].lower(), NEG)
        self.assertIn('255 public claims', w['all'])

    def test_site_carries_the_canonical_sentences(self):
        site = ROOT / 'site' / 'index.html'
        if not site.exists():
            self.skipTest('site not built')
        html = site.read_text(encoding='utf-8')
        for k, v in review_wording.words(self.s).items():
            if k in ('all', 'auto', 'ai', 'excluded', 'spot', 'tag_zrm', 'tag_auto', 'tag_ai', 'ask_note') and v:
                self.assertIn(json.dumps(v, ensure_ascii=False)[1:-1], html, k)

    def test_held_back_and_rejected_claims_are_not_public(self):
        with open(config.CLAIMS_JSONL, encoding='utf-8') as f:
            kept = [json.loads(line) for line in f]
        public = {c['claim_id'] for c in kept if c['status'] in review_wording.PUBLIC}
        path = ROOT / 'site' / 'data' / 'ledger_claims.json'
        shown = {c['claim_id'] for c in json.loads(path.read_text(encoding='utf-8'))['claims']} if path.exists() else set()
        self.assertTrue(shown <= public)
        self.assertEqual(len(public), self.s['public'])


if __name__ == '__main__':
    unittest.main()
