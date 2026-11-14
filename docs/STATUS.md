# Status

Last updated: 2026-10-19.

## Current phase
**Build phase (team decision 2026-10-19, PLAN.md sections 1.3, 7, 9):** the full product is built between 19 October and 13 November; the hackathon weekend is for final testing, the demo video, slides, pitch rehearsal and submission inside the official window. Work is committed to git with clear messages so the build history is visible and the build period can be disclosed honestly. Decision D7 still holds: no further automated fetching from PSI.

The Islamabad organizers' answer on pre-event code (RULES.md section 7, question a) **no longer blocks anything**; it stays on the open-questions list only.

## Reminders (recurring)
- **Re-check the official challenge page weekly** (next: by 2026-10-26) and paste new sections into CHALLENGE.md: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall-ai-powered-fire-safety-insights-from-microgravity-combustion-data/
- **On 13 November 2026 re-read the Project Submission Guide and Judging & Awards Guide** and update RULES.md, REQUIREMENTS.md and PLAN.md sections 1.3-1.4. Until then demo format, the five judging criteria and global-nomination requirements stay "unverified, from PLAN.md".
- Update docs/SI_USAGE.md at the end of every task.

## Completed modules
- **M0 Challenge lock and rules:** done and accepted 2026-10-19.
- **M1 Data acquisition and provenance catalog:** done and accepted 2026-10-19.
- **M2 Unified schema and harmonized test table:** done 2026-10-19, pending team review. Outputs: [DATA_DICTIONARY.md](DATA_DICTIONARY.md) (v3, matches the pipeline), [OUTCOME_MAPPING.md](OUTCOME_MAPPING.md) (D10-D14), [GRAVITY_COVERAGE.md](GRAVITY_COVERAGE.md), [REVIEW_QUEUE.md](REVIEW_QUEUE.md), [SPOT_CHECK.md](SPOT_CHECK.md), [HUMAN_SPOT_CHECK.md](HUMAN_SPOT_CHECK.md), `data/transcribed/` (6 report CSVs, 126 rows, plus sidecars), `data/llm/` and `data/review/` (BASS-II proposals and the empty review file), the pipeline (`pipeline/`, `python -m pipeline`), **`data/processed/tests.csv` and `tests.parquet` (885 rows)** with `build_report.json`, 26 unit tests (`tests/`).
  - M2 acceptance: 20-row random spot check with zero unexplained mismatches: **met** (0 failures; all 885 rows and a stratified sample also pass); every row has a source reference, data origin and quality flags: met (checked on every build); reproducible from one command with originals kept next to converted values: met.

### M2 findings in brief
- **Final table (885 rows):** FLEX 280, CFI-G 333, BASS-II 129, Saffire 23, partial-gravity literature 29, 1 g screening 91. By outcome class: self_extinguished 369, unknown 266, externally_terminated 91, no_ignition 57, other 64, burned_to_completion 38.
- **CFI-G labels:** FT = flow terminated is confirmed by the UMD thesis (Kim 2022, Table 4.1 note c). SE -> self_extinguished is confirmed by the thesis (D23: it calls these flames "radiatively extinguished"); TFP = thin filament pyrometry. "flash", "PCI-A..G" and "Day" remain undocumented.
- **FLEX (D22):** the Test end label is the outcome (Extinction 191, Completion 28, Disruption 61, unknown 0). The extinction diameter is a consistency check: 58 tests disagree (27 Extinction without diameter, 20 Disruption and 11 Completion with a positive diameter), all listed in REVIEW_QUEUE.md section 3. Tests 275-280 exist only in the report, which prints their labels.
- **BASS-II:** outcomes extracted for 126 tests from Appendix A; 129 LLM proposals (80 self_extinguished, 29 unknown, 8 externally_terminated, 7 burned_to_completion, 5 no_ignition; 57 high, 62 medium, 10 low confidence), none approved yet. Numeric flow for 5 Table 5.1 tests (15 more as steps); pressure "1 atm" for 31 tests.
- **Saffire-II:** the "?-g Spread Length" column is "Spread Rate" in the report (header corrected); 9 one-g rows paired by `pair_id`. D24: the report corrects "037 mm" to 0.37 mm, the swapped PSI-98 length/width and two blank materials (all applied, flag `corrected_from_report`); the flow of sample 2-6 is a genuine conflict (PSI 20 cm/s kept, report 25 cm/s in `alt_value_report`, flag `source_conflict`, CONFLICTS.md).
- **Partial gravity** remains an evidence gap (D3): 3 reports transcribed, 5 lunar and 3 Martian rows, none at exploration atmospheres.

