"""LLM client for the ledger: Google Gemini (extraction) and Groq (verification, second rater), with a response cache,
per-provider rate limiting, exponential backoff and clean stops.

* API keys are read from GEMINI_API_KEY and GROQ_API_KEY at call time. They are sent only in a request header and are never printed,
  logged, cached or written to any file (error bodies are truncated and contain no request headers).
* Every successful call is cached in data/ledger/cache/<key>.json. The key hashes (provider, model, kind, document checksum, item id,
  prompt version), so an interrupted run resumes from the cache and never repeats a finished call (D27).
* The cache entry pins the exact model name/version the API returned.
* D32 limits: requests per minute and per day (and tokens per minute / per day) per provider, plus LEDGER_MAX_TOKENS in total.
  Reaching a daily limit raises DailyLimit, the CLI saves progress and reports what remains; a rerun the next day resumes.
Standard library only (urllib)."""
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from . import config


class BudgetReached(Exception):
    """LEDGER_MAX_TOKENS reached."""


class DailyLimit(Exception):
    """A provider's per-day quota is used up (own counter or a 429 that names a daily quota)."""


class RateLimited(Exception):
    """Per-minute retries exhausted; the run stops cleanly and can be resumed."""


class CacheMiss(Exception):
    pass


USAGE_LOG = config.LEDGER_DIR / 'usage.jsonl'
RUN_LOG = config.LEDGER_DIR / 'run_log.jsonl'
STOPS = (BudgetReached, DailyLimit, RateLimited)


def cache_key(kind, doc_checksum, item_id, prompt_version, model, provider=''):
    raw = '\x1f'.join([provider, model, kind, doc_checksum, item_id, prompt_version])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:40]


def _append(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + '\n')


def log_event(event, **kw):
    _append(RUN_LOG, {'t': time.strftime('%Y-%m-%dT%H:%M:%S'), 'event': event, **kw})


