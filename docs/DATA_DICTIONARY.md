# Data dictionary: unified test table (M2) — v3 (matches the pipeline)

The pipeline in `pipeline/` implements this document and writes `data/processed/tests.csv` and `tests.parquet` (section 8). Column meanings come from the PSI CSV headers and the NASA reports cited per field; nothing else. Team decisions D1-D16 are recorded in [STATUS.md](STATUS.md). Scope: **FLEX (PSI-69), CFI-G (PSI-159), BASS-II (PSI-25), Saffire I-III (PSI-98/99/100)**, plus tests 275-280 of the FLEX report and the transcribed partial-gravity and 1 g screening reports. **Excluded:** PSI-10 (D6, license unknown) and BASS PSI-26 (D13: evidence ledger only).

## 1. Conventions
- **Entities (`record_type`):** `test` (one run or table row), `limit` (a threshold such as ULOI/MOC derived from several runs), `series_summary` (a plotted curve whose points are not available). Limits and series are not tests and must not be counted as tests.
- **Units.** Gravity in g0 = 9.80665 m/s². Pressure in kPa (mmHg x 101.325/760; bar x 100; atm x 101.325; psia x 6.894757). Oxygen as mole fraction 0-1 (vol% / 100). Flow in cm/s and spread rate in mm/s as the sources give them (SI: x0.01 and x0.001). The original cell text is kept next to every converted value in `orig_values`.
- **Gravity (D15).** Microgravity rows (ISS, Cygnus) use `gravity_level_g = 0` with `gravity_source = nominal` (the investigations are microgravity; no source states a measured residual acceleration). Lunar tests without a printed value use `0.165` (nominal, flag `gravity_nominal_0.165_decision_D15`). Martian 0.38 is printed in the source. `measured` is never used (no per-test measurement is tabulated).
- **Missing data.** Empty cell = not given or not readable; flag `missing_value:<field>`. The FLEX report prints "?"; the PSI CSVs leave blanks. Never replaced by 0.
- **Field origins.** Row-level `data_origin` says where the row comes from. A field filled from a report into a PSI row carries its own origin inside `orig_values` (`origin = transcribed_from_text` or `transcribed_from_table`, plus `source`): BASS-II pressure and Table 5.1 flow.
- **Ids.** FLEX `PSI-69:001`; report-only FLEX tests `NTRS20150023456:FLEX-275`; CFI-G `PSI-159:normal:21088A1`; BASS-II `PSI-25:B1`; Saffire `PSI-98:S1`, `PSI-99:2-1`, `PSI-100:S1`; the Saffire-II card 2-7 becomes `PSI-99:2-7-PMMA` and `PSI-99:2-7-Nomex`; 1 g comparison rows `PSI-99:2-1:1g`. `pair_id` joins a microgravity row to its 1 g row.
- **`source_ref`.** PSI rows: `<csv path>#data_row=<N>` (N counts all data records after the header, empty ones included; spreadsheet row = N + 1). Transcribed rows: the report citation (report, PDF page, table, figure or slide), then ` | <transcribed csv>#data_row=<N>`.
- **Dropped:** 861 empty rows of the CFI-G Inverse file; flow-visualization and footnote rows of the Saffire tables.

## 2. Unified schema
Required: **R** always populated; **C** populated whenever the source gives it (else empty plus a flag); **O** optional. All schema additions were approved in D9.

