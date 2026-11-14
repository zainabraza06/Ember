"""LLM extraction: pages -> chunks -> raw claims. Output of the model is parsed and validated, never repaired."""
import json

from . import config
from .llm import CacheMiss
from .pages import scope
from .schema import clean_raw_claim

MIN_PAGE_CHARS = 50


def chunks_for(src, doc_pages, max_chars=None):
    """Consecutive in-scope pages grouped to about max_chars; returns [(chunk_id, [page numbers])]."""
    max_chars = max_chars or config.CHUNK_CHARS
    allowed = scope(src)
    pages = [p for p in sorted(doc_pages) if (allowed is None or p in allowed) and len(doc_pages[p].strip()) >= MIN_PAGE_CHARS]
    out, cur, size = [], [], 0
    for p in pages:
        n = len(doc_pages[p])
        if cur and size + n > max_chars:
            out.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += n
    if cur:
        out.append(cur)
    return [(chunk_id(src['doc_id'], c), c) for c in out]


def chunk_id(doc_id, pages):
    return f'{doc_id}:p{pages[0]}-{pages[-1]}'


def chunk_text(doc_pages, pages):
    return '\n\n'.join(f'[PAGE {p}]\n{doc_pages[p].strip()}' for p in pages)


def parse_chunk(entry, pages):
    """-> (claims, problems_by_claim, error or None). entry is the cache entry."""
    if entry.get('finish_reason') == 'length':
        return [], [], 'truncated_output'
    try:
        obj = json.loads(entry['content'])
        raw = obj['claims']
        if not isinstance(raw, list):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return [], [], 'invalid_json'
    claims = []
    for r in raw:
        c, problems = clean_raw_claim(r, set(pages))
        if c is not None:
            c['flags'] = problems
            claims.append(c)
    return claims, [], None


def extract_chunk(client, src, doc_pages, pages, prompt_text, prompt_version, stats):
    """Extract one chunk; on truncated or invalid output, split the chunk in half once per level. Returns list of raw claims."""
    cid = chunk_id(src['doc_id'], pages)
    try:
        entry = client.complete('extract', src['sha256'], cid, prompt_version, prompt_text, chunk_text(doc_pages, pages), tag=src['doc_id'])
    except CacheMiss:
        stats['pending_chunks'].append(cid)
        return []
    claims, _, err = parse_chunk(entry, pages)
    if err:
        if len(pages) > 1:
            mid = len(pages) // 2
            stats['split_chunks'].append(cid)
            return (extract_chunk(client, src, doc_pages, pages[:mid], prompt_text, prompt_version, stats)
                    + extract_chunk(client, src, doc_pages, pages[mid:], prompt_text, prompt_version, stats))
        stats['failed_chunks'].append({'chunk': cid, 'error': err})
        return []
    for c in claims:
        c['chunk_id'] = cid
        c['model_version'] = entry['model_version']
        c['prompt_version'] = prompt_version
    stats['chunks_done'] += 1
    return claims
