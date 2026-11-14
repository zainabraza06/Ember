# Requirements tracker (M0)

Derived from PLAN.md section 1; submission rows also draw on [RULES.md](RULES.md). Status values: not started / in progress / done. Update after each module (PLAN.md rule 9).

Challenge wording note: the page title says "**AI**-Powered" while the summary says "**super intelligence (SI)** powered dashboard", and the 2026 FAQ uses "Super Intelligence" in place of "Artificial Intelligence" and requires submissions to describe SI tool use (https://www.spaceappschallenge.org/resources/participant-faqs/). We treat these as one requirement: **AI must be central to the product, not decorative** (row W1).

| ID | Requirement | Type | Module(s) | Acceptance evidence | Status |
|---|---|---|---|---|---|
| R1 | Interactive dashboard | explicit | M9 | Deployed app with filters, comparisons, charts, scenario controls; section-3 demo runs end-to-end in under 3 minutes on a fresh device | not started |
| R2 | AI-powered | explicit | M3, M4, M6, M8 | LLM extraction, grounded Q&A, learned model, generated briefs all running in the app, with evaluation numbers (M10). M3: Gemini-based claim extraction and Groq/Llama-based verification built (docs/LEDGER_SCHEMA.md); live run state in LEDGER_REPORT.md | not started |
| W1 | AI central, not decorative (title "AI-Powered" vs summary "SI powered") | explicit (wording) | M3, M4, M6, M8, M13 | Demo and slides show that removing the AI layer removes the core outputs; SI-use description written for submission | not started |
| R3 | Summarize findings | explicit | M3, M8 | Per-experiment, per-material and per-scenario summaries; zero uncited sentences in 3 sampled briefs | not started |
| R4 | Rank findings | explicit | M5 | Ranked list with per-criterion scores and adjustable weights; every score reproducible from documented formulas | not started |
| R5 | Interpret findings | explicit | M6 | Effect directions, consensus/contradiction list, envelope with uncertainty; sanity checks pass | not started |
| R6 | Use NASA microgravity combustion data | explicit | M1 | data/catalog.csv (93 rows) covers all 24 PSI Combustion investigations, 56 NTRS reports, standards, Glenn/partner pages; 22 PSI tables downloaded with provenance (M1 done; family recommendation in docs/DATA_SURVEY.md) | done (M1); team review pending |
| R7 | Fire safety insights | explicit | M8 | Brief contains material screening, atmosphere risk, detection/suppression notes with citations | not started |
| R8 | For human space exploration (Moon, Mars) | explicit | M5, M6, M8 | Mission profiles (lunar, Mars) with partial-gravity handling; extrapolation labels | not started |
| R9 | Address "hard to find, compare, understand" | explicit | M2, M9 | Unified test table built by the pipeline (data/processed/tests.csv and .parquet, 885 rows) per DATA_DICTIONARY.md v3; 20-row spot check passed (SPOT_CHECK.md); plain-language layer and Explore page (M9) not started | in progress |
| I1 | Scientific validity | implicit | M6, M10 | No invented numbers; leave-one-experiment-out results vs baseline; physics sanity checks | not started |
| I2 | Traceability | implicit | M2, M3, M9 | Every row of tests.csv carries source_ref (file + data_row, or report + page/table/slide), data_origin and quality_flags; original values kept in orig_values; 20-row spot check 0 mismatches and all 885 rows pass (SPOT_CHECK.md); 10 transcribed values await human verification (HUMAN_SPOT_CHECK.md). Claims: every ledger claim carries doc, PDF page and a verbatim span verified against the PDF text (M3 machinery built); UI traceability (M9) not started | in progress |
| I3 | Honest uncertainty | implicit | M4, M6 | Evidence strength shown; refusals; M2 adds the censored outcome class (externally_terminated), proposal-vs-approved separation for LLM outcome classes, and review queue (REVIEW_QUEUE.md) | in progress |
| I4 | Partial-gravity gap stated explicitly | implicit | M6, M7, M9 | docs/GRAVITY_COVERAGE.md tabulates evidence by gravity level; partial gravity kept flagged as a gap (D3); 3 reports transcribed (lunar/Martian/other) and none at exploration atmospheres | in progress |
| I5 | Multiple audiences | implicit | M8, M9 | Engineer brief (P0); crew and public modes (P1) | not started |
| I6 | Works live | implicit | M12, M13 | Stable deployed demo plus recorded fallback | not started |
| I7 | Reusable / continuable | implicit | M12 | Public repo, README, reproducible data build; stranger can run it | not started |
| S1 | Demo: video up to 30 s with English subtitles OR up to 7 English slides; links only | submission (2026 format unverified; PLAN.md) | M13 | Video and/or deck URL on project page; format re-checked against 2026 guide on 13 Nov | not started |
| S2 | Public code repository linked, NASA/partner data clearly listed | submission (2026 rule unverified; PLAN.md) | M12, M13 | Repo URL on project page; list of NASA data used | not started |
| S3 | Describe how SI tools were used | submission (FAQ) | M13 | Written SI-use statement in submission, built from docs/SI_USAGE.md (running log, includes the LLM-proposed BASS-II outcome classes of decision D12) | in progress |
| S4 | Third-party code/datasets open or free, cited, licenses identified | submission (Terms) | M1, M12 | docs/THIRD_PARTY.md lists every source, library and tool with license and URL; nothing with an unknown license enters the product (PSI-10 excluded, D6); NTRS reports cited and transcribed only | in progress |
| S5 | Team of at most six, all registered for the same Local Event | submission | M0 | Team roster confirmed (team registered under the Islamabad Local Event) | in progress |
| S6 | Submit by the EARLIER of the Local Event end time and Sunday 15 Nov 11:59 PM local time; internal target Sunday midday | submission | M13 | Organizers confirm the deadline (RULES.md section 7); submission made by Sunday midday 15 Nov | not started |
| S7 | Local judging format and pre-event work rules confirmed with Islamabad hosts | submission | M0 | Answers to RULES.md section 7 recorded. Pre-event code no longer blocks anything (team decision, PLAN.md 1.3); the organizer answer is still wanted and stays open | not started |
| J1 | Impact | judging | M8 | Named user and decision; exportable brief | not started |
| J2 | Creativity | judging | M3, M6, M7 | Evidence ledger with contradiction detection; partial-gravity lens; next-experiment recommender | not started |
| J3 | Validity | judging | M6, M10 | Measured evaluation numbers shown in-app and in docs/EVALUATION.md | not started |
| J4 | Relevance | judging | M1, M5 | Every NASA/partner resource used or considered; direct mapping to summarize/rank/interpret | not started |
| J5 | Presentation | judging | M13 | 30-s video / 7-slide deck around one story; clean UI | not started |
| M0a | Every NASA/partner resource listed on the challenge page appears in the M1 catalog (used / considered) | module acceptance | M0, M1 | Blocked: challenge resource list unpublished. M1 catalog already includes NASA Glenn, Task Book, JAXA, ESA, CSA rows marked pending | not started |
| O1 | Official: per-investigation summary (objectives, fuels incl. shape/size, oxygen and airflow, variables, sensors) | official Potential Considerations | G1 | Investigations tab, all 24 PSI combustion investigations; fuels/conditions from the table only for 6 (others: not documented in the catalog). See OFFICIAL_ALIGNMENT.md | partly met |
| O2 | Official: similarities and differences between investigations | official Potential Considerations | G1 | Compare tab (2-3 investigations, short fields highlighted) | met |
| O3 | Official: prevention / detection / suppression | official Background | G2 | Tags with reasons plus filter; 11 untagged | met |
| O4 | Official: hardware groups (ACME/CIR, MDCA/CIR, MSG flow duct) | official Potential Considerations | G1 | Hardware group on every investigation, filterable | met |
| O5 | Official: mission atmospheres (lunar base and rover >=30% O2 and <=10.2 psi; suit 100% O2, 4.3 psi) | official Potential Considerations | G3 | Mission tab; kPa computed in pipeline/profiles.py; suit has no test rows | met |
| O6 | Official: partial-gravity bounds (no PSI data; LUCI, FM2, E-FIELD; 0 g and 1 g bound) | official Potential Considerations | G4 | Partial-gravity tab; literature rows labelled outside PSI | met |
| O7 | Official: applications to fire safety on Earth (three spinoffs) | official Objectives / Resources | G5 | Earth applications tab: links only, no analysis | partly met |
| O8 | Official: scope note and the ten resources | official Objectives / Resources | G6 | About tab | met |
| O9 | Official: SI-powered dashboard that summarizes, ranks and interprets | official Objectives | M3-M9 | Ranking (formula, RANKING.md), computed interpretation summaries, claim retrieval (Ask) and a cited mission brief are built; no language model runs on the page; claims are verified or labelled unreviewed | partly met |
| O10 | Official: extract data supporting predictive modeling | official Objectives | M2 | tests.csv / tests.parquet in the repository, not offered on the site | partly met |
| O11 | Islamabad local Google Form by Sun 15 Nov 2026, 3:30 PM PKT, plus the website submission | local event | M13 | Section 2 of SUBMISSION_DRAFT.md (names and contacts are placeholders) | in progress |