| Field | Type | Unit | Allowed values | Req. | Description |
|---|---|---|---|---|---|
| test_id | string | | see Ids | R | Unique id. |
| record_type | enum | | test, limit, series_summary | R | |
| family | enum | | FLEX, CFI-G, BASS-II, BASS, Saffire, partial_gravity_literature, screening_1g | R | Experiment family (BASS is allowed by the schema but unused, D13). |
| psi_id | string | | PSI-25, PSI-69, PSI-98, PSI-99, PSI-100, PSI-159 or empty | R for PSI rows | Empty for report-only rows. |
| platform | string | | e.g. ISS-CIR/MDCA, ISS-CIR/ACME, ISS-MSG, Cygnus, KC-135, sounding rocket, lab 1 g | R | Free text; controlled list proposed. |
| gravity_level_g | float | g0 | 0, 0.10, 0.165, 0.38, 1, ... | C | See Gravity. Empty for plotted series. |
| gravity_source | enum | | measured, nominal, assumed | R | |
| material_or_fuel | string | | as written | R | Original name. |
| material_class | enum | | liquid_droplet, gas_fuel, solid_sheet, film, fabric, solid_rod, solid_sphere, foam, elastomer, laminate, other, unknown | R | |
| sample_geometry | string | | | C | Description. |
| sample_thickness_mm, sample_width_cm, sample_length_cm | float | mm, cm, cm | | O | |
| oxygen_fraction, oxygen_fraction_final | float | mole fraction | 0-1 | C | Initial and final ambient O2. |
| oxygen_orig, pressure_orig | string | | | O | Original text (ranges such as "21.5 - 21.7" are not collapsed). |
| pressure_kpa | float | kPa | | C | Total pressure; empty where only a bound or nothing is given. |
| diluent | string | | e.g. `N2=0.79;CO2=0;He=0` | C | |
| flow_velocity_cm_s | float | cm/s | | C | Imposed forced-flow velocity. Instrument codes are never entered here. |
| flow_direction | enum | | opposed, concurrent, quiescent, unknown | R | |
| spread_orientation | enum | | upward, downward, horizontal, not_applicable, unknown | O | |
| ignition_method | string | | | C | |
| uloi_vol_pct, moc_vol_pct, o2_margin_vs_1g_pct, limit_criterion | float, float, float, string | vol% O2 | | limit rows | Limits. |
| outcome_raw | string | | original label or text | C | Original outcome label or observation. |
| outcome_class | enum | | no_ignition, self_extinguished, burned_to_completion, externally_terminated, other, unknown | R | [OUTCOME_MAPPING.md](OUTCOME_MAPPING.md). |
| outcome_class_proposed | enum | | the six classes or empty | O | LLM proposal (BASS-II only, D12). Never used downstream. |
| outcome_proposal_confidence | enum | | high, medium, low, empty | O | |
| alt_value_report | string | | `<field>=<value> (<report ref>)` | O | The report's value where it conflicts with the primary table (D24); empty otherwise. |
| outcome_review_status | enum | | not_applicable, proposed, approved, rejected, changed, empty | O | Only approved or changed proposals set `outcome_class`. |
| spread_rate | float | mm/s | | C | Not applicable to droplets and spherical gas flames. |
| spread_rate_basis | enum | | flame_base, flame_tip, pyrolysis_front, regression, unknown | C | |
| burn_duration_s | float | s | | C | For `externally_terminated` it is a lower bound. |
| pair_id | string | | `PSI-99:<sample>` | O | Links a microgravity row to its 1 g comparison row (D14). |
| data_origin | enum | | psi_table, transcribed_from_table, read_from_figure, transcribed_from_text | R | `transcribed_from_text` approved in D9. |
| source_ref | string | | | R | Traceability. |
| quality_flags | string | | semicolon list, vocabulary in section 6 (a detail may follow a colon) | R | |
| orig_values | JSON | | `{field: {value, column, unit, origin?, source?, converted?}}` | R | **Original value next to every converted value.** |
| ext | JSON | | family-specific keys (section 3) | O | Fields as written in the source. |
| notes | string | | | O | Free text on transcribed rows. |

## 3. Per-family column mapping ("-" means no conversion)
### 3.1 FLEX (PSI-69 table, 274 rows) and report tests 275-280
| Original column | Unified field | Conversion / note |
|---|---|---|
| FLEX Test # | test_id | zero-padded. |
| Fuel | material_or_fuel; material_class = liquid_droplet | Methanol, Heptane. |
| Ambient pressure; mmHg | pressure_kpa | x 101.325/760; one entry is 0.0: empty plus `missing_value:pressure_kpa`. |
| O / N / CO / He initial ambient composition | oxygen_fraction; diluent | "O" is O2 and "CO" is CO2 (NTRS 20150023456 Table IX headings). |
| Visible flame extinction diameter; mm | `ext.extinction_diameter_mm` | consistency check only (D22): disagreement with Test end -> flag `diameter_label_disagree`. |
| Test end | `outcome_raw`, `outcome_class` | **the outcome label (D22)**: Extinction -> self_extinguished, Completion -> burned_to_completion, Disruption -> other. |
| Burn time; s | burn_duration_s | 8 rows missing. |
| Droplet initial diameter; mm; Burning rate; mm | `ext.droplet_initial_diameter_mm`, `ext.burning_rate_mm2_s` | the burning-rate header says mm; the report says mm2/s. |
| FLEX Identifier, Test Date, Test GMT | `ext` | |
| (none) | platform ISS-CIR/MDCA; gravity 0 nominal; flow_direction quiescent (flag `flow_direction_assumed_quiescent`) | |

