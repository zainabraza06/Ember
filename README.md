# Ember: a fire-safety evidence explorer for NASA microgravity combustion research

**Live site:** https://zainabraza06.github.io/Ember/ (GitHub Pages, branch `gh-pages`)
**Challenge:** Flame in Freefall, NASA Space Apps Challenge 2026 (Islamabad local event, 14 to 15 November 2026)
**Team:** a team of one with AI assistance (see [SI use and limits](#si-use-and-limits))

Ember turns NASA's scattered microgravity fire research into one place where you can **see where NASA has tested fire, where it has not, and what the cited evidence says**. It is a single static web page: no server, no build-time framework, no network calls at runtime, no model at runtime.

It answers three questions for a mission atmosphere such as the planned lunar base (30% oxygen at 10.2 psi):

1. *What has NASA tested?* A map of every test by oxygen share and total pressure.
2. *How sure are we?* Every statement comes from a quoted passage of a NASA report, checked by code, and every number carries its source. If the evidence does not cover a question, Ember says so instead of guessing.
3. *What should NASA test next?* A deterministic ranking of untested oxygen-pressure bands inside the lunar-base envelope.

> Ember is an evidence explorer, **not a safety assessment** and not a design tool. Results depend on pressure, gravity, geometry and flow; the page says so wherever it matters.

---

## Contents

- [What is on the site](#what-is-on-the-site)
- [Where the numbers come from](#where-the-numbers-come-from)
- [How the claims were checked](#how-the-claims-were-checked)
- [Honest limits](#honest-limits)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Rebuild everything](#rebuild-everything)
- [Tests](#tests)
- [Deploy](#deploy)
- [Design and accessibility](#design-and-accessibility)
- [SI use and limits](#si-use-and-limits)
- [Licences and third-party material](#licences-and-third-party-material)
- [Provenance](#provenance)
- [Documentation index](#documentation-index)

---

## What is on the site

The site is one page (`site/index.html`) with a home screen and a handful of views reached from one navigation bar (Atmosphere map, Ask the ledger, Data, Honest limits, and a "More" menu). Dark theme by default, light theme on request, reduced-motion respected.

### Home

| Block | What it shows |
|---|---|
| **Hero and stat strip** | The question Ember answers, a search box that opens Ask, and four counted numbers (investigations, cited claims, plotted tests, PSI lunar/Mars rows). The numbers count up once when they scroll into view (skipped under reduced motion). |
| **Moon safety margin** | Bar chart of the change in oxygen margin of safety for lunar and Martian gravity versus 1 g, transcribed from Table I of NTRS 20130010991. Labelled "outside PSI", from one paper. |
| **Oxygen dial** | A large keyboard- and touch-operable slider (15% to 40% oxygen, 44 px handle, markers for Earth air 21% and the lunar-base target 30%) over cards for 84 transcribed 1 g flammability-limit rows (ULOI and MOC as printed, NTRS 20110008636 and 20170004702, each with a numeric limit and a stated pressure). Each card shows the material, both limits, the test pressure, the source page and a state: *below its limit* (did not sustain flame in the standard test), *above its limit* (burned in the standard test), or, between the two printed limits, *some samples burned*. Cards that change state animate. Caption: "Limits from the standard 1 g upward-burn test, mostly at 14.7 psia. The planned lunar base is 30% oxygen at 10.2 psi. Pressure and gravity change the result; this is a warning, not a design value." |
| **The map** | Every test with both oxygen and pressure (643 of 769) as a mark by oxygen share and total pressure. Shape and colour show how the test ended. Filters by gravity level (0 g, 1 g, 0.165 g lunar, 0.38 g Mars). **Hatched cells have no test at all.** The lunar-base zone, the spacesuit condition and Earth sea level are marked. Hover or focus a point for a tooltip. An optional 3D view shows the same tests. |
| **Where should NASA test next?** | The five most relevant untested bands of oxygen and pressure inside the lunar-base atmosphere, ranked by distance to the design point. Select one to highlight the whole band on the map. Formula in [`docs/RANKING.md`](docs/RANKING.md). |
| **The ledger** | One verified claim next to a "no answer" card, to show Ember refuses what the evidence does not cover. |
| **What a spacecraft fire does** | A timeline of four public claims from NASA's Saffire reports, shown unchanged with their review label and page citation (including the smoke-alarm threshold reached at 981 s with most hazardous gas already released). The ledger holds no public claim on exposure limits or on temperature rising only near the fire, so none is shown. |
| **The investigations** | Prevention, detection and suppression: what NASA tested for each (BASS, SAME, FLEX, CFI-G and others). |
| **Honest limits and open data** | What is checked and how; downloads of the unified table, data dictionary and public claims. |

### Other views

| View | Purpose |
|---|---|
| **Ask the ledger** | Retrieval over the evidence ledger only. Type a question such as "lunar base at 30% oxygen and 10.2 psi" or "smoke detection in microgravity". The parser reads environment words (oxygen, pressure, gravity, diluent) and shows the answer with its source label, the claim, its quoted text, page and review label. A relevance gate returns **"no answer"** for out-of-scope questions (for example "who won the cricket match"). Twelve demo queries are built in. No model runs in the browser. |
| **Investigations and comparison** | All 24 PSI combustion investigations with objectives, approach, conditions varied and measurements, with side-by-side comparison. |
| **Ranking** | A deterministic score (0 to 100) of the 24 investigations for a chosen mission atmosphere (lunar base, pressurized rover, spacesuit, ISS), with the formula shown. |
| **Interpretation** | Three effect summaries computed from the test table: FLEX droplets (oxygen and diluent versus extinction), ACME CFI-G gas flames (oxygen versus how tests ended) and Saffire-II (0 g versus 1 g for the same sample), each with counts, caveats, the recorded source conflict and an evidence-strength label from a fixed rule. |
| **Mission brief** | A cited, printable one-page brief for the lunar base. Every sentence carries a source number. Has a print stylesheet for A4. |
| **Mission atmospheres** | The official lunar-base, rover and spacesuit conditions, with how many test rows fall inside each. |
| **Partial gravity** | What the evidence bounds: 0 g and 1 g side by side for nine Saffire-II samples, and the **gap**: PSI holds no lunar or Martian gravity combustion rows. |
| **Earth applications** | Where the findings connect to fire safety on Earth. |
| **About / Honest limits** | Method, review status, SI use, data licences. |
| **Judge mode** | A 25-second guided tour of the lunar-base zone, an Ask answer with its citation, a refusal and the honest limits. |

---

## Where the numbers come from

All data is public and cited. Nothing is invented; anything undocumented is shown as "not documented in the catalog".

| Source | Used for |
|---|---|
| **NASA Physical Sciences Informatics (PSI)** combustion investigations and their data tables (CC0 as stated in each record) | The unified test table, investigation descriptions |
| **NASA Technical Reports Server (NTRS)** reports (56 catalogued; the ledger's claims come from 11 of them) | Claims, quoted passages, transcribed tables (cited, not redistributed; NTRS rights determinations are not open licences) |
| **Official challenge text** | Mission atmospheres, the gap statement, suggested resources (copied to [`docs/CHALLENGE.md`](docs/CHALLENGE.md)) |

### The unified test table

`python -m pipeline` harmonizes the PSI tables and hand-transcribed NTRS tables into `data/processed/tests.csv` (885 rows, 769 tests plus oxygen-limit rows; also `tests.parquet`). Every row has a source reference, a data origin, a gravity level and quality flags. Automated data checks fail the build loudly if counts, ranges or citations drift. See [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md), [`docs/OUTCOME_MAPPING.md`](docs/OUTCOME_MAPPING.md) and [`docs/GRAVITY_COVERAGE.md`](docs/GRAVITY_COVERAGE.md).

Hand-transcribed tables (`data/transcribed/`):

- `NTRS20110008636_limits.csv` and `NTRS20170004702_limits.csv`: 1 g flammability limits (ULOI and MOC) used by the oxygen dial
- `NTRS20130010991_tableI_limits.csv`: oxygen margin of safety (Moon safety margin chart)
- `NTRS20010059376_series.csv`: partial-gravity literature series
- `NTRS20150023456_flex_tests_275_280.csv`: FLEX tests
- `NTRS20250010653_luci_tests.csv`: LUCI lunar-gravity tests

### The evidence ledger

`python -m ledger` extracts claims from 11 NASA reports into `data/ledger/claims.jsonl`. A claim is one statement tied to a **verbatim quoted span** on a **specific page** of a **specific report**. See [`docs/LEDGER_SCHEMA.md`](docs/LEDGER_SCHEMA.md) and the generated [`docs/LEDGER_REPORT.md`](docs/LEDGER_REPORT.md).

---

## How the claims were checked

Counts here are computed from the ledger files by `ledger/review_wording.py`, the single source the site, the ledger report and the tests all read. They cannot drift from the data.

- **255 public claims, each opened and checked against its source page by the reviewer (ZRM).**
- **181** of them passed the automatic checks first: code checks for the exact text span, numbers and conditions, plus a second AI model (a different model family from the extractor).
- **74** were held back by those checks and approved after an AI-assisted page check, which the reviewer then checked herself. 25 of them carry a corrected statement or gravity class; a reworded statement is re-checked by code against its span, and a span can only be extended, never replaced.
- **2** claims were approved by manual override of the number check (C-f4d3c81aef, C-cbca12ebcd), and are marked as such.
- **7** claims were rejected and **3** are held back and not published. None of these 10 is shown as checked, and none is used to answer.
- **Spot check of transcribed table values:** all 10 sampled values were AI-checked against the PDFs, and 2 were also checked by ZRM ([`docs/HUMAN_SPOT_CHECK.md`](docs/HUMAN_SPOT_CHECK.md)).

Claim cards on the site show the path each claim took ("Automatic checks passed" or "AI-assisted page check") plus "Opened and checked by ZRM".

Wording guard: `tests/test_review_wording.py` fails the build if any page or document states a different number of public claims, uses an overstated review phrase (listed in the test), or describes a rejected or held-back claim with a checked-or-approved word.

The review records are `data/review/claim_review.csv` (every decision, the original wording and the AI suggestion), `data/review/gravity_relabel.csv` and `data/review/outcome_review.csv`.

---

## Honest limits

- **NASA's archive has no partial-gravity combustion data yet.** Ember shows the gap rather than filling it. The few lunar and Martian rows come from published reports and are labelled "outside PSI".
- The oxygen dial uses a 1 g test mostly at 14.7 psia. It is a warning, not a design value; pressure, gravity, geometry and flow change the result.
- Transcribed report values were spot-checked, not independently verified in full.
- Some rows lack oxygen or pressure and cannot be placed on the map (126 of 769 tests).
- The "test next" ranking uses a fixed, documented formula; it is a prioritisation aid, not a recommendation from NASA.
- The extraction models used free-tier APIs with daily limits, so the ledger covers 11 priority reports, not all of NTRS.
- NTRS reports carry NASA rights determinations that are not open licences, so they are cited and linked, not redistributed.

---

## Repository layout

| Path | Purpose |
|---|---|
| `site/` | The built site. `index.html` is one self-contained page (data, scripts and fonts inlined). `site/data/` holds the downloads (`tests.csv`, `ledger_claims.json`, data dictionary). |
| `scripts/site_template.html` | Page source: HTML, CSS and all page JavaScript (map, Ask, dial, timeline, brief, judge mode). |
| `scripts/build_site.py` | Builds `site/index.html` from the data files and the template. |
| `scripts/ask_parser.js`, `scripts/hero_cube.js` | Ask query parser and the 3D/2D plots, inlined at build time. |
| `scripts/fonts/` | Sora, IBM Plex Sans and IBM Plex Mono (SIL OFL), embedded as base64. |
| `scripts/*.py` (others) | Source fetching, observation extraction, review application, review queue and conflict reports. |
| `pipeline/` | Harmonization pipeline (standard library plus pyarrow): PSI readers, transcribed tables, outcome rules, material normalizer, data checks, ranking, interpretation, mission profiles, spot check. |
| `ledger/` | Evidence ledger: extraction, verification, second rater, review application, display filter, report, `review_wording.py`. |
| `prompts/` | Extraction, verification and BASS-II rater prompts, with a changelog. |
| `data/raw/` | PSI tables and NTRS source information (large PDFs are git-ignored; URL, size and SHA-256 are kept in each `info.md`). |
| `data/transcribed/` | Hand-transcribed NTRS tables with citations. |
| `data/processed/` | Harmonized test table, ranking, interpretations, mission profiles, build report. |
| `data/ledger/` | Claims, rejected claims, page text index, source list, usage and run logs, model cache. |
| `data/review/` | Reviewer decisions. |
| `data/llm/` | AI-proposed BASS-II outcome classes (not used until approved). |
| `tests/` | 96 unit tests. |
| `docs/` | Challenge text, rules, requirements, status, data notes, ranking rules, ledger report, submission draft, SI log, third-party register. |
| `PLAN.md` | Original scope, modules and acceptance criteria. |

---

## Quick start

Open the built site directly, no server needed:

```
site/index.html
```

or visit the live URL above. To work on it, you need Python 3 and Node.js only for the parser tests.

```
pip install -r requirements.txt        # pyarrow
pip install -r requirements-dev.txt    # pypdf and pymupdf, development only
```

## Rebuild everything

From the repository root:

```
python -m pipeline                    # harmonized test table, parquet and build report; fails loudly on a data-check failure
python -m pipeline.profiles           # mission atmosphere profiles
python -m pipeline.ranking            # investigation ranking
python -m pipeline.interpret          # effect summaries
python -m ledger all --offline --skip-pilot   # rebuild the ledger from the cache (no API calls)
python -m ledger report               # regenerate docs/LEDGER_REPORT.md
python scripts/build_site.py          # write site/index.html and site/data/
```

On Windows use `python -X utf8 ...`.

### Re-running the extraction (needs API keys)

`GEMINI_API_KEY` and `GROQ_API_KEY` must be in the environment or the git-ignored `.env.local`, never in a tracked file.

```
python -m ledger smoke                                   # check both providers answer
python scripts/fetch_ledger_sources.py                   # fetch new source PDFs
python -m ledger extract --skip-pilot --docs <ids> --stop-at HH:MM
```

It resumes from `data/ledger/cache/` after any interruption and stops cleanly at a daily limit.

## Tests

```
python -m unittest discover -s tests -q
```

96 tests cover the pipeline and its data checks, the ledger checks (span, numbers, conditions, review rules), the Ask parser (run through Node), the site build, the single-source review wording and the home-page blocks (oxygen dial rows, spacecraft-fire timeline claims). A 20-row random spot check against the sources is available with `python -m pipeline.spot_check`.

Browser checks used for each release: no JavaScript errors and no sideways scroll at 390 px and 1366 px, judge mode still 25 s, and the Mission brief printing on one A4 page.

## Deploy

The site is static. Build, commit, then publish the `site/` folder to the `gh-pages` branch:

```
python scripts/build_site.py
git add -A && git commit -m "..."
git push origin main
git branch -D gh-pages ; git subtree split --prefix=site -b gh-pages
git push -f origin gh-pages
```

GitHub Pages serves it at https://zainabraza06.github.io/Ember/ (allow a minute or two for it to update).

---

## Design and accessibility

- Dark default with a light option; keyboard navigation throughout; visible focus; text contrast of at least 4.5:1.
- Controls are at least 44 px; the layout works at a 390 px phone width.
- Charts use colour **and** shape, carry text alternatives, and have a "See the numbers" table where they summarise data.
- `prefers-reduced-motion` and a motion toggle switch off animation (count-up, card flips, reveals, orbit).
- No external requests: fonts, data and scripts are inlined, so the page works offline.
- Print stylesheet for the Mission brief.

---

## SI use and limits

An AI coding assistant (Claude, via Claude Code) helped write the pipeline, the checks, the tests and this page. Claim extraction used a language model (Google Gemini, free tier); a second model from a different family (OpenAI's open-weight gpt-oss-120b, served by Groq) checked each claim; code checks the quoted text, numbers and conditions against the report. AI-proposed BASS-II outcome classes (`data/llm/`) are not used until approved in `data/review/outcome_review.csv`. The reviewer, Zainab Raza (ZRM), opened and checked each public claim against its source page (see [How the claims were checked](#how-the-claims-were-checked)).

**The page itself runs no model and makes no network calls.** Rankings, summaries, the mission brief and the Ask answers are computed by fixed rules from the data. Every tool, what it did and what a person reviewed is logged in [`docs/SI_USAGE.md`](docs/SI_USAGE.md).

---

## Licences and third-party material

- **Code:** Apache License 2.0 (see `LICENSE`).
- **Data:** PSI records are CC0 as stated per record. NTRS reports keep their own NASA rights determinations and are cited, not redistributed. Hand-transcribed numbers are facts with citations.
- **Fonts:** Sora, IBM Plex Sans and IBM Plex Mono, SIL Open Font License 1.1, embedded in the page.
- **No third-party JavaScript, CSS framework, icon set or image** is in the web page.
- Development-only: `pypdf` and `pymupdf` (AGPL-3.0 or commercial; not a runtime dependency).

The full register, with licence and source URL for every dataset, library and model, is [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md).

---

## Provenance

This repository was created on 2026-11-14 as a single import of the project files. The data pipeline, document checks and evidence-ledger code in it were developed from 2026-10-19 to 2026-11-14 in an earlier local repository (about 25 commits, kept as an archive by the team); the explorer page, the official-alignment document and the submission drafts were produced on 2026-11-14 and after. Dates inside `docs/` record when each step actually happened. The import does not claim that the work was done on the day of import.

---

## Documentation index

| Document | Contents |
|---|---|
| [`PLAN.md`](PLAN.md) | Scope, modules, acceptance criteria, risks |
| [`docs/CHALLENGE.md`](docs/CHALLENGE.md) | The official challenge text |
| [`docs/RULES.md`](docs/RULES.md), [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md), [`docs/STATUS.md`](docs/STATUS.md) | Rules, requirement tracking, status |
| [`docs/OFFICIAL_ALIGNMENT.md`](docs/OFFICIAL_ALIGNMENT.md) | How the site maps to the official challenge text |
| [`docs/SUBMISSION_DRAFT.md`](docs/SUBMISSION_DRAFT.md) | The submission text and form fields |
| [`docs/DATA_SURVEY.md`](docs/DATA_SURVEY.md), [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | Sources surveyed and the test-table columns |
| [`docs/OUTCOME_MAPPING.md`](docs/OUTCOME_MAPPING.md), [`docs/GRAVITY_COVERAGE.md`](docs/GRAVITY_COVERAGE.md), [`docs/CONFLICTS.md`](docs/CONFLICTS.md) | Outcome classes, gravity coverage, source conflicts |
| [`docs/LEDGER_SCHEMA.md`](docs/LEDGER_SCHEMA.md), [`docs/LEDGER_REPORT.md`](docs/LEDGER_REPORT.md), [`docs/CLAIM_AUDIT.md`](docs/CLAIM_AUDIT.md) | Ledger design, generated report (including how claims were checked), random claim audit |
| [`docs/REVIEW_QUEUE.md`](docs/REVIEW_QUEUE.md), [`docs/SPOT_CHECK.md`](docs/SPOT_CHECK.md), [`docs/HUMAN_SPOT_CHECK.md`](docs/HUMAN_SPOT_CHECK.md) | Review queue and spot checks |
| [`docs/RANKING.md`](docs/RANKING.md) | Investigation score, evidence strength, data-gap and next-test band rules |
| [`docs/SI_USAGE.md`](docs/SI_USAGE.md), [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md) | AI tool log, third-party register |
