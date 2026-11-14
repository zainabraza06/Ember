# Human spot check of transcribed values

Seeded random sample (seed 20261019) of 10 of 489 printed values transcribed by hand from NASA reports. For each row, open the report (NTRS id: https://ntrs.nasa.gov/citations/<id>; the PDFs are in `data/raw/ntrs/<id>/`, the two large ones are git-ignored, see their `info.md`), go to the page and table, and compare the value as printed. Fill in the last two columns (initials and date; OK / mismatch with the value you read). Any mismatch: correct the transcribed CSV and rerun `python -m pipeline`.

| # | file / test | NTRS report | page (PDF page; printed page where known) and table, figure or slide | field | transcribed value | verified by | result |
|---|---|---|---|---|---|---|---|
| 1 | `NTRS20150023456_flex_tests_275_280.csv / NTRS20150023456:FLEX-277` | 20150023456 | PDF p.34 (printed p.28), Table IX, row FLEX-277 | pressure as printed | 530.4 mmHg | ZRM | OK 2026-11-14 |
| 2 | `NTRS20110008636_limits.csv / T08636-045` | 20110008636 | PDF p.6, Table 6 | MOC (vol% O2) | 19 | AI | value verified, ID mapping pending |
| 3 | `NTRS20170004702_limits.csv / T04702-16` | 20170004702 | PDF p.3-4 (paper p.3-4), Table 2 (thickness from Table 1) | pressure as printed | 10.2 psia (text: 70.3 kPa) | AI | OK (AI-checked against PDF, 2026-11-14) |
| 4 | `sidecars/bass2_table5_1.csv / PSI-25:M20` | 20210011385 | PDF p.65 (printed p.57), Table 5.1 | velocity list (cm/s) | 10 | AI | OK (AI-checked against PDF, 2026-11-14) |
| 5 | `NTRS20110008636_limits.csv / T08636-010` | 20110008636 | PDF p.5, Table 2 | pressure as printed | 14.7 psia (default) | AI | OK (AI-checked against PDF, 2026-11-14) |
| 6 | `NTRS20110008636_limits.csv / T08636-026` | 20110008636 | PDF p.6, Table 5 | MOC (vol% O2) | 21.0 | AI | OK (AI-checked against PDF, 2026-11-14) |
| 7 | `NTRS20110008636_limits.csv / T08636-070` | 20110008636 | PDF p.7, Table 9 | MOC (vol% O2) | 35 | AI | OK (AI-checked against PDF, 2026-11-14) |
| 8 | `NTRS20130010991_tableI_limits.csv / T10991-10` | 20130010991 | PDF p.6 (paper p.6), Table I, row "0g ULOI*/MOC*", column Mylar G | MOC (vol% O2) | 16.0 | ZRM | OK 2026-11-14 |
| 9 | `NTRS20110008636_limits.csv / T08636-040` | 20110008636 | PDF p.6, Table 6 | ULOI (vol% O2) | 23.5 | AI | value verified, ID mapping pending |
| 10 | `NTRS20110008636_limits.csv / T08636-035` | 20110008636 | PDF p.6, Table 6 | pressure as printed | 10.2 psia (footnote a) | AI | OK (AI-checked against PDF, 2026-11-14) |

## Notes

- Row 1 and row 8: checked against the PDF by ZRM (reviewer), 2026-11-14.
- Rows 3, 4, 5, 6, 7 and 10: checked against the source PDFs by the AI (second reviewer), 2026-11-14.
- Row 3: the 70.3 kPa text is printed in the report.
- Row 5: the 14.7 psia default is stated in the introduction ("Except as noted, the tests were conducted at 14.7 psia"), not in Table 2 itself.
- Rows 2 and 9: the printed value was verified; the mapping of the test IDs (T08636-045, T08636-040) to the Table 6 rows is pending, so they are not marked OK.

## Summary

10 of 10 values AI-checked against the source PDFs, of which 2 were also checked by a person (ZRM). 0 individual claims opened by a person.