Cannot fill: flow_velocity_cm_s; ignition_method; spread_rate (not applicable). Tests 275-280 exist only in NTRS 20150023456 Table IX (PDF p.33-34, rendered and checked).

### 3.2 CFI-G (PSI-159; Normal 179, Inverse 154 populated rows)
| Original column | Unified field | Conversion / note |
|---|---|---|
| Test | test_id | spaces removed. |
| Fuel | material_or_fuel; material_class = gas_fuel | mixtures as text ("30% butane"). |
| approx p (bar) | pressure_kpa | x 100; flag `approximate_value`. |
| XO2 before/after test (Normal); XO2 (Inverse) | oxygen_fraction, oxygen_fraction_final | Inverse has no final value. |
| burn time (sec) | burn_duration_s | |
| Self-ext or flow term; Hot ignition | `outcome_raw` = `end=<SE/FT/-> ; hot_ignition=<value>`; outcome_class | rules in OUTCOME_MAPPING.md (D10). |
| Comments | `ext.comments` | evidence for 5 comment-based classes (`class_from_comment`). |
| Day, Cool flame? (PCI-A..G), TFP | `ext.day_raw`, `ext.cool_flame_raw`, `ext.tfp_raw` | metadata, not outcomes (D10). TFP = thin filament pyrometry. |
| Xf, mHC / HC burnrate, O2 flow rate, Tad, Zst, Peak burner T, Color | `ext` | mass flows are not velocities. |

Cannot fill: flow_velocity_cm_s, flow_direction (spherical diffusion flame), diluent, ignition_method, spread_rate (not applicable).

### 3.3 BASS-II (PSI-25; 129 rows), decision D12
| Source | Unified field | Note |
|---|---|---|
| PSI-25 columns | test_id, material (free text normalized by `pipeline/materials.py`), oxygen_fraction / final (vol% / 100), `ext` (PI, GMT day, sample, flow restrictor, fan display, air display, radiometer gain, frames, CO2, CO) | flow codes stay raw. |
| Report Appendix A observations (`data/transcribed/sidecars/bass2_observations.csv`) | `outcome_raw` (original text) | O20-O22 absent: empty. |
| LLM proposals (`data/llm/bass2_outcome_proposals.csv`) and `data/review/outcome_review.csv` | `outcome_class_proposed`, `outcome_proposal_confidence`, `outcome_review_status`; `outcome_class` only after approval | 0 approved so far. |
| Report Table 5.1 (`sidecars/bass2_table5_1.csv`) | flow_velocity_cm_s for the 5 tests with one velocity; `ext.flow_velocity_steps_cm_s` for 15 with several; `ext.table_5_1` for all 20 | origin transcribed_from_table. |
| Report text "1 atm" (`sidecars/bass2_pressure_statements.csv`) | pressure_kpa = 101.325 for 31 tests | flag `nominal`; origin transcribed_from_text. |

Cannot fill: diluent, flow direction (the Appendix A word is not mapped), ignition_method, spread_rate and burn duration (Table 5.1 values stay in `ext`), pressure for 98 tests.

