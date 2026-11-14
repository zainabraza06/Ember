"""Paths, constants and limits for the evidence ledger."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_env_local():
    """Keys may be kept in <repo>/.env.local (KEY=value per line). The file is git-ignored; values are never printed or logged.
    Real environment variables win over the file."""
    f = ROOT / '.env.local'
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_local()
LEDGER_DIR = ROOT / 'data' / 'ledger'
SOURCES_CSV = LEDGER_DIR / 'sources.csv'
PAGES_JSONL = LEDGER_DIR / 'pages.jsonl'          # derived from the PDFs; git-ignored (regenerate with `python -m ledger pages`)
CACHE_DIR = LEDGER_DIR / 'cache'                  # one JSON file per LLM call; committed so a run can resume or be audited
CLAIMS_JSONL = LEDGER_DIR / 'claims.jsonl'
REJECTED_JSONL = LEDGER_DIR / 'rejected.jsonl'
REVIEW_CSV = ROOT / 'data' / 'review' / 'claim_review.csv'
AUDIT_MD = ROOT / 'docs' / 'CLAIM_AUDIT.md'
REPORT_MD = ROOT / 'docs' / 'LEDGER_REPORT.md'
PROMPTS_DIR = ROOT / 'prompts'
EXTRACT_PROMPT_VERSION = os.environ.get('LEDGER_EXTRACT_PROMPT', 'extract_v1')
VERIFY_PROMPT_VERSION = os.environ.get('LEDGER_VERIFY_PROMPT', 'verify_v1')
FUZZY_THRESHOLD = 0.95
CHUNK_CHARS = 9000          # target size of one extraction chunk (characters of page text)
VERIFY_CONTEXT_CHARS = 500  # page text around the span sent to the support check (keeps the Groq daily token use low)


def _chosen(provider):
    """Model chosen by `python -m ledger smoke` (data/ledger/providers.json)."""
    try:
        import json
        return json.loads((LEDGER_DIR / 'providers.json').read_text(encoding='utf-8')).get(provider, '')
    except (OSError, ValueError):
        return ''


def _f(name, default):
    v = os.environ.get(name)
    return float(v) if v not in (None, '') else default


# Decision D31: two model families, so that extraction and verification are independent.
#   extract -> Google Gemini API (free tier, Google AI Studio)   key: GEMINI_API_KEY
#   verify, rate -> Groq API, Llama 3.3 70B                      key: GROQ_API_KEY
# Decision D32: per-provider requests per minute / per day (+ tokens per minute / per day when known) and a total token cap.
# The official pages do not print the free-tier numbers (Gemini: "see Google AI Studio"; Groq: "see your account limits page"),
# so the defaults below are CONSERVATIVE PLACEHOLDERS that you should overwrite with the numbers shown in your own account
# (LEDGER_<PROVIDER>_RPM / _RPD / _TPM / _TPD). A 429 reply that names a daily quota stops the run cleanly regardless of these numbers.
PROVIDERS = {
    'gemini': {
        'key_env': 'GEMINI_API_KEY',
        'model': os.environ.get('LEDGER_GEMINI_MODEL', '') or _chosen('gemini'),           # chosen by `python -m ledger smoke` (strongest candidate that answers)
        'candidates': ['gemini-3.1-pro-preview', 'gemini-2.5-pro', 'gemini-3.8-flash', 'gemini-3.6-flash', 'gemini-2.5-flash'],
        'url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        'rpm': _f('LEDGER_GEMINI_RPM', 5), 'rpd': _f('LEDGER_GEMINI_RPD', 100), 'tpm': _f('LEDGER_GEMINI_TPM', 0), 'tpd': _f('LEDGER_GEMINI_TPD', 0),
        'day_tz': 'America/Los_Angeles',                                # Gemini daily quotas reset at midnight Pacific time
    },
    'groq': {
        'key_env': 'GROQ_API_KEY',
        'model': os.environ.get('LEDGER_GROQ_MODEL', '') or _chosen('groq') or 'llama-3.3-70b-versatile',
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'rpm': _f('LEDGER_GROQ_RPM', 20), 'rpd': _f('LEDGER_GROQ_RPD', 1000), 'tpm': _f('LEDGER_GROQ_TPM', 6000), 'tpd': _f('LEDGER_GROQ_TPD', 0),
        'day_tz': 'UTC',
    },
}
# Free-tier daily quotas are per model. When the preferred model's daily quota is used up the client moves to the next one;
# the model that produced every response is pinned in its cache entry and in each claim (model_version).
MODEL_CHAIN = {
    'gemini': [m for m in os.environ.get('LEDGER_GEMINI_MODELS', 'gemini-3.6-flash,gemini-3.7-flash,gemini-3.5-flash,gemini-3-flash-preview,gemini-2.5-flash,gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-2.5-flash-lite').split(',') if m],
}
KIND_PROVIDER = {'extract': 'gemini', 'verify': 'groq', 'rate': 'groq'}

MAX_TOKENS = int(os.environ.get('LEDGER_MAX_TOKENS', 3_000_000))   # total over the whole history, all providers
MAX_RETRIES = int(os.environ.get('LEDGER_MAX_RETRIES', 8))
DAILY_RETRY_AFTER_S = 900   # a Retry-After longer than this is treated as a daily limit
