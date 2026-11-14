"""Text layer of each source PDF -> data/ledger/pages.jsonl (one JSON object per page: doc_id, page, text).

Page numbers are PDF page indices (1-based), the same convention as the source_ref values in the unified test table.
Requires pypdf (development tool, see requirements-dev.txt)."""
import csv
import json

from .config import PAGES_JSONL, ROOT, SOURCES_CSV


def read_sources():
    with open(SOURCES_CSV, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def scope(src):
    """scope_pages like '1-40,60-70' -> sorted page list, or None for all pages."""
    spec = (src.get('scope_pages') or '').strip()
    if not spec:
        return None
    out = set()
    for part in spec.split(','):
        a, _, b = part.strip().partition('-')
        out.update(range(int(a), int(b or a) + 1))
    return sorted(out)


def build_pages():
    from pypdf import PdfReader
    n_docs = n_pages = 0
    with open(PAGES_JSONL, 'w', encoding='utf-8', newline='\n') as f:
        for src in read_sources():
            rd = PdfReader(str(ROOT / src['local_path']))
            for i, pg in enumerate(rd.pages, 1):
                try:
                    text = pg.extract_text() or ''
                except Exception as e:  # noqa: BLE001 - a broken page is recorded as empty, never invented
                    text = ''
                    print('warn', src['doc_id'], i, e)
                f.write(json.dumps({'doc_id': src['doc_id'], 'page': i, 'text': text}, ensure_ascii=False) + '\n')
                n_pages += 1
            n_docs += 1
            print(src['doc_id'], len(rd.pages), 'pages')
    print(n_docs, 'documents,', n_pages, 'pages ->', PAGES_JSONL)


def load_pages():
    pages = {}
    with open(PAGES_JSONL, encoding='utf-8') as f:
        for line in f:
            o = json.loads(line)
            pages.setdefault(o['doc_id'], {})[o['page']] = o['text']
    return pages