### 3.4 Saffire I-III (PSI-98: 2 samples; PSI-99: 9 samples; PSI-100: 2 samples), decision D14
| Original column | Unified field | Note |
|---|---|---|
| Sample Number | test_id | PSI-99 card 2-7 split into PMMA and Nomex rows. |
| Material; thickness / length / width | material_or_fuel; sample_*; units in the cell are respected | "037 mm" is not converted (flag `value_typo_suspected`; the report says 0.37 mm). PSI-98 length/width are swapped relative to the report (flag `length_width_swap_confirmed_by_report`; values kept). |
| Air Flow | flow_velocity_cm_s | PSI-99 sample 2-6: 20 in PSI, 25 in the report (flag `flow_conflicts_with_report`; PSI kept). |
| Percent O2 | oxygen_fraction when a single number; ranges stay in `oxygen_orig` | |
| Flow Direction / Direction | flow_direction | |
| Burn Time (s) | burn_duration_s; "Insignificant" stays in `outcome_raw`, burn_duration_s empty | |
| "?-g Spread Length" (PSI-99) | spread_rate (mm/s) | header corrected: the report calls it "?-g Spread Rate" (flag `header_corrected`). |
| "1-g Burn Length", "1-g Spread Rate" (PSI-99) | separate rows at gravity 1 with `pair_id` | 9 rows; flow not stated for these (flag `flow_not_stated_for_1g_test`). |

Cannot fill: pressure, diluent, ignition_method (name), outcome for PSI-98 and PSI-100.

### 3.5 Transcribed reports
Use the unified names directly (data/transcribed/README.md). The FLEX report rows follow section 3.1.

## 4. Fields each family cannot fill
Y from the table; D derived with a stated rule; R only from a named report row; A by assumption (flagged); N not available in any source read; X not applicable.

| Field | FLEX | CFI-G | BASS-II | Saffire I | Saffire II | Saffire III |
|---|---|---|---|---|---|---|
| gravity_level_g | D nominal | D nominal | D nominal | D nominal | D nominal | D nominal |
| material / class | Y/Y | Y/D | Y/D | Y/D | Y/D | Y/D |
| oxygen_fraction | Y | Y | Y | D (text) | D (text) | N |
| pressure_kpa | Y | D (approx) | R (31 of 129) | N | N | N |
| diluent | Y | N | N | N | N | N |
| flow_velocity_cm_s | N | N | R (5 of 129; 15 more as steps) | Y | Y | Y |
| flow_direction | A quiescent | N | N | Y | Y | Y |
| ignition_method | N | N | N | N | N | N |
| outcome_raw / outcome_class | Y / D | Y / D | R / proposed only | Y / N | Y / D | N / N |
| spread_rate | X | X | N | N | D (2 rows + 1 g) | N |
| burn_duration_s | Y | Y | N | Y | D | N |

## 5. Fields that exist only as codes, and what would decode them
| Code | Where | Decoding documentation |
|---|---|---|
| Flow restrictor, Fan display, Air display, Radiometer gain | PSI-25 | BASS-II hardware flow calibration; NTRS 20210011385 gives velocities only for Table 5.1 tests. One narrative (B21) pairs air display 5 with 5 cm/s, so air display is plausibly cm/s, but nothing defines it. |
| SE | PSI-159 | consistent with "radiatively extinguished" (UMD thesis, Kim 2022); the abbreviation itself is undefined |
| FT | PSI-159 | **defined**: flow terminated (same thesis, Table 4.1 note c) |
| flash, PCI-A..G, Day | PSI-159 | undocumented (metadata, not outcomes) |
| TFP | PSI-159 | thin filament pyrometry; the Yes/No meaning is inferred |
| Test end | PSI-69 | outcome label (D22) |
| "?-g" in Saffire headers | PSI-99 | the micro sign was lost (the report has the same glyph) |

## 6. Quality-flag vocabulary
All flag stems emitted by the pipeline or present in the transcribed files (a detail may follow a colon, e.g. `missing_value:pressure_kpa`), taken from `data/processed/build_report.json`:

