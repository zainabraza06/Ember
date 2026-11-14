# Hand-transcribed data (team decisions D3, D4, D8)

Numeric values were transcribed by hand from NASA technical reports (one CSV per source report). Text is cite-and-paraphrase only; numbers carry full citation. All files share one column set (below) that follows the unified field names in [../../docs/DATA_DICTIONARY.md](../../docs/DATA_DICTIONARY.md). Empty = not printed or not readable; nothing was estimated. The source PDFs are in `data/raw/ntrs/<NTRS id>/`.

Transcription method: tables were read from the PDF text layer and checked by viewing the rendered table image (fractions and column alignment). After transcription every ULOI/MOC/margin value was checked by script against the source page text (all 209 values found on the cited pages; ULOI/MOC pairs are adjacent in the text for 87 of 88 table rows, the remaining one has material labels between the numbers). Values read from figures: none were read as data points; figure legends were read where printed.

| File | Source report | Pages | Rows | What a row is | Method / `data_origin` | Gravity |
|---|---|---|---|---|---|---|
| NTRS20010059376_series.csv | NTRS 20010059376, Feier, Shih, Sacksteder, T'ien, AIAA-2001-0466, "Upward flame spread over thin solids in partial gravity" | PDF p.9-10 (paper p.7-8) | 16: 13 `series_summary` (one per plotted pressure series, Fig. 8-10 legends) + 3 text statements for 1 g | one plotted series or one printed statement | `read_from_figure` (legend text) and `transcribed_from_text` | 0.10, 0.16, 0.38 g and 1 g (series not separable) |
| NTRS20130010991_tableI_limits.csv | NTRS 20130010991, Olson and Ferkul, "Evaluating material flammability in microgravity and Martian gravity..." | PDF p.6 (Table I); p.3-4 for conditions | 12 `limit` rows (3 materials x 4 gravity cases) | ULOI, MOC and oxygen margin for one material and gravity | `transcribed_from_table` | 1 g, 0.38 g, lunar, 0 g |
| NTRS20250010653_luci_tests.csv | NTRS 20250010653, Ferkul et al., LUCI slides (2025 ASGSR) | slides 12-44 | 4 `test` rows (2 lunar-g flight burns, 2 1 g comparison burns) | one burn | `transcribed_from_text` (slide text) | lunar (assumed 0.16 g) and 1 g |
| NTRS20110008636_limits.csv | NTRS 20110008636, Hirsch et al., "Selected parametric effects on materials flammability limits" | PDF p.5-7, Tables 2-9 | 70 `limit` rows | ULOI and MOC for one material/configuration | `transcribed_from_table` | **1 g screening data, not microgravity** |
| NTRS20150023456_flex_tests_275_280.csv | NTRS 20150023456, Dietrich et al., NASA/TP-2015-216046, FLEX detailed results | PDF p.33-34 (printed p.27-28), Table IX | 6 `test` rows (FLEX-275 to FLEX-280, not in the PSI-69 table) | one test | `transcribed_from_table` (rendered page checked) | 0 g nominal |
| NTRS20170004702_limits.csv | NTRS 20170004702, Harper et al., "NASA-STD-6001B Test 1 ... Sample length impact on MOC" | PDF p.3-4, Table 2 (Table 1 for thickness) | 18 `limit` rows | ULOI and MOC for one material and sample length | `transcribed_from_table` | **1 g screening data, not microgravity** |

## Columns
`test_id, record_type (test | limit | series_summary), family, psi_id (empty here), platform, gravity_level_g, gravity_source (measured | nominal | assumed), material_or_fuel, material_class, sample_geometry, sample_thickness_mm, sample_width_cm, sample_length_cm, oxygen_fraction (0-1), oxygen_fraction_final, oxygen_orig, pressure_kpa, pressure_orig, diluent, flow_velocity_cm_s, flow_direction, spread_orientation, ignition_method, uloi_vol_pct, moc_vol_pct, o2_margin_vs_1g_pct, limit_criterion, outcome_raw, outcome_class, spread_rate (mm/s), spread_rate_basis, burn_duration_s, data_origin, source_ref, quality_flags, notes`. Definitions are in the data dictionary.

## Things to know before using these files
- **Limit rows are not tests.** ULOI and MOC are thresholds from several tests; do not count them as tests in the gap map (see docs/GRAVITY_COVERAGE.md). The "limit" definitions differ between 1 g (Test 1: at least 5 replicates) and the drop-tower limits (MOC*/ULOI*: within a 5.18 s drop), flagged `limit_criterion_differs_from_1g`.
- `data_origin = transcribed_from_text` is a third value we added beyond the two named in D3, for numbers printed in prose or slide text. It needs team approval or merging into `transcribed_from_table`.
- Some values are unit conversions (psia to kPa x6.894757, atm to kPa x101.325, mil to mm x0.0254); flagged in `quality_flags`.
- Unreadable or absent values left empty: 20010059376 individual spread rates and flammability-chart points (overlapping symbols); LUCI sample lengths of rods, burn durations, the numeric lunar g; Table I lunar/0 g test counts; 20110008636 entries marked "testing in progress".
- 20170004702 Table 2: a row "15 cm / 25.6 / 22.0" is repeated at the top of PDF p.4 and was not counted twice.
- 20110008636 Table 2 footnote a makes the pressure of the PET/PEI chemical-igniter columns ambiguous (10.2 psia hot-wire GRC protocol vs 14.7 psia default); those pressures are left empty and flagged.
- The spread-rate-vs-G data in 20010059376 (Fig. 8-10) and the flammability charts (Fig. 6-7) exist only as figures; extracting them would need a digitising step with stated uncertainty (not done).
- NTRS rights: these reports are NASA determinations "public use permitted" or similar, not open licenses (see docs/THIRD_PARTY.md). Numeric tables are transcribed with citation; narrative text is not copied.

## Sidecars (`sidecars/`, not unified rows)
Support files read by the pipeline for the BASS-II rows (NTRS 20210011385): `bass2_observations.csv` (the Appendix A "Test observations and anomalies" text for 126 of 129 tests, extracted by `scripts/extract_bass2_observations.py`), `bass2_table5_1.csv` (Table 5.1, 20 tests, each line checked verbatim against the PDF text), `bass2_pressure_statements.csv` (31 tests with a stated "1 atm"). LLM outcome proposals are in `data/llm/`, human decisions in `data/review/` (decision D12).

## Gravity values
Decision D15: lunar tests without a printed value use 0.165 g (nominal, flag `gravity_nominal_0.165_decision_D15`); microgravity is 0 nominal. The CSVs are LF-only and stored byte-exact (`.gitattributes`).
