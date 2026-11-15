# Ember: a fire-safety evidence explorer for NASA microgravity combustion research

[![Live site](https://img.shields.io/badge/live%20site-zainabraza06.github.io%2FEmber-7CC2FF)](https://zainabraza06.github.io/Ember/)
![Static site](https://img.shields.io/badge/runtime-static%20page%2C%20no%20server%2C%20no%20model-FF8A5C)
![Tests](https://img.shields.io/badge/tests-96%20unit%20tests-8CE6B2)
![Licence](https://img.shields.io/badge/code-Apache--2.0-lightgrey)

**Live site:** https://zainabraza06.github.io/Ember/ (GitHub Pages, branch `gh-pages`)
**Challenge:** *Flame in Freefall*, NASA Space Apps Challenge 2026 (Islamabad local event, 14 to 15 November 2026)
**Team:** a team of one with AI assistance (see [SI use, licences and provenance](#13-si-use-licences-and-provenance))

![Ember home page](docs/screenshots/01-home-hero.jpg)

Ember turns NASA's scattered microgravity fire research into one place where you can **see where NASA has tested fire, where it has not, and what the cited evidence says**. It is a single static web page: no server, no framework at runtime, no network calls, and **no model running in the browser**. Everything it shows is computed from public NASA data by deterministic code, and every statement is tied to a source row or a quoted page of a NASA report.

It answers three questions for a mission atmosphere such as the planned lunar base (30% oxygen at 10.2 psi):

1. **What has NASA tested?** A map of every test by oxygen share and total pressure, with the untested space hatched.
2. **How sure are we?** Claims come from quoted passages of NASA reports, checked by code, cross-checked by a second model, and opened and checked by a human reviewer. If the evidence does not cover a question, Ember says so instead of guessing.
3. **What should NASA test next?** A deterministic ranking of untested oxygen and pressure bands inside the lunar-base envelope.

> Ember is an evidence explorer. It is **not a safety assessment** and not a design tool. Flammability depends on pressure, gravity, geometry and flow; the page says so wherever it matters.

---

## Contents

1. [Quick start](#1-quick-start)
   - [Tech stack](#tech-stack)
2. [The challenge and how Ember meets it](#2-the-challenge-and-how-ember-meets-it)
3. [Guided tour with screenshots](#3-guided-tour-with-screenshots)
4. [Architecture at a glance](#4-architecture-at-a-glance)
5. [Technical core, part 1: the unified test table](#5-technical-core-part-1-the-unified-test-table)
6. [Technical core, part 2: the evidence ledger](#6-technical-core-part-2-the-evidence-ledger)
7. [Technical core, part 3: ranking, interpretation and the data-gap ranking](#7-technical-core-part-3-ranking-interpretation-and-the-data-gap-ranking)
8. [Technical core, part 4: the Ask engine](#8-technical-core-part-4-the-ask-engine)
9. [Technical core, part 5: the static site build](#9-technical-core-part-5-the-static-site-build)
10. [Setup, dependencies and how to run everything](#10-setup-dependencies-and-how-to-run-everything)
11. [Testing and quality gates](#11-testing-and-quality-gates)
12. [Repository layout](#12-repository-layout)
13. [SI use, licences and provenance](#13-si-use-licences-and-provenance)
14. [Honest limits and what is not done](#14-honest-limits-and-what-is-not-done)
15. [Documentation index](#15-documentation-index)

---

## 1. Quick start

**Just look at it:** open https://zainabraza06.github.io/Ember/ or open `site/index.html` from this repository in any modern browser (no server needed).

**Run and rebuild locally** (Python 3 and Node.js; no other build tools):

```bash
git clone https://github.com/zainabraza06/Ember.git && cd Ember
pip install -r requirements.txt            # pyarrow (parquet output)
python -m pipeline                         # harmonized test table (885 rows) and data checks
python -m pipeline.profiles && python -m pipeline.ranking && python -m pipeline.interpret
python scripts/build_site.py               # writes site/index.html and site/data/
python -m http.server -d site 8000         # optional: serve at http://localhost:8000
python -m unittest discover -s tests -q    # 96 tests
```

The evidence ledger is already built and committed (`data/ledger/claims.jsonl`), so the commands above need **no API keys**. Re-extracting claims from the NASA reports does need keys; see [section 10](#10-setup-dependencies-and-how-to-run-everything).

---

## Tech stack

| Layer | Technology | Used for |
|---|---|---|
| Language | Python 3 (developed on 3.12), standard library first | pipeline, ledger, site build, tests |
| Data | CSV, JSONL, JSON, Apache Parquet via `pyarrow` | unified test table, claims, review records |
| PDF handling | `pypdf` (text layer), `pymupdf` (development only) | page text for quote checks, table transcription |
| Extraction models | Google Gemini (extractor), gpt-oss-120b on Groq (cross-check) | proposing and cross-checking claims, offline only |
| Verification | Deterministic Python code | exact quote span, numbers, conditions, gravity words |
| Front end | One HTML file with vanilla JavaScript, CSS and canvas; no framework or library | map, oxygen dial, Ask, ranking views, 3D plot |
| Ask engine | `scripts/ask_parser.js` (deterministic parser, term-weighted claim search) | condition-aware retrieval in the browser, no model |
| Fonts | Sora, IBM Plex Sans, IBM Plex Mono (SIL OFL), embedded | typography |
| Tests | `unittest` (96 tests), Node.js for the Ask parser | quality gates |
| Browser checks | headless Chrome | layout, console errors, screenshots |
| Hosting | GitHub Pages (`gh-pages` branch) | serving the static page |
| Docs | Markdown with Mermaid diagrams | this README and `docs/` |

---

## 2. The challenge and how Ember meets it

The official text is kept in [`docs/CHALLENGE.md`](docs/CHALLENGE.md). In short: NASA's PSI archive holds decades of microgravity combustion results that are hard to find, harder to compare and harder to interpret. The task is an SI-powered, web-based dashboard that **summarizes, ranks and interprets** combustion science investigations for fire safety, and optionally helps users (1) identify investigations relevant to crew environments, (2) extract data for predictive flammability modelling, and (3) highlight research for next-generation fire safety controls. Fire safety is framed as **prevention, detection and suppression**, and the Moon base atmosphere (30% oxygen or more at 10.2 psi or less) is the focus case.

The full line-by-line audit is [`docs/OFFICIAL_ALIGNMENT.md`](docs/OFFICIAL_ALIGNMENT.md). The verdicts below are honest ones, taken from that audit (its own tally: 9 met, 4 met with a qualifier, 10 partly met, 2 not met, 1 not applicable):

| Official requirement | Verdict | Where in Ember |
|---|---|---|
| **Web-based dashboard** | met | A static page on GitHub Pages; works offline once loaded. |
| **SI-powered** | partly met | The page runs no model, by design (reproducible, citable, no keys in the browser). SI built the pipeline and extracted and cross-checked the claims it retrieves; the SI use is disclosed in [`docs/SI_USAGE.md`](docs/SI_USAGE.md). |
| **Summarizes** investigations | partly met | Investigations view: objective, approach, conditions varied and measurements, verbatim from each PSI record, plus ranges computed from the table. Interpretation view: three computed analyses. |
| **Ranks** investigations | met (rule-based) | Ranking view: a documented deterministic score for all 24 investigations in four profiles, with the weights shown ([section 7](#7-technical-core-part-3-ranking-interpretation-and-the-data-gap-ranking)). |
| **Interprets** findings | partly met | Interpretation view: FLEX oxygen and diluent versus extinction, CFI-G oxygen versus how tests ended, Saffire-II 0 g versus 1 g, each with counts, caveats and an evidence-strength label. |
| Objective 1: investigations relevant to spacecraft, stations, bases and rovers | partly met | Atmosphere map, Mission atmospheres and Ranking (profiles: lunar base, pressurized rover, spacesuit, ISS-like cabin; a Mars base is shown as an explicit assumption). |
| Objective 2: data for predictive modelling | partly met | The unified table is downloadable (`tests.csv`, `tests.parquet`, data dictionary) with a source reference and quality flags on every row. No model is trained. |
| Objective 3: research for next-generation controls and equipment | not met | Prevention, detection and suppression tags and the spacecraft-fire timeline give context, but nothing specifically selects next-generation controls. |
| Earth applications (water mist, smoke detection, firefighter gear) | partly met | The Earth view names the three areas and links the three spinoff resources. |
| Per investigation: objectives, fuels, conditions, variables, sensors | partly met | All 24 PSI combustion investigations are listed with objectives verbatim; structured conditions exist only for the 6 investigations with per-test rows; the rest say "not documented in the catalog". |
| Similarities and differences between investigations | met | Compare view, short fields marked same, differs or not documented. |
| DAFT and DAFT-2, BRE, hardware groups (ACME, MDCA, MSG) | met | Listed and filterable. |
| Prevention / detection / suppression | met | Tags with the reason on hover (13 of 24 tagged; the others have no supporting text for a tag). |
| Spacesuit 100% O2 at 4.3 psi; Moon base 30% O2 or more at 10.2 psi or less | met | Mission atmospheres and the map zones; kPa computed in code; the suit condition has no test row and is shown as a gap. |
| Highest-oxygen microgravity tests are ACME CFI-G (up to 85%) | met | Computed from the table. |
| **No partial-gravity data in PSI** (LUCI and FM2 expected; E-FIELD mimics it) | met | The stat strip shows **0**; the Partial gravity view shows 0 g and 1 g side by side and the lunar and Mars gap; the few lunar and Mars values come from published reports and are labelled "outside PSI". |
| History of fires (Apollo 1, Apollo 13, Mir, Artemis II) | not met | Linked in About, not presented. |
| The ten NASA resources | met (linked) | Listed with links in About; the data-bearing ones (PSI, NTRS) were used. |

Event rules ([`docs/RULES.md`](docs/RULES.md)) are tracked in [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md): SI-use disclosure ([`docs/SI_USAGE.md`](docs/SI_USAGE.md)), third-party licences ([`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md)), every source cited, no NASA logos, and an open licence for original content (Apache-2.0).

---

## 3. Guided tour with screenshots

All screenshots are of the live site (`docs/screenshots/`). The nav has Atmosphere map, Ask the ledger, Data, Honest limits and a **More** menu; the site has **12 views** in total, plus a **25 s tour** button (judge mode).

### 3.1 Home page, in the order the blocks appear

**Hero and stat strip.** The question, a search box that opens Ask, and four counted numbers: 24 NASA combustion investigations, 255 claims each with a page citation, 643 tests mapped by oxygen and pressure, and **0 partial-gravity tests in PSI**. The numbers are counted from the build, never typed.

![Hero](docs/screenshots/01-home-hero.jpg)

**Moon safety margin.** What one NASA paper (NTRS 20130010991, Table I) reports for the oxygen margin of safety at lunar (0.165 g) and Martian (0.38 g) gravity for Mylar, Ultem and Nomex, compared with the 1 g limit. A negative value means the flame survives at a lower oxygen level. It is labelled *outside PSI, one paper, 3 fuels*, with a "warning sign, not a design value" note.

![Moon safety margin](docs/screenshots/02-moon-safety-margin.jpg)

**Oxygen dial.** A keyboard- and touch-operable slider from 15% to 40% oxygen with markers at Earth air (21%) and the lunar-base target (30%), over cards for 84 transcribed **1 g flammability-limit rows** (ULOI and MOC as printed in NTRS 20110008636 and 20170004702). Each card shows the material, both limits, the test pressure and the source page, and one of three states: *below its limit* (did not sustain flame in the standard test), *above its limit* (burned in the standard test), or *between its two printed limits* (some samples burned). The caption reads: "Limits from the standard 1 g upward-burn test, mostly at 14.7 psia. The planned lunar base is 30% oxygen at 10.2 psi. Pressure and gravity change the result; this is a warning, not a design value."

![Oxygen dial](docs/screenshots/03-oxygen-dial.jpg)

**The map.** Every test with both oxygen and pressure (643 of 769) as a mark by oxygen share and total pressure. Shape and colour show how the test ended; **hatched cells have no test at all**. Gravity filters (0 g, 1 g, 0.165 g, 0.38 g), the lunar-base zone, the spacesuit condition, Earth sea level, hover tooltips and an optional 3D view of the same tests. The no-partial-gravity notice is part of the map, not a footnote.

![Atmosphere map](docs/screenshots/04-atmosphere-map.jpg)

**Where should NASA test next?** The five most relevant untested bands of oxygen and pressure inside NASA's planned lunar-base atmosphere (306 of 340 grid cells are untested; 51 of those are inside the lunar-base envelope). Each card shows the band, how many tests are nearby, the closest investigation and a button that highlights the whole band on the map. It is a data-gap ranking, not a safety judgement ([algorithm](#73-the-data-gap-ranking-where-should-nasa-test-next)).

![Where next](docs/screenshots/05-where-next-ranking.jpg)

**The ledger.** One verified claim beside a deliberate "no answer" card, to show that Ember refuses what the evidence does not cover.

![Ledger](docs/screenshots/06-ledger-card.jpg)

**Spacecraft fire.** A timeline of four public claims from NASA's Saffire reports, each shown exactly as stored with its review label and page citation, including the smoke-alarm threshold reached at 981 seconds with most of the hazardous gas already released. The ledger has no public claim on exposure limits, so none is shown.

![Spacecraft fire](docs/screenshots/07-spacecraft-fire-timeline.jpg)

**The investigations.** Prevention, detection, suppression: what NASA tested for each safety area (BASS and BASS-II, SAME and SAME-R, FLEX and FLEX-2, CFI-G and E-FIELD).

![Investigations block](docs/screenshots/08-investigations-block.jpg)

**Honest limits and open data.** What is checked and how (the same sentences as the ledger report), and downloads of the unified table, the data dictionary and the public claims.

![Honest limits and open data](docs/screenshots/09-honest-limits-open-data.jpg)

### 3.2 Ask the ledger

Retrieval over the evidence ledger and the test table only. Type a question or a condition such as "lunar base at 30% oxygen and 10.2 psi". A **cited answer** shows the claim, the review path ("Opened and checked by ZRM", plus "Automatic checks passed" or "AI-assisted page check"), the report, the PDF page and the claim id. An **off-topic question is refused** ("Not in the evidence", with suggestions). A condition query returns the matching tests, their outcome classes, the source labels and a table of rows.

| Cited answer | Honest refusal | Condition query |
|---|---|---|
| ![Cited answer](docs/screenshots/14-ask-cited-answer.jpg) | ![Refusal](docs/screenshots/15-ask-refusal.jpg) | ![Conditions](docs/screenshots/16-ask-conditions-table.jpg) |

### 3.3 The other views

| Investigations | Compare |
|---|---|
| ![Investigations](docs/screenshots/10-investigations.jpg) | ![Compare](docs/screenshots/11-compare.jpg) |
| All 24 PSI combustion investigations: objective, approach, conditions varied, measurements, tags with reasons, hardware group. | Two or three investigations side by side; short fields marked same, differs or not documented. |

| Ranking | Interpretation |
|---|---|
| ![Ranking](docs/screenshots/12-ranking.jpg) | ![Interpretation](docs/screenshots/13-interpretation.jpg) |
| A fixed formula scores the 24 investigations for lunar base, pressurized rover, spacesuit and ISS-like cabin (and a Mars base *assumption*); the weights and the score breakdown are shown. | Three computed effect summaries with counts, caveats, recorded source conflicts and an evidence-strength label. |

| Mission brief | Mission atmospheres |
|---|---|
| ![Brief](docs/screenshots/17-mission-brief.jpg) | ![Atmospheres](docs/screenshots/18-mission-atmospheres.jpg) |
| A printable one-page brief for the lunar base; every sentence carries a source number. A print stylesheet makes it a clean A4 page. | Official envelopes in psi and computed kPa, and how many test rows fall inside each. |

| Partial gravity | Earth applications |
|---|---|
| ![Partial gravity](docs/screenshots/19-partial-gravity.jpg) | ![Earth](docs/screenshots/20-earth-applications.jpg) |
| What the evidence bounds: 0 g and 1 g side by side for nine Saffire-II samples, and the lunar and Mars gap. | Water-mist extinguishers, terrestrial smoke detection and protective clothing, with the NASA spinoff links. |

| Honest limits | About |
|---|---|
| ![Limits](docs/screenshots/21-honest-limits-tab.jpg) | ![About](docs/screenshots/22-about.jpg) |
| What this explorer cannot tell you, stated plainly. | Method, review status, SI use, data licences and the ten official resources. |

### 3.4 Light theme and phone layout

Dark by default with a light option; the layout works at a 390 px phone width with controls of at least 44 px.

| Light theme | Phone: home | Phone: dial | Phone: map |
|---|---|---|---|
| ![Light](docs/screenshots/23-light-theme.jpg) | ![Phone home](docs/screenshots/24-mobile-home.jpg) | ![Phone dial](docs/screenshots/25-mobile-oxygen-dial.jpg) | ![Phone map](docs/screenshots/26-mobile-map.jpg) |

### 3.5 Judge mode

The **25 s tour** button walks through the lunar-base zone, a condition query, a cited Ask answer, an off-topic refusal and the honest limits, with captions. Esc stops it and it can be paused. The tour drives the same page, so what a judge sees is what the data says.

---

## 4. Architecture at a glance

```mermaid
flowchart LR
  A[NASA PSI tables<br/>data/raw/psi] --> P[pipeline/<br/>harmonize + data checks]
  T[Hand-transcribed NTRS tables<br/>data/transcribed] --> P
  P --> TC[(data/processed/tests.csv<br/>885 rows, parquet)]
  P --> R[ranking.py, interpret.py,<br/>profiles.py]
  N[NTRS reports<br/>PDF text layer] --> L[ledger/<br/>extract, verify, review]
  L --> CL[(data/ledger/claims.jsonl<br/>255 public claims)]
  TC --> B[scripts/build_site.py]
  R --> B
  CL --> B
  RV[data/review/<br/>reviewer decisions] --> L
  B --> S[site/index.html<br/>one static page]
  S --> U((Browser: map, dial, Ask,<br/>no model, no network))
```

Two properties hold the design together:

- **Everything on the page is data or a template filled with data.** No sentence is generated at run time; numbers on the page are counted from the build, and the same inputs produce the same bytes (the pipeline is deterministic: stable ordering, no timestamps).
- **Provenance is mandatory.** A test row without a `source_ref` fails the build. A claim without a verbatim span found on a named PDF page never reaches the page.

How a question is answered in the browser:

```mermaid
sequenceDiagram
  participant U as User
  participant P as ask_parser.js
  participant T as test table (JSON in the page)
  participant L as claims (JSON in the page)
  U->>P: "lunar base at 30% oxygen and 10.2 psi"
  P->>P: read environment words (oxygen, pressure, gravity, diluent), units, operators
  P->>P: relevance gate: is any real key term present?
  alt nothing relevant
    P-->>U: "Not in the evidence" + suggestions
  else conditions or topic found
    P->>T: filter rows (tolerances: oxygen +-0.5 points, pressure +-3%)
    P->>L: score public claims by key terms, gravity filter
    P-->>U: counts, outcomes with source labels, table, cited claims
  end
```

---

## 5. Technical core, part 1: the unified test table

**Goal.** Make decades of results comparable: one table where every row has oxygen, pressure, gravity, fuel, diluent, flow, outcome and a source.

**Inputs.**
- PSI investigation tables for the combustion investigations (CC0, as stated in each PSI record), fetched by `scripts/fetch_psi_tables.py` into `data/raw/psi/`.
- Hand-transcribed numeric tables from NASA NTRS reports in `data/transcribed/` (each row carries report, PDF page and table): 1 g flammability limits (NTRS 20110008636, 20170004702), oxygen margin of safety (20130010991), a partial-gravity series (20010059376), FLEX tests (20150023456) and LUCI tests (20250010653).
- PSI-10 is excluded (its licence field is empty) and PSI-26 (BASS) is used only by the evidence ledger.

**Output.** `data/processed/tests.csv` and `tests.parquet`: **885 rows** = 769 tests + 100 oxygen-limit rows + 16 series summaries. Families: CFI-G (333), FLEX (280), BASS-II (129), 1 g screening limits (91), partial-gravity literature (29), Saffire (23). Gravity: 759 rows at 0 g, 105 at 1 g, 5 at 0.165 g, 3 at 0.38 g, 13 unstated. Origin: 759 PSI table rows and 126 transcribed or read from figures. Column definitions are in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

**What the pipeline does (`pipeline/`).**

| Module | Job |
|---|---|
| `psi.py` | Maps each approved PSI table to the unified schema (rules in DATA_DICTIONARY section 3). |
| `transcribed.py` | Loads the hand-transcribed CSVs with the same schema and keeps the original value next to the harmonized one. |
| `outcome.py` | Maps free-text outcomes to six classes: no_ignition, self_extinguished, burned_to_completion, **externally_terminated** (censored: the test was stopped while the flame burned, never treated as extinction), other, unknown. Source labels (for example `end=FT; hot_ignition=yes`) are kept so the page can show what the lab wrote. |
| `materials.py` | Rule-based normalization of BASS-II material text. Only what the text states is extracted; unclear dimensions stay empty and are flagged. |
| `schema.py`, `checks.py` | Allowed values, numeric parsing, **unit-sanity ranges per field and per family** (catches mmHg versus kPa or percent versus fraction slips), unique test ids, no row without `source_ref`, row counts per family and outcome class against `expected_counts.json`. **Any failure stops the build and writes nothing.** |
| `profiles.py` | Mission atmosphere envelopes from the official text; kPa computed from psi (1 psi = 6.894757 kPa), never typed. |
| `ranking.py`, `interpret.py` | The deterministic ranking and effect summaries ([section 7](#7-technical-core-part-3-ranking-interpretation-and-the-data-gap-ranking)). |
| `spot_check.py` | Random 20-row spot check that **re-reads the sources without the mapping code** (`python -m pipeline.spot_check`; add `--stratified` or `--n 99999`). |

**Conflicts and quality flags.** Where a PSI table and a report disagree (for example Saffire values), both values are kept (`alt_value_report`) and the disagreement is listed in [`docs/CONFLICTS.md`](docs/CONFLICTS.md). Flags such as `diameter_label_disagree`, `pressure_ambiguous` and `gravity_nominal_microgravity` travel with the row and surface as caveats in the Interpretation view.

**AI-proposed values are quarantined.** 129 BASS-II outcome classes were proposed by an AI assistant (`data/llm/`); a rule in the checks forbids using them until a person approves them in `data/review/outcome_review.csv`.

---

## 6. Technical core, part 2: the evidence ledger

**Goal.** Let a user ask a question and get an answer they can check: an atomic claim, the **verbatim quoted passage**, the PDF page and how it was verified.

### 6.1 Pipeline

```mermaid
flowchart LR
  S[sources.csv<br/>NTRS reports + SHA-256] --> PG[pages.jsonl<br/>PDF text per page]
  PG --> EX[Extract<br/>Gemini]
  EX --> G1{Code gate 1<br/>exact quote span}
  G1 --> G2{Code gate 2<br/>numbers}
  G2 --> G3{Code gate 3<br/>conditions + gravity}
  G3 --> SR[Cross-check<br/>second model family, Groq]
  SR --> ST{status}
  ST -->|all passed| VA[verified_auto]
  ST -->|held back| NR[needs_review]
  NR --> RV[reviewer: AI-assisted<br/>page check, then human]
  RV --> AP[approved]
  RV --> RJ[rejected]
  VA --> PUB[public claims]
  AP --> PUB
```

1. **Text layer.** `python -m ledger pages` extracts the text of each PDF page (pypdf); page numbers are PDF page indices starting at 1.
2. **Extract (Gemini, free tier).** `prompts/extract_v1.md` asks for atomic claims with a verbatim span (at most 600 characters), numbers only from the span, fixed unit conversions and a gravity class by words. Because the free tier allows few requests per day per model, extraction moves down a model chain (`ledger/config.py`) and every claim records the exact model version that produced it. Runs resume from `data/ledger/cache/` after any interruption and stop cleanly at a daily limit. The cache key contains the prompt version, so a new prompt never reuses old answers.
3. **Code gates (deterministic, `ledger/verify.py`).**
   - *Exact quote span:* the normalized span must be a substring of the normalized page text. A wrong page named by the model is corrected from the text and flagged. A near match (similarity of at least 0.95) is held back as `fuzzy_span`; no match at all is rejected.
   - *Numbers:* every number in the claim statement must appear in the quote with the same value.
   - *Conditions and gravity:* each numeric condition must follow from a printed number by a fixed conversion; a lunar, Mars, microgravity or 1 g class needs a matching word in the span or on the page.
4. **Cross-check (a different model family, `prompts/verify_v1.md`).** A second model (the open-weight gpt-oss-120b served by Groq) judges whether the quote supports the claim: supported, partial or unsupported. Unsupported claims are rejected and partial ones are held back.
5. **Status.** `verified_auto` (everything passed), `needs_review`, `approved`, `rejected`. Rejected claims are kept in `rejected.jsonl` for audit and never shown.
6. **Review (`data/review/claim_review.csv`).** Held-back claims were decided by the reviewer, Zainab Raza (ZRM). An AI assistant produced triage and page-check suggestions; the reviewer opened each page and decided. A reworded statement is **re-checked by code** against its span, and a span can only be **extended, never replaced** (`apply_review` in `ledger/build.py`). Two claims were approved by manual override of a failed number check and are marked as such.
7. **Grouping.** Public claims with the same gravity class, effect direction and variables are clustered (overlap of content words) so near-duplicates show once.
8. **Display rule.** The UI shows the claim statement and its citation; the verbatim quote is shown only for documents whose NTRS rights determination permits it, otherwise "Quotation not shown (the source is not a US Government work)".

### 6.2 What was checked, in numbers

These counts are computed from the ledger files by `ledger/review_wording.py`, the single source used by the site, the ledger report and the tests, so they cannot drift:

- **255 public claims, each opened and checked against its source page by the reviewer (ZRM).**
- **181** passed the automatic checks first (code checks for the exact text span, numbers and conditions, plus a second AI model).
- **74** were held back by those checks and approved after an AI-assisted page check, which the reviewer then checked herself; 25 of them carry a corrected statement or gravity class.
- **2** were approved by manual override of the number check (C-f4d3c81aef, C-cbca12ebcd).
- **7** were rejected and **3** are held back and not published. None of these 10 is shown as checked or used to answer.
- **Spot check of transcribed table values:** all 10 sampled values were AI-checked against the PDFs and 2 were also checked by ZRM ([`docs/HUMAN_SPOT_CHECK.md`](docs/HUMAN_SPOT_CHECK.md)).

`tests/test_review_wording.py` fails the build if any page or document states a different number of public claims, uses an overstated review phrase, or describes a rejected or held-back claim as checked.

### 6.3 What the checks do and do not prove

They prove the quoted text exists on that page, that the claim's numbers are in it, and that a second model and a person judged it supported. They do **not** prove that the paper is right. The generated report is [`docs/LEDGER_REPORT.md`](docs/LEDGER_REPORT.md); the schema is [`docs/LEDGER_SCHEMA.md`](docs/LEDGER_SCHEMA.md); a 30-claim random audit is in [`docs/CLAIM_AUDIT.md`](docs/CLAIM_AUDIT.md).

---

## 7. Technical core, part 3: ranking, interpretation and the data-gap ranking

Everything here is deterministic. The same inputs always give the same numbers, and the weights are shown on the page.

### 7.1 Investigation ranking (`pipeline/ranking.py`, [`docs/RANKING.md`](docs/RANKING.md))

`score = 100 x (0.35 atmosphere + 0.20 safety_area + 0.20 fuel + 0.15 data + 0.10 gravity)`, each component between 0 and 1:

| Component | Weight | Rule |
|---|---|---|
| atmosphere | 0.35 | For investigations with rows that have oxygen and pressure: 0.6 x share of rows inside the profile envelope + 0.4 x nearness to it. |
| safety_area | 0.20 | 1 if tagged prevention, detection or suppression (official text or record metadata), else 0. |
| fuel | 0.20 | Solid materials 1.0; smoke or aerosol 0.6; droplets or gas flames 0.4; unknown 0.2. |
| data | 0.15 | min(1, test rows / 100). |
| gravity | 0.10 | Flight microgravity 1.0; ground analysis or modelling 0.4. No investigation has partial-gravity data, so none earns lunar or Mars credit. |

Profiles: lunar base and pressurized rover (oxygen 30% or more, 10.2 psi / 70.33 kPa or less, official), spacesuit (100% O2, 4.3 psi, official) and ISS-like cabin (19 to 25% O2 within 10% of 14.7 psi; **team-defined**, because the official text gives no cabin numbers). The page states that the atmosphere component covers only the 6 investigations with per-test rows and that the weights are judgement.

### 7.2 Interpretation and evidence strength (`pipeline/interpret.py`)

Three summaries (FLEX oxygen and diluent versus extinction, CFI-G oxygen versus how tests ended, Saffire-II 0 g versus 1 g) are templates filled with counts per condition bin. The **evidence-strength label** is a fixed rule: *moderate* (at least 100 tests, one experiment family), *limited* (30 to 99), *very limited* (under 30) and *strong* (at least 100 tests agreeing across two or more independent families; no current analysis qualifies). A recorded source conflict lowers the label by one step.

### 7.3 The data-gap ranking ("Where should NASA test next?")

It ranks **untested conditions**, not safety.

1. **Grid:** the 0 g coverage grid of the map, cells 20 kPa wide and 5 percentage points of oxygen tall (17 x 20 = 340 cells; 306 are untested). A cell is untested when no test and no oxygen-limit point at 0 g falls in it.
2. **Envelope and design point:** NASA's planned lunar-base atmosphere (O2 >= 30%, pressure <= 70.33 kPa); the design point is its corner, 30% O2 at 10.2 psi.
3. **Bands:** untested cells that touch within one pressure column merge into a band at most 3 cells (15 oxygen points) tall, so that five non-touching bands exist inside the envelope.
4. **Sort key:** distance from the design point in cells, then fewest tests in the surrounding cells, then lower oxygen first (only to keep the order deterministic).
5. **Selection:** best first, skipping any band that touches one already chosen; the first five are shown with their oxygen and pressure ranges, tests nearby, the closest investigation and a button that highlights the whole band on the map.

Limits: it looks at oxygen and pressure only (not gravity, fuel, flow or sample size), uses 0 g coverage only, and says nothing about how dangerous a condition is.

---

## 8. Technical core, part 4: the Ask engine

`scripts/ask_parser.js` is a deterministic parser and filter, inlined into the page and unit-tested through Node. **No model, no network.**

- **Environment words.** Oxygen (`30% oxygen`, `O2`), pressure with units (`10.2 psi`, `kPa`, `atm`, `mmHg`, `torr`, `bar`, all converted to kPa), gravity (microgravity, lunar, Mars, 1 g) and diluent words (CO2, helium and others).
- **Operators.** "above", "over", "at least", "no more than", "up to", "30% or more", `>=` and similar map to a minimum or maximum, inclusive or exclusive; an unqualified value matches with a tolerance (oxygen +-0.5 points, pressure +-3%).
- **Relevance gate.** If no real key term, condition or topic is found, the answer is "Not in the evidence" with suggestions. This is the refusal path.
- **Outcomes with their labels.** Results are grouped by outcome class; lab labels are kept ("source: end=FT; hot_ignition=yes"), and censored outcomes are explained as "the test was stopped while the flame was still burning, not 'did not burn'".
- **Claim search.** Public ledger claims are scored by term weighting over the statement, variables, gravity class and material; only claims that share the question's key terms are shown, best first, each with its review path and citation.
- **Provenance everywhere.** Every row links to its PSI table row or NTRS report page.

Tests: `tests/test_ask_parser.py` (20 tests, run through Node) covers units, operators, tolerances, refusals and diluent handling.

---

## 9. Technical core, part 5: the static site build

- `scripts/site_template.html` holds the HTML, CSS and all page JavaScript. `scripts/build_site.py` reads the processed data, the ledger and the official text, then writes **`site/index.html`** (about 1.2 MB) with the data blob, the Ask parser, the 3D plot code and the base64-embedded fonts inlined. It also writes `site/data/` (`tests.csv`, `ledger_claims.json`, the data dictionary).
- **No third-party JavaScript, CSS framework, icon set or image.** Fonts: Sora, IBM Plex Sans and IBM Plex Mono (SIL OFL), embedded.
- **No network calls at runtime.** The page works offline once loaded (a test checks that the page has no keys and no network references).
- **Single source of truth for numbers and review wording.** Counts on the page come from the build data; the review sentences come from `ledger/review_wording.py`.
- **Accessibility and motion.** Dark and light themes, keyboard navigation, visible focus, text contrast of at least 4.5:1, controls of at least 44 px, charts with shape as well as colour, tables behind "See the numbers", and `prefers-reduced-motion` plus a motion toggle that switches off count-ups, card flips and reveals.
- **Print.** The Mission brief has a print stylesheet that fits one A4 page.
- **Deploy.** The `site/` folder is published to the `gh-pages` branch.

---

## 10. Setup, dependencies and how to run everything

### 10.1 Prerequisites

| Need | Version | Used for |
|---|---|---|
| Python | 3 (developed and tested on 3.12) | pipeline, ledger, site build, tests |
| Node.js | a current release (developed on 24) | the Ask-parser unit tests only |
| Git | any recent | clone, deploy |
| `pyarrow` | 14 or newer | parquet output (`requirements.txt`) |
| `pypdf`, `pymupdf` | latest | development only: PDF text and table extraction (`requirements-dev.txt`; PyMuPDF is AGPL-3.0 or commercial and is **not** a runtime dependency) |
| Google Chrome | any recent | optional: browser checks and screenshots |
| API keys | Gemini and Groq | **only** to re-extract claims; never needed to build or run the site |

```bash
pip install -r requirements.txt          # runtime
pip install -r requirements-dev.txt      # optional development tools
```

On Windows run Python with UTF-8 (`python -X utf8 ...`).

### 10.2 Rebuild the site from the committed data

```bash
python -m pipeline                          # data/processed/tests.csv, tests.parquet, build_report.json (fails loudly on a data-check failure)
python -m pipeline.profiles                 # mission atmosphere profiles
python -m pipeline.ranking                  # investigation ranking
python -m pipeline.interpret                # effect summaries
python -X utf8 -m ledger all --offline --skip-pilot   # rebuild the ledger from the cache (no API calls)
python -X utf8 -m ledger report             # regenerate docs/LEDGER_REPORT.md
python scripts/build_site.py                # site/index.html and site/data/
```

Run it: open `site/index.html`, or `python -m http.server -d site 8000` and visit http://localhost:8000.

### 10.3 Re-run the claim extraction (needs API keys)

Put `GEMINI_API_KEY` and `GROQ_API_KEY` in the environment or in the git-ignored `.env.local`; **never in a tracked file**.

```bash
python -m ledger smoke                                    # check both providers answer and pick models
python scripts/fetch_ledger_sources.py                    # fetch the source PDFs listed in data/ledger/sources.csv
python -m ledger pages                                    # PDF text layer
python -m ledger extract --skip-pilot --docs <ids> --stop-at HH:MM
python -m ledger report                                   # regenerate the report
```

Commands: `smoke | pages | pilot | extract | rate | report | all`. Flags: `--offline` (cache only), `--skip-pilot`, `--docs`, `--no-verify`, `--stop-at HH:MM`. Rate limits are per provider (`LEDGER_<PROVIDER>_RPM / _RPD / _TPM / _TPD`); a daily-quota reply stops the run cleanly and the next run resumes from `data/ledger/cache/`.

### 10.4 Apply reviewer decisions

Edit `data/review/claim_review.csv` (decision, corrected statement, extended span, note), then rebuild the ledger offline as above. Decisions are re-applied on every build; a reworded statement is re-checked by code and a failing wording stays held back.

### 10.5 Deploy

```bash
python scripts/build_site.py
git add -A && git commit -m "..." && git push origin main
git branch -D gh-pages ; git subtree split --prefix=site -b gh-pages
git push -f origin gh-pages          # GitHub Pages serves it a minute or two later
```

### 10.6 Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `DATA CHECKS FAILED` | A data check caught a bad row, a unit slip or a changed count. Read the message; if the change is intended, update `pipeline/expected_counts.json` deliberately with `python -m pipeline --write-expected`. |
| A ledger run stops at a "daily limit" | Free-tier quota. Rerun later; it resumes from the cache. |
| `UnicodeEncodeError` on Windows | Use `python -X utf8`. |
| Ask-parser tests fail or are skipped | Node.js is not installed. |
| The site looks stale after a deploy | GitHub Pages caches for a minute or two; hard-refresh. |

---

## 11. Testing and quality gates

```bash
python -m unittest discover -s tests -q      # 96 tests
python -m pipeline.spot_check                # 20 random rows re-read from the sources
```

| File | Tests | Covers |
|---|---|---|
| `tests/test_pipeline.py` | 28 | schema and unit conversions, outcome rules (censored is never extinction), BASS-II proposals not used until approved, original values kept next to converted ones, determinism, data checks that fail loudly |
| `tests/test_ledger.py` | 27 | span, number and condition checks, wrong-page correction, statuses, rejected claims never public, review rules (a span may be extended but never replaced), cache reuse, rate-limit back-off, daily limits and resume, API keys never written |
| `tests/test_ask_parser.py` | 20 | units, operators, tolerances, refusals, diluents (through Node) |
| `tests/test_site.py` | 11 | kPa computed from the official psi, every row inside the envelope meets it, all 24 investigations with sources, the partial-gravity gap is labelled, ranking weights sum to one and the ranking is deterministic, the evidence-strength rule, interpretation counts match the table, the page script parses, no keys and no network calls, unreviewed claims are labelled |
| `tests/test_review_wording.py` | 7 | one number everywhere, banned phrases, nothing called checked about rejected or held-back claims |
| `tests/test_home_blocks.py` | 3 | oxygen-dial rows (numeric limit and stated pressure only) and the spacecraft-fire claims (public only) |

Browser checks used for each release: no JavaScript errors and no sideways scroll at 390 px and 1366 px, the 25 s tour still takes 25 s, and the Mission brief prints on one A4 page.

---

## 12. Repository layout

```text
.
├── site/                       built site (index.html, data/)           <- what GitHub Pages serves
├── scripts/                    site_template.html, build_site.py, ask_parser.js, hero_cube.js,
│                               fonts/, fetch_* and review helpers
├── pipeline/                   harmonization, data checks, profiles, ranking, interpretation, spot check
├── ledger/                     extraction, verification, second rater, review, display, report, review_wording
├── prompts/                    extract_v1, verify_v1, bass2_rater_v1 (+ CHANGELOG)
├── data/
│   ├── raw/                    PSI tables, NTRS source info (large PDFs are git-ignored; SHA-256 recorded)
│   ├── transcribed/            hand-transcribed NTRS tables with citations
│   ├── processed/              tests.csv, tests.parquet, ranking, interpretations, profiles, build report
│   ├── ledger/                 claims, rejected claims, sources, cache, usage and run logs
│   ├── review/                 reviewer decisions (claims, gravity labels, outcomes)
│   └── llm/                    AI-proposed outcome classes (not used until approved)
├── tests/                      96 unit tests
├── docs/                       challenge text, rules, requirements, alignment, data notes, ledger report,
│                               ranking rules, SI log, third-party register, screenshots/
├── PLAN.md                     original scope, modules, acceptance criteria
├── requirements.txt, requirements-dev.txt
└── LICENSE                     Apache-2.0
```

---

## 13. SI use, licences and provenance

**SI use and limits.** An AI coding assistant (Claude, via Claude Code) helped write the pipeline, the checks, the tests and this page. Claim extraction used a language model (Google Gemini, free tier); a second model from a different family (OpenAI's open-weight gpt-oss-120b, served by Groq) cross-checked each claim; code checks the quoted text, numbers and conditions against the report. AI-proposed BASS-II outcome classes are not used until a person approves them. A person, Zainab Raza (ZRM), opened and checked each public claim against its source page. **The page itself runs no model and makes no network calls.** Every tool, what it did and what a person reviewed is logged in [`docs/SI_USAGE.md`](docs/SI_USAGE.md).

**Licences.** Code: Apache License 2.0. PSI records: CC0 as stated per record. NTRS reports keep their own NASA rights determinations and are cited and linked, not redistributed. Fonts: SIL Open Font License 1.1. The complete register, with licence and source URL for every dataset, library and model, is [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md). No NASA logos or imagery are used anywhere.

**Secrets.** API keys are read from the environment or the git-ignored `.env.local` only; the repository history contains no key (checked across all branches).

**Provenance.** This repository was created on 2026-11-14 as a single import of the project files. The data pipeline, document checks and evidence-ledger code were developed from 2026-10-19 to 2026-11-14 in an earlier local repository (about 25 commits, kept as an archive by the team); the explorer page, the official-alignment document and the submission drafts were produced on 2026-11-14 and after. Dates inside `docs/` record when each step happened. The import does not claim the work was done on the day of import.

---

## 14. Honest limits and what is not done

- **NASA's archive has no partial-gravity combustion data yet.** Ember shows the gap rather than filling it. The few lunar and Mars values come from published reports and are labelled "outside PSI".
- The oxygen dial uses a 1 g test mostly at 14.7 psia: it is a warning, not a design value.
- Transcribed report values were spot-checked (10 values), not independently verified in full. 126 of 769 tests lack oxygen or pressure and cannot be placed on the map.
- The ranking weights are judgement and the ISS-like cabin envelope is a team assumption; both are shown on the page.
- The ledger covers 11 priority NTRS reports (extraction used free-tier APIs with daily limits), not all of NTRS.
- **Not met or only partly met against the challenge:** next-generation controls and equipment (objective 3), the history-of-fires background, structured fuels and sensors for the 18 investigations without per-test rows, and no predictive model (the data is exported for one).
- No user testing was done.

---

## 15. Documentation index

| Document | Contents |
|---|---|
| [`PLAN.md`](PLAN.md) | Scope, modules, acceptance criteria, risks |
| [`docs/CHALLENGE.md`](docs/CHALLENGE.md) | The official challenge text |
| [`docs/OFFICIAL_ALIGNMENT.md`](docs/OFFICIAL_ALIGNMENT.md) | Line-by-line audit of the official text against the product |
| [`docs/RULES.md`](docs/RULES.md), [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md), [`docs/STATUS.md`](docs/STATUS.md) | Event rules, requirement tracking, status |
| [`docs/SUBMISSION_DRAFT.md`](docs/SUBMISSION_DRAFT.md) | The submission text and form fields |
| [`docs/DATA_SURVEY.md`](docs/DATA_SURVEY.md), [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | Sources surveyed and the test-table columns |
| [`docs/OUTCOME_MAPPING.md`](docs/OUTCOME_MAPPING.md), [`docs/GRAVITY_COVERAGE.md`](docs/GRAVITY_COVERAGE.md), [`docs/CONFLICTS.md`](docs/CONFLICTS.md) | Outcome classes, gravity coverage, source conflicts |
| [`docs/LEDGER_SCHEMA.md`](docs/LEDGER_SCHEMA.md), [`docs/LEDGER_REPORT.md`](docs/LEDGER_REPORT.md), [`docs/CLAIM_AUDIT.md`](docs/CLAIM_AUDIT.md) | Ledger design, generated report, random claim audit |
| [`docs/REVIEW_QUEUE.md`](docs/REVIEW_QUEUE.md), [`docs/SPOT_CHECK.md`](docs/SPOT_CHECK.md), [`docs/HUMAN_SPOT_CHECK.md`](docs/HUMAN_SPOT_CHECK.md) | Review queue and spot checks |
| [`docs/RANKING.md`](docs/RANKING.md) | Investigation score, evidence strength, data-gap ranking |
| [`docs/SI_USAGE.md`](docs/SI_USAGE.md), [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md) | AI tool log, third-party register |