`aborted_comment`, `approximate_value`, `class_from_comment`, `corrected_from_report`, `cool_flame_only`, `derived_from_two_material_card`, `duplicate_identifier`, `duplicate_of_table_2_chemical`, `duplicate_of_table_2_hotwire`, `end_state_not_in_table`, `flow_codes_undecoded`, `flow_direction_assumed_quiescent`, `flow_not_stated_for_1g_test`, `geometry_assumed_same_as_flight`, `gravity_changed_during_test`, `gravity_nominal_0.165_decision_D15`, `gravity_nominal_microgravity`, `header_corrected`, `hot_ignition_value_flash_undocumented`, `ignition_not_stated`, `insignificant_burn_meaning_undocumented`, `label_conflict_SE_vs_comment`, `label_conflict_hot_ignition_no_but_burn_time_positive`, `limit_criterion_differs_from_1g`, `material_dimension_meaning_unclear`, `material_not_stated`, `material_shape_not_stated`, `material_wax_material`, `material_width_assumed_from_position`, `missing_value`, `multiple_flow_steps`, `nominal`, `not_in_psi_69_table`, `o2_final_differs_from_initial_by_more_than_3pct`, `orientation_from_slide_16`, `outcome_class_from_1g_burn_length_complete`, `outcome_class_judgement`, `outcome_class_provisional`, `outcome_from_table_note_2`, `outcome_not_in_appendix_a`, `outcome_not_in_table`, `outcome_not_stated`, `oxygen_approximate`, `pair_row_of_microgravity_test`, `pressure_ambiguous`, `pressure_from_figure_legend`, `pressure_in_table_in_psia`, `pressure_is_bound_not_value`, `pressure_is_range_not_value`, `pressure_unit_converted_psia_to_kpa`, `rule_burn_length_equals_sample_length`, `series_not_individual_tests`, `size_split_by_position_in_cell`, `spread_rate_not_readable`, `diameter_label_disagree`, `text_in_discussion_of_Fig6`, `text_not_numeric`, `text_range_not_parsed`, `thickness_from_table_1_nominal`, `thickness_unit_converted_in_to_mm`, `thickness_unit_converted_mil_to_mm`, `source_conflict`, `value_typo_suspected`, `width_unit_converted_in_to_cm`.

`nominal` marks a value taken from a report statement as a nominal figure (BASS-II "1 atm"). `class_from_comment` marks an outcome class decided by a comment text (5 CFI-G rows).

## 7. Open decisions
1. (Closed by D24.) Saffire report-vs-PSI: clear errors are corrected and flagged `corrected_from_report` (thickness 0.37 mm, PSI-98 length/width, two blank materials); the genuine flow conflict of sample 2-6 keeps the PSI value (20 cm/s) with the report value in `alt_value_report` and the flag `source_conflict` (CONFLICTS.md). `orig_values` entries of corrected fields carry `corrected_value`, `origin` and `source`.
2. Whether the Appendix A flow-direction words (Opposed, Concurrent, Stagnation) may fill `flow_direction` for BASS-II.
3. Controlled vocabularies for platform and material normalization tables.

## 8. Implementation
`pip install -r requirements.txt` (pyarrow, Apache-2.0), then from the repository root: **`python -m pipeline`** rebuilds `data/processed/tests.csv`, `tests.parquet` and `build_report.json` from `data/raw/psi/**` (the table CSVs), `data/transcribed/**` (including `sidecars/`), `data/llm/` and `data/review/`. The CSV and report are deterministic (byte-identical on rebuild; the report stores SHA-256 hashes of every input CSV).

Automated checks run on every build and stop it with exit status 1, writing nothing, if any fails (`pipeline/checks.py`): allowed values and numeric parsing; plausible ranges per field and per family (unit sanity); unique `test_id`; no empty `source_ref`; `pair_id` integrity; LLM proposals cannot set an outcome class without an approved review; and exact row counts per family and per outcome class against `pipeline/expected_counts.json` (a change must be reviewed, then `python -m pipeline --write-expected`).

| Family | Source rows | Output rows | Notes |
|---|---|---|---|
| FLEX | 274 + 6 report tests | 280 | |
| CFI-G | 179 + 1015 | 333 | 861 empty rows dropped |
| BASS-II | 129 | 129 | |
| Saffire | 2 + 9 + 2 samples | 23 | 14 microgravity rows (card 2-7 split) + 9 one-g rows |
| partial-gravity literature | 29 transcribed | 29 | |
| 1 g screening | 91 transcribed | 91 | |
| **Total** | | **885** | |

Other commands: `python -m unittest discover -s tests -t .` (26 tests); `python -m pipeline.spot_check` (results in [SPOT_CHECK.md](SPOT_CHECK.md)); `python scripts/make_review_queue.py` (REVIEW_QUEUE.md); `python scripts/make_human_spot_check.py` (HUMAN_SPOT_CHECK.md).
