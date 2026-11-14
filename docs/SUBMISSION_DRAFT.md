# Submission draft (ready to paste)

Prepared 2026-11-14. Text in **[BRACKETS]** is a placeholder that a team member must fill in; nothing in brackets has been invented. The wording of the summary and description is shared by both submissions so they agree. Check every claim against `docs/OFFICIAL_ALIGNMENT.md` and `docs/STATUS.md` before pasting. At the time of writing the explorer is **not deployed**: fill in the live link only after it is.

---

## Section 1. Official Space Apps website submission

**Project name:** Ember

**Challenge:** Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data

**High-level summary** (identical text is used in Section 2):

> Ember is a web-based explorer for NASA's microgravity combustion research. It collects the 24 combustion investigations in NASA's Physical Sciences Informatics (PSI) repository on one page, lets users filter them by fire-safety area (prevention, detection, suppression) and by hardware group, and compares two or three side by side, showing what is the same and what differs. A reproducible pipeline harmonises 769 individual tests into one table with original values, sources and quality flags. A mission page places those tests against the official lunar base, rover and spacesuit atmospheres, and a partial-gravity page shows the gap between 0 g and 1 g evidence and the few lunar and Martian rows that exist outside PSI. Every field links to its source, and anything the catalog does not document is shown as not documented. SI tools helped build the pipeline; a claim-extraction ledger is built but not yet run.

**Detailed description**

Ember answers the challenge's problem that NASA's combustion results are "hard to find, harder to compare, harder yet to interpret". It is aimed at students, researchers and engineers who need to see what was tested, under which conditions, and where the evidence stops.

*What it does today*
- **Investigations and comparison.** All 24 PSI combustion investigations (flight experiments and ground analyses) with objectives, approach, conditions varied and measurements quoted from the PSI record, each linked to its source. Fuels, shape and size, oxygen, pressure and flow ranges are added from the unified test table for the six investigations that have rows in it (BASS-II, Saffire-I, -II, -III, FLEX and ACME CFI-G); for the others the page says "not documented in the catalog". Two or three investigations can be compared side by side with similarities and differences highlighted.
- **Fire-safety areas and hardware groups.** Each investigation is tagged prevention, detection and/or suppression, using the official Background text where it names the investigation and the investigation's own metadata otherwise; the reason is shown. Hardware groups (ACME and the MDCA in the Combustion Integrated Rack; the Microgravity Science Glovebox flow duct) follow the official text. Eleven investigations are left untagged because nothing supports a tag.
- **Mission atmospheres.** The official numbers (lunar base and pressurized rover: oxygen 30% or more at 10.2 psi or less; spacesuit: 100% oxygen at 4.3 psi) are converted to kPa in the pipeline and compared with the test table: 48 tests (all ACME CFI-G, microgravity) fall inside the lunar base and rover envelope and none at the spacesuit condition, which is shown as an evidence gap.
- **Partial-gravity bounds.** There is no partial-gravity data in PSI. The page shows the nine Saffire-II samples at 0 g and at 1 g side by side, clearly labels the lunar and Martian gap, and lists the eight lunar and Martian rows that exist only in NASA technical reports (marked "outside PSI, transcribed from NTRS"). It notes that LUCI and FM2 are expected to add data and that ACME E-FIELD mimicked partial gravity with an electric field.
- **Earth applications and About.** Links to the three NASA spinoff stories and the ten official resources, the scope note (rocket and propellant fire safety is outside the PSI data), data origins and licenses.

*How the data was prepared.* A Python pipeline reads the PSI tables and hand-transcribed report tables into one table of 885 records (769 individual tests plus flammability-limit and series entries) with original values kept next to normalised ones, a source reference on every row, and quality flags. Automated checks fail the build on out-of-range values, duplicate ids or changed counts. A seeded 20-row spot check against the source files found no mismatches, and all rows pass an independent checker; a 10-value human check of transcribed numbers is prepared for the team. Corrections made where a report clearly contradicts a PSI table are flagged (`corrected_from_report`) and one genuine conflict is listed (`docs/CONFLICTS.md`).

*What it does not do yet.* It does not rank investigations, answer questions, interpret results or generate briefs, and it does not show extracted claims. The code for an evidence ledger (language-model extraction of claims from NASA reports, each checked by code against the PDF text) is written and tested, but it has not been run on the reports.