## In progress
**2026-11-14 build (feature freeze 23:30 PKT):** the explorer is a static page, `site/index.html`, deployed on GitHub Pages at https://zainabraza06.github.io/Nasa_Challange/ (branch `gh-pages`, produced from `site/` with `git subtree split --prefix=site`). Tabs: Atmosphere map (home), Investigations, Compare, Ranking, Interpretation, Ask, Mission brief, Atmospheres, Partial gravity, Earth, About; "Play the story" runs a captioned walk of about 85 seconds. Ranking and interpretation are deterministic code over the data (docs/RANKING.md). The page runs no model and makes no network calls.
**Evidence ledger run (2026-11-14):** 107 extraction and 265 verification requests, 845,622 tokens in total. Models used (exact versions returned by the APIs): gemini-2.5-flash (21 requests); gemini-3-flash-preview (19 requests); gemini-3.1-flash-lite (50 requests); gemini-3.6-flash (17 requests); openai/gpt-oss-120b (265 requests). Claims: 181 verified_auto, 0 pending_verification (unreviewed), 84 needs_review, 0 rejected. Claims per gravity class (non-rejected, usable on the site): earth_1g 9, lunar 2, mars 2, microgravity 35, not_stated 130, partial_other 3. Review of claims by people: not done (placeholder for the team). Details: LEDGER_REPORT.md.
**Repository:** a new repository (`origin` = https://github.com/zainabraza06/Nasa_Challange.git) holds one import commit of the earlier project (2026-10-19 to 2026-11-14, see README Provenance) plus the commits made on 2026-11-14.
**Not done:** BASS-II second rater (needs the Llama model, not available on the Groq account), human review of claims and of the BASS-II proposals, any live model on the site.

## Open questions
1. Islamabad organizers (RULES.md section 7): pre-event code (answer wanted, no longer a blocker), pitch format, winners, venue/internet, exact deadline. A team member is asking.
2. 2026 submission and judging guides unpublished until 13 November.
3. Challenge page: Objectives, Considerations, NASA Resources, Partner Resources still unpublished (as of 2026-10-19).
4. Human review: 129 BASS-II outcome proposals (REVIEW_QUEUE.md section 1, `data/review/outcome_review.csv`); the CFI-G `class_from_comment` rows; the 58 FLEX label/diameter disagreements; the 10 transcribed values in HUMAN_SPOT_CHECK.md.
5. Documentation gaps: "flash", "PCI-A..G"; Saffire I and III end states.
6. Still open from M1: PSI-10 license (excluded meanwhile, D6); Task Book search and terms; JAXA/ISAS data terms; confirm acceptable use of PSI's undocumented endpoints already used in M1.
7. Partner datasets (JAXA, ESA, CSA) pending the official list.
8. The two large reports are git-ignored (D16); anyone running the report-sourced spot checks must download them (URL and SHA-256 in their `info.md`).

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-10-19 | Moved `PLAN (2).md` to `PLAN.md`, `CHALLENGE.md` to `docs/` | Match PLAN.md paths |
| 2026-10-19 | AI central, not decorative (W1) | Title "AI-Powered" vs summary "SI powered" |
| 2026-10-19 | Demo format, five judging criteria, global-nomination requirements stay "unverified, from PLAN.md" | 2026 guides unpublished |
| 2026-10-19 | Team is registered under the Islamabad Local Event; organizer questions remain open | Team statement |
| 2026-10-19 | Binding deadline = the earlier of Local Event end time and Sunday 15 Nov 11:59 PM local; plan to submit by Sunday midday | Team decision; sources disagree |
| 2026-10-19 | Apache 2.0 for our code; SI_USAGE.md running log; THIRD_PARTY.md gate: nothing with an unknown license enters the product | Team decision; FAQ requires SI-use disclosure |
| 2026-10-19 | Partial gravity handled as an evidence gap plus manually transcribed report data, not PSI tables | None in PSI tables |
| 2026-10-19 | **D1** Families approved: FLEX (PSI-69), CFI-G (PSI-159), BASS-II (PSI-25) + BASS (PSI-26), Saffire I-III (PSI-98/99/100). No fifth family. Roles: FLEX and CFI-G feed the flammability envelope model; BASS-II/BASS and Saffire feed material insights and the mission brief | Team decision (M1 review) |
| 2026-10-19 | **D2** Download only the two over-size PDFs (FLEX detailed results, BASS-II summary report) and check BASS-II for per-test outcomes and conditions | Team decision |
| 2026-10-19 | **D3** Create a small hand-transcribed partial-gravity dataset from NTRS 20010059376, 20130010991, 20250010653 AND keep partial gravity flagged as an evidence gap; every value carries report ID, page, table/figure and a data-origin flag | Team decision |
| 2026-10-19 | **D4** Transcribe per-material results from NTRS 20110008636 and 20170004702; label as 1 g screening data, not microgravity | Team decision |
| 2026-10-19 | **D5** Keep each family's original outcome label in `outcome_raw`; add `outcome_class` with exactly: no_ignition, self_extinguished, burned_to_completion, externally_terminated, other, unknown. externally_terminated is censored ("sustained at least until termination"), never extinction. FLEX "Disruption" maps to other. Mapping table per family; flag undocumented labels | Team decision |
| 2026-10-19 | **D6** PSI-10 excluded until its license is confirmed | Team decision |
| 2026-10-19 | **D7** No further automated fetching from PSI; use already-downloaded files or normal manual download links | Team decision |
| 2026-10-19 | **D8** NTRS text is cite-and-paraphrase only; numeric tables may be transcribed with full citation | Team decision |
| 2026-10-19 | ~~M2 is documentation and transcription only~~ **Superseded:** full build 19 Oct to 13 Nov, submission during the event window; the M2 restriction is removed. PLAN.md replaced with the new version (sections 1.3, 7, 9 re-read). Commit to git with clear messages from now on; keep the full history and disclose the build period if asked | Team decision |
| 2026-10-19 | Git-ignore the two over-size PDFs (keep their info.md); `data/raw/**` is stored byte-exact (`.gitattributes`). **Correction:** an earlier commit had forced the PDFs into history with `git add -f`; the 7 unpushed local commits were rewritten to drop them (`origin/main` was untouched) and `.git` went from 91 MB to 8.6 MB | Avoid 90 MB of binaries in history; preserve raw provenance |
| 2026-10-19 | Pipeline uses the Python standard library plus `pyarrow` (Apache-2.0) for the Parquet output; CSV is canonical; originals in `orig_values`, family-specific fields in `ext` (JSON) | The task asks for CSV and Parquet; keeps dependencies minimal |
| 2026-10-19 | (Claude, pending review) Saffire-II card 2-7 split into two test rows; CFI-G empty rows dropped; BASS-II oxygen anomalies flagged not corrected; material normalizer rules in `pipeline/materials.py` | Documented in DATA_DICTIONARY.md; needs team review |
| 2026-10-19 | (Claude) No data points were read from figures; only legend text and printed statements were transcribed | Overlapping symbols made individual values unreadable (D3 allows read_from_figure only for clearly readable values) |
| 2026-10-19 | **D9** Approve the schema additions (`record_type`, `spread_orientation`, size fields, `oxygen_fraction_final`, `*_orig`, `uloi/moc/margin`, `limit_criterion`, `spread_rate_basis`) and the `data_origin` value `transcribed_from_text`. Also added for D12/D14: `pair_id`, `outcome_class_proposed`, `outcome_proposal_confidence`, `outcome_review_status` | Team decision |
| 2026-10-19 | **D10** Outcome rules approved. CFI-G: SE -> self_extinguished, FT -> externally_terminated after confirming both meanings in CFI-G documentation and recording the source (result: FT confirmed by the UMD thesis; SE consistent with its "RE", letters not defined; see OUTCOME_MAPPING.md). "flash" and "TFP" -> unknown until documented; "Day" and "PCI-A..G" are metadata, not outcomes. The comment-based overrides stay, flagged `class_from_comment`, and are listed in REVIEW_QUEUE.md | Team decision |
| 2026-10-19 | **D11 (superseded by D22)** FLEX: "Test end" is a raw column, never used for outcomes (the outcome class uses the visible flame extinction diameter; this supersedes the part of D5 that mapped Disruption to other). Transcribe tests 275-280 from NTRS 20150023456 (done) | Team decision |
| 2026-10-19 | **D22** FLEX: the Test end labels are the outcome labels (Extinction -> self_extinguished, Completion -> burned_to_completion, Disruption -> other); this **reverses D11**, which was a team error. The extinction diameter is only a consistency check, disagreements flagged `diameter_label_disagree` and listed in REVIEW_QUEUE.md | Team decision |
| 2026-10-19 | **D23** CFI-G SE -> self_extinguished is confirmed by the UMD thesis (Kim 2022, "radiatively extinguished"); cited in OUTCOME_MAPPING.md and THIRD_PARTY.md, not redistributed | Team decision |
| 2026-10-19 | **D24** Saffire report vs PSI: clear errors corrected and flagged `corrected_from_report` ("037 mm" -> 0.37 mm, PSI-98 length/width swap, two blank materials); genuine conflict (sample 2-6 flow) keeps PSI 20 cm/s, report 25 cm/s in new column `alt_value_report`, flag `source_conflict`, listed in CONFLICTS.md | Team decision |
| 2026-10-19 | **D25 and D26 withdrawn** (Mistral removed free-plan API keys); replaced by D31 and D32 | Team decision |
| 2026-10-19 | **D31** LLM providers for the ledger: extraction with the Google Gemini API (free tier, `GEMINI_API_KEY`, strongest model that works, JSON mode, temperature 0); support check and the BASS-II second rater with Groq `llama-3.3-70b-versatile` (`GROQ_API_KEY`). Two model families keep extraction and verification independent. Keys never printed, logged or committed | Team decision |
| 2026-10-19 | **D32** Limits: per-provider requests per minute and per day (from the official docs / account pages) plus `LEDGER_MAX_TOKENS` (default 3,000,000); at a daily limit the run saves progress, reports the chunks remaining and a rerun the next day resumes from the cache | Team decision |
| 2026-10-19 | **D27** Rate limiting with exponential backoff and automatic resume from the cache; run the full extraction as soon as the pilot passes | Team decision |
| 2026-10-19 | **D28** SI_USAGE.md states honestly how the 129 BASS-II proposals were made (by the coding assistant reading text, no API call) | Team decision |
| 2026-10-19 | **D12** BASS-II: extract all Appendix A observations (done: 126 of 129; O20-O22 stay unknown); an LLM proposes outcome_class with confidence; original text in outcome_raw; every proposal in REVIEW_QUEUE.md; only approved classes used downstream. Numeric flow only for the 20 Table 5.1 tests; pressure only where the report text states it (origin transcribed_from_text, flag nominal) | Team decision |
| 2026-10-19 | **D13** BASS (PSI-26) removed from the structured test table; evidence ledger (M3) only | Team decision |
| 2026-10-19 | **D14** Saffire-II 1 g comparison values become separate 1 g rows linked by `pair_id`; "Insignificant" burn time: value empty, word kept in outcome_raw; the "?-g Spread Length" values are spread rates, mapped with flag `header_corrected` (confirmed against NTRS 20170008805 slide 29) | Team decision |
| 2026-10-19 | **D15** Gravity: microgravity rows use 0 with gravity_source = nominal; lunar tests without a printed value use 0.165 with gravity_source = nominal and a note | Team decision |
| 2026-10-19 | **D16** Large PDFs git-ignored (`data/raw/ntrs/*.pdf` and the two large files); each info.md keeps URL, size and SHA-256 | Team decision |
| 2026-10-19 | (Claude, pending review) Pressure "1 atm" applied only to the tests the report text names (B3, B4, B11, B13 from a figure caption; the 27 T'ien SIBAL tests from section 7.1.3); other pressure statements are listed, not applied | The scope of the other statements is not stated per test |
| 2026-10-19 | (Claude, pending review) Saffire report-vs-PSI differences (flow of 2-6, blank materials, "037 mm", PSI-98 length/width) are flagged, not applied | Not covered by D14 |

## What was corrected in earlier drafts (kept for the record)
**M1 (re-verification of the pre-M0 drafts):** (1) the draft said table contents were not inspected and the CSV route was unavailable: now inspected; (2) FLEX conditions were taken from approach text (0.5-1.5 atm); the table shows 526-2320 mmHg and O2 0.12-0.34; (3) CFI-G was ranked last as "gas flames" but has clear outcome labels and 333 usable tests: now recommended; Flame Design and BRE were demoted; (4) "no partial-gravity test seen" was true for PSI tables only: NTRS partial-gravity reports are now listed; (5) Saffire table sizes are now counts (2, 9, 2 samples); (6) the draft's "DBP-coated sample" for PSI-102 (taken from PSI-101 text) was replaced by what the SAME table shows; (7) unknown test counts were replaced by counts from the tables; (8) unverifiable items (media size, NTRS rights as "license", JAXA/Task Book terms) were marked unknown.
**M2:** the pre-M1 DATA_DICTIONARY.md was replaced in full (all "Likely/Partial" ratings are now answered from real columns). DATA_SURVEY.md was updated to note that the two over-size reports are now downloaded. In the first transcription draft, `record_id` was renamed `test_id` to match the unified schema. **M2 build phase:** outcome rules changed by D10, D11 and D14 (flash rows now unknown; FLEX outcomes from the extinction diameter; Saffire-II 1 g rows and header correction); gravity source changed to nominal (D15); BASS removed from the table (D13); counts moved from 992 to 885 rows.

## Next step
1. Team reviews M2: the 10 values in HUMAN_SPOT_CHECK.md, the BASS-II proposals (REVIEW_QUEUE.md), the CFI-G overrides and the Saffire report-vs-PSI differences.
2. M3 Evidence Ledger (week 2 in PLAN.md section 9): claim schema, extraction with span verification, review queue, 30-claim audit; first needs the team's choice of LLM API and embedding model (record in SI_USAGE.md and THIRD_PARTY.md before use). BASS (PSI-26) and the BASS-II and FLEX reports are ledger sources.
3. In parallel (week 1 items still open): first 20 gold questions for M10; repo skeleton for backend and frontend; deployment accounts.
