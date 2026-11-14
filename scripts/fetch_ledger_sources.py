"""M3: download the NTRS reports used by the evidence ledger and write data/ledger/sources.csv.

Idempotent: existing PDFs are kept (SHA-256 recorded). Only documents listed in DOCS are fetched (public NTRS API, robots.txt
allows it). New PDFs are git-ignored (see .gitignore); URL and SHA-256 are in sources.csv. Standard library only.
Run from the repo root: python scripts/fetch_ledger_sources.py
"""
import csv
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# NTRS id -> why it is in the ledger (one line)
DOCS = {
    '20150023456': 'FLEX detailed results (droplet extinction, microgravity)',
    '20210011385': 'BASS-II summary report (solid fuel, flow and O2 limits)',
    '20170008805': 'Saffire I/II results presentation',
    '20010059376': 'Upward flame spread over thin solids in partial gravity',
    '20130010991': 'Material flammability in microgravity and Martian gravity vs 1 g',
    '20250010653': 'Lunar Combustion Investigation (LUCI) rocket results',
    '20110008636': 'Selected parametric effects on materials flammability limits (1 g)',
    '20170004702': 'NASA-STD-6001B Test 1 sample length impact on MOC (1 g)',
    '20260001966': 'Material flammability at lunar and Martian gravity (presentation)',
    '20210020516': 'Fire on the Moon: solid fuel combustion experiments',
    '20240008623': 'Flammability of materials on the Moon',
    '20040053567': 'Upward and downward flame spreading in partial gravity',
    '20010074003': 'Three-dimensional upward flame spreading in partial-gravity buoyant flows',
    '20160000593': 'Combustion of solids in microgravity: BASS-II results',
    '20140011099': 'Thickness and fuel preheating effects on flammability in microgravity',
    '20150008961': 'Microgravity flammability of PMMA rods in concurrent flow',
    '20170006615': 'Mixed convection blowoff limits vs oxygen and upward flow',
    '20210011521': 'Fire safety implications of Saffire IV and V results',
    '20240002981': 'Preliminary results from Saffire VI',
    '20200000361': 'SoFIE project on ISS',
    '20040053586': 'CO2 suppression of PMMA flames in low gravity',
    '20260002050': 'Surface vehicle atmospheric considerations for Moon to Mars exploration (exploration atmospheres)',
}
# Narrative pages only for the two long reports: FLEX Tables IX and Appendix B and BASS-II Appendix A are per-test data already in the
# unified test table (M2), not findings. Empty = all pages.
SCOPE = {'20150023456': '1-25', '20210011385': '1-109'}
# Documents that report the same experiment campaign share a study_family (used for the independent-source count); all others stand alone.
FAMILY = {'20210011385': 'BASS-II', '20160000593': 'BASS-II'}
FIELDS = ['doc_id', 'ntrs_id', 'title', 'authors', 'year', 'sti_type', 'rights_determination', 'author_types', 'us_government_work',
          'display_verbatim', 'study_family', 'url', 'pdf_url', 'local_path', 'bytes', 'sha256', 'retrieved_date', 'scope_pages', 'why_included']


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'ember-research/0.1 (NASA Space Apps 2026 research project)'})
    return urllib.request.urlopen(req, timeout=120).read()


def main():
    existing = {}
    sp = ROOT / 'data/ledger/sources.csv'
    if sp.exists():
        existing = {r['ntrs_id']: r for r in csv.DictReader(open(sp, encoding='utf-8'))}
    rows = []
    for nid, why in DOCS.items():
        rec = json.loads(get(f'https://ntrs.nasa.gov/api/citations/{nid}'))
        dets = rec.get('copyright', {}).get('determinationType', '')
        types = sorted({a.get('userType', '') for a in rec.get('authorAffiliations', [])})
        names = '; '.join(a['meta']['author']['name'] for a in rec.get('authorAffiliations', []))
        dl = [d for d in rec.get('downloads', []) if d.get('mimetype') == 'application/pdf' or str(d.get('links', {}).get('pdf', '')).endswith('.pdf')]
        folder = ROOT / 'data/raw/ntrs' / nid
        pdfs = sorted(folder.glob('*.pdf')) if folder.exists() else []
        if not pdfs:
            if not dl:
                print(nid, 'NO PDF in record')
                continue
            link = dl[0]['links']['pdf']
            url = 'https://ntrs.nasa.gov' + link if link.startswith('/') else link
            folder.mkdir(parents=True, exist_ok=True)
            data = get(url)
            (folder / url.rsplit('/', 1)[-1]).write_bytes(data)
            pdfs = sorted(folder.glob('*.pdf'))
            time.sleep(1)
        pdf = pdfs[0]
        b = pdf.read_bytes()
        gov = 'yes' if dets == 'GOV_PUBLIC_USE_PERMITTED' else 'no'
        old = existing.get(nid, {})
        rows.append({
            'doc_id': f'NTRS-{nid}', 'ntrs_id': nid, 'title': rec['title'], 'authors': names,
            'year': ((rec.get('publications') or [{}])[0].get('publicationDate') or rec.get('distributionDate') or rec.get('created') or '')[:4], 'sti_type': rec.get('stiType', ''),
            'rights_determination': dets, 'author_types': ';'.join(types), 'us_government_work': gov, 'display_verbatim': gov,
            'url': f'https://ntrs.nasa.gov/citations/{nid}', 'pdf_url': f'https://ntrs.nasa.gov/api/citations/{nid}/downloads/{pdf.name}',
            'local_path': pdf.relative_to(ROOT).as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
            'retrieved_date': old.get('retrieved_date') or time.strftime('%Y-%m-%d'), 'scope_pages': SCOPE.get(nid, ''), 'study_family': FAMILY.get(nid, f'NTRS-{nid}'), 'why_included': why})
        print(nid, dets, gov, len(b))
    with open(sp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'documents ->', sp)


if __name__ == '__main__':
    main()
