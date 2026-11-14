# Ember (working name)

**Challenge:** Flame in Freefall: AI-Powered Fire Safety Insights from Microgravity Combustion Data, NASA Space Apps Challenge 2026.
**Event:** Islamabad local event, hackathon weekend 14–15 November 2026.

**Goal.** Ember turns NASA's scattered microgravity fire research into a verified evidence ledger, then answers one real question for any mission, "What will burn here, how sure are we, and what should NASA test next?", and exports the answer as a cited fire-safety brief (PLAN.md section 2).

**Status: build phase** (19 October to 13 November 2026; final testing and submission during the event, 14-15 November). Data foundation (M0-M2) is done; the evidence ledger, ranking, interpretation, brief and dashboard are next. Scope, rules and requirement tracking live in [PLAN.md](PLAN.md), [docs/RULES.md](docs/RULES.md), [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) and [docs/STATUS.md](docs/STATUS.md).

## Layout
| Path | Purpose |
|---|---|
| `PLAN.md` | Source of truth: scope, modules, acceptance criteria |
| `docs/` | Challenge text, rules, requirements, status, data notes |
| `data/raw/`, `data/processed/`, `data/ledger/` | Raw sources, harmonized tables, evidence ledger (provenance rules in PLAN.md) |
| `eval/` | Evaluation assets (M10) |
| `pipeline/`, `tests/` | M2 harmonization pipeline and its tests |
| `data/processed/tests.csv` | Harmonized test table (885 rows; also `tests.parquet`; see docs/DATA_DICTIONARY.md) |

## Rebuild the harmonized test table
Python 3 from the repository root (`pip install -r requirements.txt` for pyarrow; the dev tools are in `requirements-dev.txt`):
```
python -m pipeline                          # writes data/processed/tests.csv, tests.parquet and build_report.json; fails loudly if a data check fails
python -m unittest discover -s tests -t .   # tests
python -m pipeline.spot_check               # 20-row random spot check against the sources (pip install pypdf for the PDF rows)
```

## Evidence ledger (M3)
`python -m ledger` extracts and verifies claims from the NASA reports listed in `data/ledger/sources.csv` using the Gemini API for extraction and Groq (Llama 3.3 70B) for verification (`GEMINI_API_KEY` and `GROQ_API_KEY` in the environment, never in a file; `python -m ledger smoke` checks both). It resumes from `data/ledger/cache/` after any interruption; `python -m ledger --offline` rebuilds from the cache without calling the API. New source PDFs are fetched by `scripts/fetch_ledger_sources.py`. See `docs/LEDGER_SCHEMA.md` and `docs/LEDGER_REPORT.md`.

## Explorer page (static)
`python -m pipeline && python -m pipeline.profiles && python scripts/build_site.py` writes `site/index.html` (no server needed; open it or host the `site/` folder on any static host). Docs: `docs/OFFICIAL_ALIGNMENT.md`, `docs/SUBMISSION_DRAFT.md`.

## Provenance (read this)
This repository was created on 2026-11-14 as a single import of the project files. The data pipeline, document checks and evidence-ledger code in it were developed from 2026-10-19 to 2026-11-14 in an earlier local repository (about 25 commits, kept as an archive by the team); the explorer page, the official-alignment document and the submission drafts were produced on 2026-11-14. Dates inside `docs/` (STATUS.md, SI_USAGE.md, SPOT_CHECK.md and others) record when each step actually happened. The import does not claim that the work was done today.

## Live explorer
https://zainabraza06.github.io/Ember/ (GitHub Pages, branch `gh-pages`). Rebuild and redeploy: `python -m pipeline && python -m pipeline.profiles && python -m pipeline.ranking && python -m pipeline.interpret && python scripts/build_site.py`, commit, then `git subtree split --prefix=site -b gh-pages && git push -f origin gh-pages`. The evidence ledger needs `GEMINI_API_KEY` and `GROQ_API_KEY` (environment or the git-ignored `.env.local`): `python -m ledger extract --skip-pilot --docs <ids> --stop-at HH:MM`.