def read_usage():
    if not USAGE_LOG.exists():
        return []
    with open(USAGE_LOG, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def usage_totals():
    u = read_usage()
    return sum(x.get('total_tokens', 0) for x in u), len(u)


def day_key(provider, ts=None):
    """Calendar day in the timezone in which the provider's daily quota resets."""
    ts = ts or datetime.now(timezone.utc)
    name = config.PROVIDERS[provider]['day_tz']
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(name)
    except Exception:  # noqa: BLE001 - tzdata missing on some Windows installs
        tz = timezone(timedelta(hours=-8 if name != 'UTC' else 0))
    return ts.astimezone(tz).strftime('%Y-%m-%d')


def today_usage(provider):
    req = tok = 0
    key = day_key(provider)
    for u in read_usage():
        if u.get('provider') == provider and u.get('ts') and day_key(provider, datetime.fromisoformat(u['ts'])) == key:
            req += 1
            tok += u.get('total_tokens', 0)
    return req, tok


# ----------------------------------------------------------------------------------------------- provider request/response shapes
def build_request(provider, model, system, user, max_tokens):
    p = config.PROVIDERS[provider]
    key = os.environ.get(p['key_env'], '')
    if not key:
        raise SystemExit(f"{p['key_env']} is not set. Set it in the environment (never in a file) and rerun; the run resumes from the cache.")
    if provider == 'gemini':
        headers = {'Content-Type': 'application/json', 'x-goog-api-key': key}
        payload = {'systemInstruction': {'parts': [{'text': system}]}, 'contents': [{'role': 'user', 'parts': [{'text': user}]}],
                   'generationConfig': {'temperature': 0, 'responseMimeType': 'application/json', 'maxOutputTokens': max_tokens}}
        url = p['url'].format(model=model)
    else:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}
        payload = {'model': model, 'temperature': 0, 'seed': 0, 'max_tokens': min(max_tokens, 8000), 'response_format': {'type': 'json_object'},
                   'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
        url = p['url']
    return url, headers, payload


def parse_response(provider, resp):
    """-> dict(content, finish_reason, model_version, response_id, prompt_tokens, completion_tokens, total_tokens)."""
    if provider == 'gemini':
        cand = (resp.get('candidates') or [{}])[0]
        parts = (cand.get('content') or {}).get('parts') or []
        content = ''.join(x.get('text', '') for x in parts if not x.get('thought'))
        u = resp.get('usageMetadata', {})
        total = u.get('totalTokenCount', 0)
        return {'content': content, 'finish_reason': {'STOP': 'stop', 'MAX_TOKENS': 'length'}.get(cand.get('finishReason', ''), cand.get('finishReason', '')),
                'model_version': resp.get('modelVersion', ''), 'response_id': resp.get('responseId', ''),
                'prompt_tokens': u.get('promptTokenCount', 0), 'completion_tokens': total - u.get('promptTokenCount', 0), 'total_tokens': total}
    ch = resp['choices'][0]
    u = resp.get('usage', {})
    return {'content': ch['message']['content'] or '', 'finish_reason': ch.get('finish_reason', ''), 'model_version': resp.get('model', ''),
            'response_id': resp.get('id', ''), 'prompt_tokens': u.get('prompt_tokens', 0), 'completion_tokens': u.get('completion_tokens', 0),
            'total_tokens': u.get('total_tokens', 0)}


def http_transport(provider, url, headers, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={**headers, 'Accept': 'application/json'}, method='POST')
    r = urllib.request.urlopen(req, timeout=240)
    return json.loads(r.read().decode('utf-8')), dict(r.headers.items())


def model_for(provider):
    m = config.PROVIDERS[provider]['model']
    if not m:
        raise SystemExit(f'No model chosen for {provider}. Run `python -m ledger smoke` (it picks the strongest Gemini candidate that answers) or set LEDGER_GEMINI_MODEL.')
    return m


class Client:
    def __init__(self, offline=False, transport=None, sleep=time.sleep):
        self.offline = offline
        self.transport = transport or http_transport     # tests inject a mock: transport(provider, url, headers, payload) -> (json, headers)
        self.sleep = sleep
        self._last = {}
        self._window = {}                                # provider -> [(time, tokens)] for the tokens-per-minute limiter
        self.session_calls = self.session_cached = 0

    # ---- public
    def complete(self, kind, doc_checksum, item_id, prompt_version, system, user, max_tokens=8000, tag=''):
        provider = config.KIND_PROVIDER[kind]
        model = model_for(provider)
        key = cache_key(kind, doc_checksum, item_id, prompt_version, model, provider)
        path = config.CACHE_DIR / f'{key}.json'
        if path.exists():
            self.session_cached += 1
            return json.loads(path.read_text(encoding='utf-8'))
        if self.offline:
            raise CacheMiss(f'{kind} {item_id}')
        self._guard(provider)
        url, headers, payload = build_request(provider, model, system, user, max_tokens)
        resp = self._with_retries(provider, url, headers, payload, f'{kind} {item_id}')
        r = parse_response(provider, resp)
        entry = {'kind': kind, 'provider': provider, 'item_id': item_id, 'doc_checksum': doc_checksum, 'prompt_version': prompt_version,
                 'requested_model': model, 'model_version': r['model_version'], 'response_id': r['response_id'], 'finish_reason': r['finish_reason'],
                 'usage': {k: r[k] for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')}, 'created': time.strftime('%Y-%m-%dT%H:%M:%S'),
                 'content': r['content'], 'tag': tag}
        config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        _append(USAGE_LOG, {'kind': kind, 'provider': provider, 'item_id': item_id, 'model_version': r['model_version'], 'prompt_tokens': r['prompt_tokens'],
                            'completion_tokens': r['completion_tokens'], 'total_tokens': r['total_tokens'], 'tag': tag,
                            'ts': datetime.now(timezone.utc).isoformat(timespec='seconds')})
        self._window.setdefault(provider, []).append((time.time(), r['total_tokens']))
        self.session_calls += 1
        return entry

    # ---- limits
    def _guard(self, provider):
        tokens, _ = usage_totals()
        if tokens >= config.MAX_TOKENS:
            raise BudgetReached(f'LEDGER_MAX_TOKENS reached: {tokens} of {config.MAX_TOKENS} tokens')
        p = config.PROVIDERS[provider]
        req, tok = today_usage(provider)
        if p['rpd'] and req >= p['rpd']:
            raise DailyLimit(f"{provider}: {req} requests today reached the daily limit of {int(p['rpd'])} (LEDGER_{provider.upper()}_RPD)")
        if p['tpd'] and tok >= p['tpd']:
            raise DailyLimit(f"{provider}: {tok} tokens today reached the daily limit of {int(p['tpd'])} (LEDGER_{provider.upper()}_TPD)")

    def _pace(self, provider):
        p = config.PROVIDERS[provider]
        if p['rpm']:
            wait = 60.0 / p['rpm'] + 0.2 - (time.time() - self._last.get(provider, 0))
            if wait > 0:
                self.sleep(wait)
        if p['tpm']:
            now = time.time()
            win = [(t, n) for t, n in self._window.get(provider, []) if now - t < 60]
            self._window[provider] = win
            if win and sum(n for _, n in win) >= p['tpm'] * 0.8:
                self.sleep(max(0.0, 61 - (now - win[0][0])))
        self._last[provider] = time.time()

    @staticmethod
    def _is_daily(detail, retry_after):
        d = (detail or '').lower()
        return ('perday' in d.replace(' ', '').replace('_', '') or 'per day' in d or 'requests per day' in d or 'tokens per day' in d
                or 'daily' in d or (retry_after is not None and retry_after > config.DAILY_RETRY_AFTER_S))

    def _with_retries(self, provider, url, headers, payload, what):
        delay = 2.0
        for attempt in range(1, config.MAX_RETRIES + 1):
            self._pace(provider)
            try:
                body, _hdr = self.transport(provider, url, headers, payload)
                return body
            except urllib.error.HTTPError as e:
                code = e.code
                ra = None
                try:
                    ra = float(e.headers.get('Retry-After')) if e.headers and e.headers.get('Retry-After') else None
                except (TypeError, ValueError):
                    ra = None
                detail = ''
                try:
                    detail = e.read().decode('utf-8', 'replace')[:600]
                except Exception:  # noqa: BLE001
                    pass
                if code == 429:
                    if self._is_daily(detail, ra):
                        log_event('daily_limit', provider=provider, what=what, http=429)
                        raise DailyLimit(f'{provider}: HTTP 429 naming a daily quota ({detail[:160]!r})')
                    pause = min(ra if ra is not None else delay, 120.0) + random.uniform(0, 1)
                    log_event('retry', provider=provider, what=what, http=429, attempt=attempt, pause_s=round(pause, 1))
                    self.sleep(pause)
                    delay = min(delay * 2, 120.0)
                    continue
                if code in (500, 502, 503, 504):
                    log_event('retry', provider=provider, what=what, http=code, attempt=attempt)
                    self.sleep(min(delay, 60.0) + random.uniform(0, 1))
                    delay = min(delay * 2, 120.0)
                    continue
                if code in (400, 401, 403, 404):
                    raise ApiError(provider, code, detail)
                raise ApiError(provider, code, detail)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                log_event('retry', provider=provider, what=what, error=type(e).__name__, attempt=attempt)
                self.sleep(min(delay, 60.0))
                delay = min(delay * 2, 120.0)
        log_event('rate_limit_exhausted', provider=provider, what=what)
        raise RateLimited(f'{provider}: {what}')


class ApiError(RuntimeError):
    def __init__(self, provider, code, detail):
        super().__init__(f'{provider} HTTP {code}: {detail[:300]}')
        self.provider, self.code, self.detail = provider, code, detail
