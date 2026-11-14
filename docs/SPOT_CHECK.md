# M2 spot check (acceptance: 20 random rows, zero unexplained mismatches)

Run 2026-10-19 with `python -m pipeline.spot_check` (seed 20261019, simple random sample of 20 of the 885 rows in `data/processed/tests.csv`). Full per-check details: [data/processed/spot_check_results.md](../data/processed/spot_check_results.md). The checker (`pipeline/spot_check.py`) re-reads each source independently of the pipeline's mapping code.

## What is checked
- **PSI rows** (cell level): the `test_id` key equals the key in the source row; every recorded original value in `orig_values` equals the source cell text; every converted value (pressure mmHg, bar or atm to kPa; vol% to mole fraction; cm or mm; seconds; cm/s; mm/s) equals an independent recomputation within 1e-4; each converted field has a recorded original; `material_or_fuel` equals the source cell; `outcome_class` equals an independent rule table (FLEX Test end label, CFI-G rules, Saffire-II burn-length and 1 g rules; BASS-II stays unknown until a human approves the LLM proposal); for Saffire `pair_id` partners exist (one 0 g and one 1 g row).
- **BASS-II rows, report-sourced fields:** the words of the Appendix A observation appear on the cited PDF page; the Table 5.1 row (thickness, width, sides) is on PDF p.65 and a numeric flow equals its single velocity; a stated pressure ("1 atm") is on the cited page with value 101.325 kPa and flag `nominal`.
- **Transcribed rows** (including the FLEX report tests 275-280): the cited PDF page (or slides) is re-extracted and every transcribed number must appear there (ULOI, MOC, margin, spread rate, oxygen, burn time, extinction diameter, droplet diameter, pressure as printed, Test end label). This is weaker than the cell-level check (presence on the page, not position); it complements the rendered-table verification done during transcription and the human sheet [HUMAN_SPOT_CHECK.md](HUMAN_SPOT_CHECK.md).

## Result: 20 rows, 0 failures
| # | test_id | family | data_origin | checks passed | checks failed |
|---|---|---|---|---|---|
| 1 | PSI-159:normal:21291C1 | CFI-G | psi_table | 11 | 0 |
| 2 | PSI-159:inverse:21216H2 | CFI-G | psi_table | 9 | 0 |
| 3 | PSI-25:T7 | BASS-II | psi_table | 8 | 0 |
| 4 | PSI-69:118 | FLEX | psi_table | 10 | 0 |
| 5 | PSI-69:212 | FLEX | psi_table | 10 | 0 |
| 6 | PSI-159:normal:21112A4 | CFI-G | psi_table | 11 | 0 |
| 7 | PSI-159:normal:21137A7 | CFI-G | psi_table | 11 | 0 |
| 8 | PSI-159:inverse:21202A4 | CFI-G | psi_table | 9 | 0 |
| 9 | PSI-69:268 | FLEX | psi_table | 10 | 0 |
| 10 | PSI-25:T28a | BASS-II | psi_table | 9 | 0 |
| 11 | PSI-69:023 | FLEX | psi_table | 10 | 0 |
| 12 | PSI-159:inverse:21228K2 | CFI-G | psi_table | 9 | 0 |
| 13 | PSI-69:136 | FLEX | psi_table | 10 | 0 |
| 14 | NTRS20150023456:FLEX-280 | FLEX | transcribed_from_table | 10 | 0 |
| 15 | PSI-100:S2 | Saffire | psi_table | 9 | 0 |
| 16 | PSI-159:normal:21153A1 | CFI-G | psi_table | 11 | 0 |
| 17 | PSI-159:inverse:21202H2 | CFI-G | psi_table | 9 | 0 |
| 18 | PSI-159:normal:21102C1 | CFI-G | psi_table | 11 | 0 |
| 19 | PSI-25:M9 | BASS-II | psi_table | 12 | 0 |
| 20 | PSI-69:272 | FLEX | psi_table | 10 | 0 |

**Rows with at least one failed check: 0 of 20**

## Findings and fixes
1. **Mismatches in the earlier (pre-D9) run, already fixed:** 2 of 20 rows had failed (`T08636-069`, `T08636-057`): the default pressure 14.7 psia is stated on PDF p.3 of that report, not on the table page the `source_ref` cited. The citation was completed for every row that uses the default.
2. **This run, before the final result:** the all-rows pass first reported 277 failing rows and then 3. All were bugs in my checker, not data mismatches: it tried to recompute a conversion for the `outcome_class` entry in `orig_values` (277 FLEX rows), and, after I rewrote the checker, it no longer handled the split Saffire-II card 2-7 whose cells read "5 and 24 cm" and "0.85 and 0.37 mm" (3 rows). Both were corrected in the checker; the data needed no fix.
3. **Extended runs** with the same checks: **all 885 rows: 0 failures**; a stratified sample (one row per source file, 13 rows): 0 failures.
4. **Not mismatches but worth knowing (flagged in the data, see REVIEW_QUEUE.md):** PSI-99 sample 2-6 flow is 20 cm/s in PSI and 25 cm/s in the report (flag `source_conflict`, CONFLICTS.md); 58 FLEX tests have a Test end label that disagrees with the extinction diameter (listed in REVIEW_QUEUE.md; the label is the outcome, D22); 6 BASS-II rows have a final O2 far from the initial one.

## Limits of this check
- Transcribed-row checks verify presence of numbers on the cited page, not their position in the table. A person should compare the 10 values in HUMAN_SPOT_CHECK.md with the PDFs.
- The outcome rules for CFI-G, Saffire and the LLM proposals for BASS-II are rules or proposals; the check confirms the pipeline follows them, not that they are right (human review pending, REVIEW_QUEUE.md).
- No check can verify values the sources do not contain (for example pressure for Saffire is empty and flagged).
- The checker and the pipeline were written by the same author; the comparison against the raw cell text and the PDF pages is the independent part. Report-sourced checks need the two large PDFs, which are git-ignored (see their `info.md` for URL and SHA-256).