**NASA data used**
- PSI Data Repository, Combustion Science (https://psi.nasa.gov/physci/repo/search?q=combustion), investigation records for all 24 combustion investigations: PSI-10, 20, 21, 22, 23, 25, 26, 39, 47, 60, 62, 68, 69, 98, 99, 100, 101, 102, 106, 107, 115, 117, 142, 159. Experiment tables from PSI-25 (BASS-II), 69 (FLEX), 98, 99, 100 (Saffire-I, -II, -III) and 159 (ACME CFI-G) were harmonised into the test table (PSI records are marked CC0-1.0 except one whose license field is empty).
- NASA Technical Reports Server reports used for transcribed values, cross-checks or limits: 20150023456 (FLEX detailed results), 20210011385 (BASS-II summary report), 20170008805 (Saffire results), 20010059376 (partial-gravity flame spread), 20130010991 (flammability in microgravity and Martian gravity), 20250010653 (LUCI rocket results), 20110008636 and 20170004702 (1 g flammability limits).
- The ten resources on the challenge Resources tab are linked in the About page: PSI repository, NASA Combustion Science, the ScienceCasts video, A Researcher's Guide to ISS Combustion Science, Apollo 1, Apollo 13, the Mir fire article, and the three spinoff stories. The Guide, video and history pages were linked, not read for data.
- Exploration-atmosphere reports (NTRS 20260002050, 20130013505, 20150021491 and NASA/TP-2010-216134) are cited as supporting references on the mission page; they were not used for numbers.

**Other data**
- One university thesis (M. Kim, 2022, University of Maryland) was read to confirm the meaning of two ACME CFI-G outcome labels; it is cited, not redistributed. No other third-party data.

**Use of artificial intelligence (SI)**
- *SI-powered development.* An AI coding assistant (Claude, via Claude Code) wrote the pipeline, checks, tests, the static page generator and the documentation under the team's direction, and read report pages to transcribe tables. All of it is in the repository with its history.
- *Outcome labels for BASS-II.* The assistant read each of the 126 BASS-II test observations and proposed an outcome class (self-extinguished, burned to completion and so on) with a confidence. These were **not produced through an API call**; they are the assistant's own judgements written into a script. **None has been approved by a human**, so none is used: every BASS-II outcome in the data is "unknown" until a person approves it. A second, independent model rating was planned but has not been run.
- *Evidence ledger.* Code for extracting claims with Google Gemini and checking each claim with a different model (Llama 3.3 70B on Groq) is written and tested with a mocked API. Only a one-call connection test of Gemini was made; the extraction and verification have not been run, no claims were produced, and nothing from it is shown.
- *At runtime.* The explorer calls no model: its text is quoted from NASA records or computed by code. It contains no SI-generated summaries.
- *Human review.* The team reviews data checks, the review queue and the human spot-check sheet **[TEAM: state what was actually reviewed, by whom and when, before submitting]**.

**Limitations**
- Not deployed at the time of writing **[TEAM: add the live URL once it exists]**. No ranking, question answering, interpretation or brief generation. No extracted claims.
- Only 6 of 24 investigations have per-test rows in the unified table; for the rest the page shows PSI record text only. Several tests lack oxygen or pressure values (126 of 769 cannot be placed in the mission envelopes).
- Outcome classes: 369 self-extinguished, 38 burned to completion, 91 externally terminated (a censored outcome, not an extinction), and 266 unknown, which includes all of BASS-II. For FLEX, the report's "Test end" label is used, and 58 of 280 tests have a label that disagrees with the extinction diameter (listed for review).
- Tags and hardware groups are assigned from the official text and record metadata; 11 investigations are untagged.
- Partial-gravity evidence consists of eight rows from two reports and is not PSI data. The spacesuit condition has no test.
- The report-sourced values were transcribed by hand and have been spot-checked, not independently verified in full. NTRS reports carry NASA rights determinations that are not open licenses, so they are cited, not redistributed.

**Demonstration video:** [LINK TO VIDEO]
**Project link (deployed explorer):** [LIVE URL, not yet available]
**Source code:** [REPOSITORY URL: the new repository link the team will supply]

---

## Section 2. Islamabad local Google Form (deadline: Sunday 15 November 2026, 3:30 PM PKT)

Submit this form **and** the official website submission. The description below is the same text as the high-level summary above (146 words).

| Field | Paste |
|---|---|
| Team name | **[TEAM NAME]** |
| Team members (all) | **[MEMBER 1 FULL NAME]**; **[MEMBER 2 FULL NAME]**; **[MEMBER 3 FULL NAME]**; **[MEMBER 4 FULL NAME]**; **[MEMBER 5 FULL NAME]**; **[MEMBER 6 FULL NAME]** (delete unused lines; at most six) |
| Team lead name | **[TEAM LEAD FULL NAME]** |
| Team lead email | **[TEAM LEAD EMAIL]** |
| Team lead phone / WhatsApp | **[TEAM LEAD PHONE]** |
| Selected challenge | Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data |
| Project title | Ember |
| Project description (about 150 words) | Ember is a web-based explorer for NASA's microgravity combustion research. It collects the 24 combustion investigations in NASA's Physical Sciences Informatics (PSI) repository on one page, lets users filter them by fire-safety area (prevention, detection, suppression) and by hardware group, and compares two or three side by side, showing what is the same and what differs. A reproducible pipeline harmonises 769 individual tests into one table with original values, sources and quality flags. A mission page places those tests against the official lunar base, rover and spacesuit atmospheres, and a partial-gravity page shows the gap between 0 g and 1 g evidence and the few lunar and Martian rows that exist outside PSI. Every field links to its source, and anything the catalog does not document is shown as not documented. SI tools helped build the pipeline; a claim-extraction ledger is built but not yet run. |
| Demonstration video link | **[LINK TO VIDEO]** |

Before pasting: confirm the form's own field names and word limits (they were not available to me), keep the description identical in both submissions, and submit before 3:30 PM PKT on 15 November.
