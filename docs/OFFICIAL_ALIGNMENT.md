# Alignment with the official challenge text

Updated 2026-11-14 (evening build) against [CHALLENGE.md](CHALLENGE.md) (official text as supplied by the team). "Product" means `site/index.html` (built by `scripts/build_site.py`) plus the data pipeline in this repository. Verdicts: **met**, **partly met**, **not met**. Nothing is claimed that the product does not do. The site is deployed on GitHub Pages: https://zainabraza06.github.io/Nasa_Challange/ (see STATUS.md).

## Objectives

| Official statement | Verdict | Evidence |
|---|---|---|
| Build an SI-powered, web-based dashboard | **partly met** | Web-based: a static page on GitHub Pages. SI-powered: the page itself runs no model and makes no network calls. SI was used to build it (an AI coding assistant) and to extract the claims it retrieves (Gemini extraction, Groq verifier, with code checks); see SI_USAGE.md. Those claims are labelled verified or unreviewed |
| ...that **summarizes** combustion investigations | **partly met** | Investigations tab: objective, approach, conditions varied and measurements quoted from each PSI record, plus ranges computed from the unified table where it has rows. Interpretation tab: computed effect summaries. Mission brief: a one-page cited summary. None of these are language-model written summaries |
| ...that **ranks** investigations | **met (rule-based)** | Ranking tab: a documented deterministic formula (docs/RANKING.md) over all 24 investigations for four profiles, with the score breakdown shown. It ranks relevance to an atmosphere and safety need, not scientific quality |
| ...that **interprets** findings | **partly met** | Interpretation tab: three computed analyses (FLEX oxygen and diluent versus extinction, CFI-G oxygen versus how tests ended, Saffire-II 0 g versus 1 g) with counts, caveats, recorded conflicts and an evidence-strength label. No general interpretation engine, and the effects shown are associations in uncontrolled test series, not causal estimates |
| 1. Identify investigations most relevant to the needs of spacecraft, stations, lunar and Martian bases, pressurized rovers | **partly met** | Atmosphere map (home), Mission atmospheres and Ranking tabs: official envelopes in psi and computed kPa, every test placed by oxygen and pressure, 48 CFI-G tests inside the lunar and rover envelope, none at the suit condition, untested areas hatched, and a relevance ranking per profile. No Martian-surface profile (the official text gives none); no relevance judgement beyond the documented formula |
| 2. Extract data that supports predictive modeling of flammability | **partly met** | `data/processed/tests.csv` and `tests.parquet` (885 rows, original values, source reference and quality flags, DATA_DICTIONARY.md) are in the repository, and the map shows the data's coverage and gaps. The site does not offer a download and no predictive model has been trained |
| 3. Highlight research that informs next-generation fire safety controls and equipment | **not met** | Safety-area tags (prevention, detection, suppression) and the SAME/FLEX investigations are visible, but nothing specifically highlights research for next-generation controls or equipment |
| Applications of PSI data to fire safety on Earth (fine-water-mist extinguishers, terrestrial smoke detection, firefighter gear) | **partly met** | Earth applications tab names the three areas from the official text and links the three spinoff resources. It shows no analysis; which spinoff covers which area is not stated officially, so none is mapped |
| Scope note: rocket and propellant fire safety is beyond PSI | **met** | About tab states it |

## Potential Considerations

| Official statement | Verdict | Evidence |
|---|---|---|
| Target audience: professors, students, researchers, engineers | **met (design)** | Plain tables with sources; no hidden jargon beyond the PSI text. No user testing was done |
| Per investigation: experimental objectives | **met** | All 24 PSI combustion investigations, verbatim from the PSI record, each with its PSI link |
| ...fuels, including shape and size of samples or burners | **partly met** | For the 6 investigations with rows in the unified table (PSI-25, 69, 98, 99, 100, 159): fuels, shape and size ranges from the table. For the other 18: "not documented in the catalog", with the record's approach text (which may describe burners) shown in full |
| ...other test conditions (oxygen, airflow) | **partly met** | Oxygen, pressure and flow ranges for the same 6 investigations. Others only through the record text |
| ...variables: how tests differed and what stayed the same | **partly met** | The record's "Conditions varied" text and, in Compare, the table ranges. No automatic same/different analysis of the variables themselves |
| ...sensors or types of measurements | **partly met** | The record's "Outcomes measured" and approach text, shown verbatim; not extracted into a structured field |
| Similarities and differences between investigations | **met (short fields)** | Compare tab: two or three investigations side by side, short fields highlighted same / differs / not documented, long text shown in full |
| Other PSI investigations: DAFT/DAFT-2, BRE | **met** | PSI-47 (tagged detection) and PSI-20 (tagged prevention) are in the list; all 24 combustion investigations are listed |
| Hardware groups (ACME in CIR, MDCA in CIR, MSG flow duct) | **met** | Hardware group shown and filterable; assignment follows the official text, other investigations use the catalog platform column and say so |
| Prevention / detection / suppression (Background) | **met** | Tags with the reason on hover; 13 of 24 investigations tagged, 11 untagged because neither the official text nor the metadata supports a tag |
| Spacesuit 100% O2 at 4.3 psi; Moon base and rover 30% O2 or more at 10.2 psi or less | **met** | Mission atmospheres tab; kPa computed in `pipeline/profiles.py`; no test row is at the suit condition (stated as a gap) |
| Highest-oxygen microgravity tests were ACME CFI-G (up to 85%) | **met** | Computed from the table: maximum oxygen fraction 0.85 in PSI-159 rows |
| No partial-gravity data in PSI; LUCI and FM2 expected; E-FIELD mimics partial gravity; 0 g and 1 g could bound | **met** | Partial-gravity tab: 0 g / 1 g side by side for the 9 Saffire-II pairs; lunar and Martian gap with 8 rows transcribed from NTRS 20130010991 (limit rows) and NTRS 20250010653 (LUCI), labelled "outside PSI, transcribed from NTRS"; the note on LUCI, FM2 and E-FIELD |

## Background and resources

| Official statement | Verdict | Evidence |
|---|---|---|
| Fire hazards (Artemis II, Apollo 1 and 13, Mir) and why microgravity flames differ | **not met** | Context only; the product does not present it. The three history resources are linked in About |
| Increased oxygen, reduced pressure expected in the Moon Base and rovers | **met** | Mission atmospheres tab |
| The ten resources on the Resources tab | **met (linked)** | All ten are listed with links in About. The ScienceCasts video, Apollo and Mir pages and the Researcher's Guide are linked only; none was read for the data |
| Space Agency partner resources | **n/a** | None listed officially |

## Researcher's Guide (2015)
Not in `data/ledger/sources.csv` or `data/catalog.csv`. It is cited as a linked resource only; it was not extracted.
