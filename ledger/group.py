"""Grouping of claims that assert the same finding, and the independent-source count.

Deterministic: claims share a group when they have the same gravity class, effect direction and primary variables, and their
statements overlap (token Jaccard >= 0.5, single link). Groups are computed over claims that may reach the UI (verified_auto, approved).
independent_sources = number of distinct study families among the members; study_family defaults to the document itself, and two
documents share a family only where sources.csv says so (the same experiment campaign reported twice)."""
import hashlib
import re

THRESHOLD = 0.5
STOP = set('the a an of in at to and or for with was were is are by on as that this it its from be been than then which when'.split())


def tokens(s):
    return {t for t in re.findall(r'[a-z0-9.]+', s.lower()) if t not in STOP and len(t) > 1}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def group_key(c):
    vs = sorted(v for v in c['variables'] if v != 'other')[:3]
    return f"{c['conditions']['gravity_class']}|{','.join(vs)}|{c['effect_direction']}"


def assign_groups(claims, sources):
    elig = [c for c in claims if c['status'] in ('verified_auto', 'approved')]
    for c in claims:
        c['group_id'] = None
        c['group_size'] = 0
        c['independent_sources'] = 0
    buckets = {}
    for c in elig:
        buckets.setdefault(group_key(c), []).append(c)
    for key, items in buckets.items():
        items.sort(key=lambda c: c['claim_id'])
        toks = {c['claim_id']: tokens(c['statement']) for c in items}
        parent = {c['claim_id']: c['claim_id'] for c in items}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                if jaccard(toks[a['claim_id']], toks[b['claim_id']]) >= THRESHOLD:
                    parent[find(b['claim_id'])] = find(a['claim_id'])
        clusters = {}
        for c in items:
            clusters.setdefault(find(c['claim_id']), []).append(c)
        for members in clusters.values():
            first = min(m['claim_id'] for m in members)
            gid = 'G-' + hashlib.sha1(f'{key}|{first}'.encode()).hexdigest()[:10]
            fams = {(sources.get(m['doc_id']) or {}).get('study_family') or m['doc_id'] for m in members}
            for m in members:
                m['group_id'] = gid
                m['group_size'] = len(members)
                m['independent_sources'] = len(fams)
