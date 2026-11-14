"""`python -m ledger smoke`: one minimal call to each provider (key valid, JSON output works, model name returned).
Prints only model names and token counts; never the keys."""
import json
import urllib.error

from . import config
from .llm import ApiError, build_request, http_transport, parse_response

SYSTEM = 'Return one JSON object and nothing else.'
USER = 'Return {"ok": true, "word": "ember"}.'


def try_model(provider, model):
    url, headers, payload = build_request(provider, model, SYSTEM, USER, 2000)
    resp, hdr = http_transport(provider, url, headers, payload)
    r = parse_response(provider, resp)
    obj = json.loads(r['content'])
    ok = obj.get('ok') is True
    lim = {k: v for k, v in hdr.items() if k.lower().startswith('x-ratelimit')}
    return ok, r, lim


def smoke():
    results = {}
    for provider in ('gemini', 'groq'):
        p = config.PROVIDERS[provider]
        models = [p['model']] if p['model'] else p.get('candidates', ['llama-3.3-70b-versatile'])
        results[provider] = None
        for m in models:
            try:
                ok, r, lim = try_model(provider, m)
                print(f"[{provider}] model requested {m!r} -> returned {r['model_version']!r}; JSON ok={ok}; finish={r['finish_reason']}; tokens={r['total_tokens']}")
                if lim:
                    print(f'[{provider}] rate-limit headers: {lim}')
                if ok:
                    results[provider] = {'requested': m, 'returned': r['model_version']}
                    break
            except urllib.error.HTTPError as e:
                print(f'[{provider}] {m!r}: HTTP {e.code} {e.reason}')
            except ApiError as e:
                print(f'[{provider}] {m!r}: HTTP {e.code} {e.detail[:160]!r}')
            except (ValueError, KeyError) as e:
                print(f'[{provider}] {m!r}: unusable answer ({type(e).__name__})')
    if all(results.values()):
        (config.LEDGER_DIR / 'providers.json').write_text(json.dumps({k: v['requested'] for k, v in results.items()}, indent=1) + '\n', encoding='utf-8')
    for provider, res in results.items():
        print(f"SMOKE {provider}: {'PASS ' + json.dumps(res) if res else 'FAIL'}")
    return 0 if all(results.values()) else 1
