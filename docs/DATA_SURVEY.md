# M1 data survey: NASA microgravity combustion data

Retrieved 2026-10-18 to 2026-10-19. This file replaces the earlier metadata-only draft. Row-level detail with a source URL on every row is in [../data/catalog.csv](../data/catalog.csv) (93 rows). Per-investigation notes and the downloaded files are under `data/raw/` (`psi/<PSI-ID>/info.md`).

**What was and was not downloaded.** Downloaded: the 22 experiment-table CSVs from the 20 PSI investigations that have one (about 210 KB), the 24 PSI metadata records (JSON), and 2 small NTRS reports with per-material result tables. Not downloaded: any video, image, zip archive or full-size report. Some PDFs (about 50, under 20 MB each) were read into a temporary folder outside the repo only to scan for table captions; they were not kept. Two key reports (FLEX detailed results 42.9 MB; BASS-II summary 49 MB) were over the 20 MB limit and were not downloaded in M1; **they were downloaded in M2 under team decision D2** (see docs/STATUS.md and data/raw/ntrs/<id>/info.md).

## 1. Sources and method
| Source | How it was surveyed | URL |
|---|---|---|
| PSI repository | Read-only calls to the site's own endpoints: search (`.../geode-py/ws/repo/search`), investigation record (`.../repo/investigations/<ID>`), and the site's file route (`.../studies/<ID>/download?file=<name>&redirect=false`, which returns a pre-signed link). No robots.txt exists on psi.nasa.gov (404). The file-listing endpoint returns 403 and was not pursued. These endpoints are undocumented and may change. | https://psi.nasa.gov/physci/repo/search?q=&data_source=psi&data_type=investigation |
| PSI user guide | Read | https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/Complete_PSI_Database_Guide.pdf |
| NTRS | Public API (robots.txt allows crawling: https://ntrs.nasa.gov/robots.txt); several hundred title-match queries and about 50 topic searches; records and PDF sizes for 56 shortlisted reports | https://ntrs.nasa.gov/api/citations/search |
| NASA Glenn combustion pages | Fetched | https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/ |
| NASA Task Book | Welcome page loads; search not run | https://taskbook.nasaprs.com/tbp/welcome.cfm |
| JAXA | Leaflet, one DARTS dataset page; two search summaries | https://humans-in-space.jaxa.jp/2026/07/Leaflet_CombustionExperimentInMicrogravity.pdf |
| NASA-STD-6001, NASA/TP-2010-216134 | Located, PDFs checked for identity (temporary copies) | see section 6 |

## 2. Overview
- **PSI:** 133 investigations in total; **24 Combustion Science** (19 microgravity flight, 5 ground analysis: PSI-60, 62, 115, 117, 142). 20 have an experimental-table CSV (22 files); PSI-60, 62, 115, 117 have none. About 13.5 TB in total, mostly zip archives and video (see catalog `media_size`). 23 records state CC0-1.0; **PSI-10's license field is empty (unknown)**.
- **Platforms (PSI):** ISS (Combustion Integrated Rack/ACME, MDCA droplet apparatus, Microgravity Science Glovebox) and Cygnus (Saffire). No Space Shuttle, Mir, drop-tower or parabolic-flight investigation appears in the 24 (PSI-10's approach text mentions drop towers).
- **NTRS:** 56 reports catalogued, plus the two standards documents. Rights fields are NASA determinations (for example "public use permitted"), **not open licenses**.
- **Glenn / others:** three current projects not in PSI: FM2 (lunar surface), SoFIE (ISS), FLARE (JAXA Kibo). Eight archived projects are linked on the Glenn page.

By family (PSI tests counted from the downloaded tables; rows are what the tables contain, not what PSI states):
| Family | Investigations | Table rows (approx tests) |
|---|---|---|
| FLEX / droplets | PSI-69 FLEX, PSI-68 FLEX-2, PSI-39 CFI | 274; 8 fuel rows (matrix, not per test); 87 |
| ACME gas flames | PSI-10 Flame Design, PSI-159 CFI-G, PSI-20 BRE, PSI-21 CLD, PSI-22 E-FIELD, PSI-23 s-Flame | 327; 333 (179 + 154); and four per-day summaries (18-32 rows each) |
| BASS | PSI-25 BASS-II, PSI-26 BASS | 129; 122 |
| Saffire | PSI-98 / 99 / 100 | 2; 9; 2 samples |
| SPICE / SLICE | PSI-107, PSI-106 | 469 (435 distinct); 12 |
| SAME / DAFT | PSI-102, 101, 47 | 8; 109; 2 |
| Ground analysis | PSI-60, 62, 115, 117, 142 | none, except PSI-142 (index of 8 figures) |

## 3. Coverage table (per-test columns actually present in the downloaded tables)
O2/pressure/flow count only if a per-test column exists. Gravity is microgravity everywhere unless stated.

| Family (PSI) | O2 | Pressure | Flow | Gravity levels in table | Outcome columns |
|---|---|---|---|---|---|
| FLEX (69) | yes (mole fraction 0.12-0.34) | yes (mmHg; 526-2320, one 0.0 entry) | no (droplets quiescent) | 1 (micro) | extinction diameter, burning rate, burn time, test end class: Extinction 186 / Disruption 61 / Completion 27 |
| FLEX-2 (68) | range 0.17-0.30 | range 0.5-3.0 atm | range 0.1-5 cm/s | 1 | none (matrix only) |
| CFI (39) | yes (0.17, 0.21) | yes (0.5-5 atm, text) | no | 1 | none |
| CFI-G (159) | yes (0.18-0.40 normal; 0.12-0.85 inverse) | yes (about 0.5-3.3 bar) | mass flows only | 1 | cool flame?, hot ignition, burn time, self-extinguished vs flow-terminated, peak temperature, color |
| Flame Design (10) | yes | yes (0.43-3.02 atm) | mass flows only | 1 | none |
| BRE (20) | O2 % listed per day | not in table (notes say varied) | no | 1 | flames ignited per day |
| BASS-II (25) | initial/final O2 (13.6-22.2%) | no | instrument codes only | 1 | none (CO2/CO final values) |
| BASS (26) | no | no | no | 1 | none |
| Saffire I-III (98-100) | O2 % (98, 99) | no | yes (20 / 30 cm/s) | micro; **PSI-99 also has 1-g burn length and 1-g spread rate columns** | burn time; burn and spread length (99) |
| SPICE (107) | no | no | yes (air rate, cm/s) | 1 | ignition and flame-off times |
| SAME-R / SAME (101, 102) | no | no | yes (inlet velocity / air flow) | 1 | smoke particle size ratio, weight-loss rate |

## 4. Gravity coverage (partial gravity: Moon about 0.16 g, Mars about 0.38 g)
**Inside PSI (24 investigations): no table contains a partial-gravity test.** Every flight investigation is microgravity. Earth-gravity comparison exists in PSI-99 (1-g columns) and in "Earth gravity" data folders described in the PSI guide; several publication titles in PSI-106/107 mention gravity effects (for example "Effects of Fuel Dilution and Gravity" and "Scaling of Gas-Jet Flame Lengths in Elevated Gravity"), but their data were not examined.

**Outside PSI (literature and projects found; none has a machine-readable test table yet):**
| Item | What it reports (from the NTRS abstract or NASA page) | Link |
|---|---|---|
| Upward flame spread over thin solids in partial gravity (2001) | Thin cellulose fuel, 0.2-0.4 atm air, **0.1 g, 0.16 g (lunar), 0.38 g (Martian)** on NASA KC-135 plus normal gravity; widths 1, 2, 4 cm | https://ntrs.nasa.gov/citations/20010059376 |
| Downward flame spread in variable gravity: lunar and Martian simulation (1993) | Thin cellulosic fuel, normal pressure, 21% O2 and below, 0.05-0.6 g on research aircraft | https://ntrs.nasa.gov/citations/19930040901 |
| Evaluating material flammability in microgravity and Martian gravity (2012) | Drop-tower tests at Martian gravity, three materials; flammability limits in different gravity and flow environments are tabulated per the abstract | https://ntrs.nasa.gov/citations/20130010991 |
| Lunar Combustion Investigation (LUCI), 2025 presentation | Rotating suborbital rocket gives lunar gravity; tests longer than 25 s; two samples in air at normal pressure | https://ntrs.nasa.gov/citations/20250010653 |
| Material flammability at lunar and Martian gravity (2026 abstract and slides) | Abstract text is empty in NTRS; the slides contain one table, which is the 1-g Test 1 sample-length study, so lunar/Martian results appear only in figures (not examined) | https://ntrs.nasa.gov/citations/20260000646 ; https://ntrs.nasa.gov/citations/20260001966 |
| FM2: Flammability of Materials on the Moon | Planned lunar-surface experiment, 1/6 g, four samples; no results or launch date stated | https://www.nasa.gov/flammability-of-materials-on-the-moon-fm2/ |
| FLARE (NASA/JAXA) and JAXA FLARE-2/-3 | ISS Kibo; JAXA leaflet lists FLARE-2/-3 as planned demonstrations for lunar-like low gravity | https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-limits-at-reduced-g-experiment-flare/ |

**Conclusion:** structured partial-gravity data are essentially absent from the PSI tables. Partial-gravity evidence exists only as a small set of reports (thin cellulose mostly), and the numbers must be transcribed manually from those reports if we want them. The gap map should show this clearly.

**Exploration atmospheres (reduced pressure with elevated O2, e.g. 8.2 psia/34% O2 and 10.2 psia/26.5% O2).** The reference definition is NASA/TP-2010-216134 (section 6).
- PSI-20 (BRE) objectives name these atmospheres, and its table lists O2 of 21, 26.5, 34, 40%, but pressure per test is not in the table.
- FLEX (PSI-69): no test near 8.2 psia/34% (our window: 380-470 mmHg and O2 0.31-0.36 gives 0 rows); 16 rows fall in a window around 10.2 psia/26.5% (480-570 mmHg, O2 0.24-0.29). These windows are ours and approximate; the unit mmHg is taken from the column header.
- CFI-G (PSI-159): 48 tests with pressure below 0.8 bar and O2 at or above 0.26 (gas fuels, cool-flame science), of which none are solid materials.
- Little else. Solid-material tests at reduced pressure and elevated O2 are not in any downloaded table.

## 5. Fire detection and suppression sources
| Source | Content | Link |
|---|---|---|
| SAME (PSI-102), SAME-R (PSI-101), DAFT (PSI-47) | Smoke particle size and morphology in microgravity, instrument feasibility; PSI-101 has 109 test rows; materials Kapton, silicone, lampwick, Pyrell, Teflon | catalog |
| FLEX suppressant tests (PSI-69) | CO2, He, SF6 as diluents in droplet extinction (objectives text) | catalog |
| Fire Prevention, Detection and Suppression project final report (NASA/TM-2011-217036) | 81 pages, project summary | https://ntrs.nasa.gov/citations/20110020262 |
| Smoke detection in low-g fires (1995); SMOKE particulate characterization (2001); Smoke particle size results (SAME-2, 2012) | Detection science | https://ntrs.nasa.gov/citations/19960008413 ; .../20010074094 ; .../20130000422 |
| CO2 suppression of PMMA flames in low gravity (2003); fire suppression in extraterrestrial environments (2001) | Suppression | https://ntrs.nasa.gov/citations/20040053586 ; .../20010074098 |
| Saffire combustion-product measurements | Heat and smoke emission from Saffire VI tests (2026) | https://ntrs.nasa.gov/citations/20260001992 |

## 6. Reports, standards, and other sources
**NASA-STD-6001B w/Change 3** (Test 1, upward flame propagation, appears on PDF pages 5, 18, 27, 29): free public download, 2.25 MB, document date 2011-08-26, change 2025-06-09, status active. https://standards.nasa.gov/standard/nasa/nasa-std-6001 . An older interim revision is in NTRS: https://ntrs.nasa.gov/citations/20110012152 .

**NASA/TP-2010-216134** (exploration atmospheres, October 2010, 178 pages, title page checked): not found in NTRS by title or number; hosted at https://www.nasa.gov/wp-content/uploads/2023/03/henninger-8.2-34-atm-tp216134-2010.pdf (2.2 MB). Related errata memo: https://ntrs.nasa.gov/citations/20130013505 .

**Main results reports by family** (full list in catalog):
| Family | Reports found |
|---|---|
| BASS / BASS-II | BASS-II Summary Report https://ntrs.nasa.gov/citations/20210011385 (49 MB, not opened); results presentation .../20160000593; PMMA rods .../20150008961 |
| FLEX | Detailed Results from FLEX, March 2009 to December 2011 https://ntrs.nasa.gov/citations/20150023456 (42.9 MB, not opened); methanol droplets .../20130014061 |
| FLEX-2 / CFI | No final report found. Related cool-flame papers: .../20140006750, .../20190002838, .../20160000344 |
| Saffire | Status papers .../20170000230, .../20170001636; results presentation .../20170008805; Saffire IV/V implications .../20210011521; Saffire VI .../20240002981, .../20260001992. Saffire IV-VI are not PSI Combustion investigations |
| ACME | Overview paper .../20210021781; BRE .../20160010073, .../20170009141; sooting limits .../20020027073 |
| SAME / SPICE / SLICE | SAME-2 .../20130000422; SLICE-related coflow papers .../20150002322, .../20150011070. No SPICE report found by title |
| Test 1 / 1-g thresholds | Sample-length study .../20170004702 (kept in data/raw); parametric effects on flammability limits .../20110008636 (kept in data/raw) |

**NASA Glenn and Task Book.** FM2, SoFIE, FLARE are listed as current; ACME, BASS, DAFT, FLEX, Saffire, SAME, SLICE, SPICE as archived (eight overview PDFs linked, not read). SoFIE's page says Active Mission (updated 2025-09-04 per our fetch) with five investigations (RTDFS, NCA, GEL, MIST, SMuRF) and O2 up to 85%; no data location is stated. The Task Book welcome page loads without login; the search was not run.

**Partners.** All marked "pending official challenge resource list". JAXA: Solid Combustion/FLARE (Kibo; wire insulation, thin PMMA, filter paper per a search summary; results not found), a public DARTS dataset for the Group Combustion experiment (droplet clouds, low relevance), the JAXA leaflet above. ESA, CSA: nothing found. JAXA/ISAS data terms were not read.

## 7. Data quality notes and known problems
- **Header ambiguity:** FLEX columns `O` and `CO` presumably mean O2 and CO2 (not confirmed); units come only from headers (mmHg, mm, s).
- **FLEX:** one pressure entry is 0.0; one duplicated test identifier; extinction diameter numeric in 197 of 274 rows.
- **CFI-G inverse table:** 861 of 1015 rows are completely empty.
- **SPICE:** 34 duplicated rows (469 rows, 435 distinct); inconsistent fuel labels; "GMT date" is a day number.
- **BASS-II:** flow is only instrument codes (fan, restrictor), so velocity is not recoverable from the table. **BASS:** only date, test number and material (names inconsistent).
- **Per-day summaries (BRE, CLD, E-FIELD, s-Flame):** counts of flames per day, not individual tests; typos such as "CH5", "N3".
- **Saffire-II table:** garbled header characters, mixed units in cells ("20 cm/s", "80 W"), two samples with blank material; quality notes in footnotes.
- **FLEX-2 and PSI-142** are matrices/indexes, not per-test.
- **Version history:** several records list thousands of "removed" files (for example 6,814 for PSI-23). Why they were removed is not stated.
- **Files not seen:** each record's file list is incomplete (zero or one file for 7 investigations). Per-run CSVs exist for some (PSI-10: 636 CSV files; PSI-159: 680; PSI-23: 576) but were not inspected.
- **Media:** dominated by zip archives (contents unknown) and video.

## 8. Recommendation: families for the structured test table
**Scoring (0-3 each; five criteria from the M1 brief).** Rubric, applied by us from the downloaded tables: **a** table quality (3 = clean per-test numeric CSV with more than 100 rows; 2 = per-test but partial or messy; 1 = summaries or tiny; 0 = none); **b** tests (3 = 250 or more; 2 = 100-249; 1 = 10-99; 0 = under 10); **c** relevance to Moon/Mars cabins (3 = spacecraft solid materials or cabin-scale fire; 2 = O2/pressure limits or suppression, other fuels; 1 = fundamental gas/droplet science; 0 = none); **d** count of O2, pressure, flow present per test (gravity is excluded because it is constant); **e** outcome labels (3 = explicit classes; 2 = quantitative outcome only; 1 = weak; 0 = none).

| Family | a | b | c | d | e | Total (max 15) |
|---|---|---|---|---|---|---|
| **FLEX (PSI-69)** | 3 | 3 | 2 | 2 | 3 | **13** |
| **CFI-G (PSI-159)** | 2 | 3 | 1 | 2 | 3 | **11** |
| **BASS-II (PSI-25)** (+ BASS PSI-26 as supplementary) | 2 | 2 | 3 | 1 | 1 | **9** |
| **Saffire I-III (PSI-98/99/100)** | 2 | 0 | 3 | 2 | 2 | **9** |
| SPICE (PSI-107) | 3 | 3 | 1 | 1 | 1 | 9 |
| ACME Flame Design (PSI-10) | 2 | 3 | 1 | 2 | 0 | 8 |
| ACME BRE (PSI-20) | 1 | 1 | 3 | 1 | 1 | 7 |
| CFI (PSI-39) | 2 | 2 | 1 | 2 | 0 | 7 |
| FLEX-2 (PSI-68) | 1 | 0 | 2 | 3 | 0 | 6 |
| BASS (PSI-26) alone | 1 | 2 | 3 | 0 | 0 | 6 |

**Recommended (4 families):**
1. **FLEX (PSI-69), with FLEX-2 conditions as context.** Best table: 274 tests with O2, pressure, diluent, and labelled test-end classes. Direct evidence on how oxygen and pressure set extinction, plus suppressants. Limits: liquid droplets, no flow axis.
2. **CFI-G (PSI-159).** 333 populated tests with hot-ignition, self-extinguished vs flow-terminated labels over a wide O2 and pressure range. Gas fuels, so useful for the O2 x pressure envelope shape rather than for materials.
3. **BASS-II (PSI-25), BASS (PSI-26) as supplement.** Solid spacecraft-relevant materials (PMMA, SIBAL, Nomex) with O2 per test, tied to the NASA Test 1 comparison. Weak table: flow only as codes, no outcome column, so outcomes will have to come from reports (the BASS-II summary report is the likely source).
4. **Saffire I-III (PSI-98/99/100).** Only 13 samples but the most cabin-relevant tests, with flow, direction, burn time and (Saffire-II) 1-g comparison columns. Hand-curate these rows; also feed the ledger.

**Rejected or deferred:**
- **SPICE (107):** large clean table but only flow; no O2, pressure or outcome class; smoke-point science. Keep for the ledger (smoke) not the model.
- **ACME Flame Design (10):** 327 conditions over wide pressure but no outcome column, and a license field that is empty (unknown). Not usable until the license is resolved.
- **ACME BRE (20):** the exploration-atmosphere link is attractive, but the table is per-day counts with no pressure column. Use the objectives/papers in the ledger.
- **CFI (39), FLEX-2 (68):** conditions only, no outcome; FLEX-2 is a matrix. Use as context for FLEX.
- **CLD, E-FIELD, s-Flame (21-23), SLICE (106), SAME/DAFT (101, 102, 47), ground studies:** summaries or non-flammability science.

No fifth family is recommended: the next candidates add rows but no outcome labels or relevance. **Caveat:** the "partial gravity" axis cannot be covered by any recommended family; it requires manual transcription from the reports in section 4.

## 9. Reports best suited for the Evidence Ledger (M3)
1. Partial gravity: 20010059376, 19930040901, 20130010991, 20250010653, 20260001966 (slides; lunar/Martian results in figures, not examined), 20210020516, 20240008623.
2. 1-g and Test 1 comparisons: 20170004702, 20110008636 (both kept in data/raw, tables of oxygen thresholds per material), NASA-STD-6001B.
3. Saffire: 20170001636, 20170000230, 20170008805, 20210011521, 20240002981, 20260001992.
4. FLEX and suppression: 20150023456 (downloaded in M2; 42.9 MB), 20130014061, 20040053586, 20010074098.
5. BASS: 20210011385 (downloaded in M2; 49 MB), 20160000593, 20150008961, 20170006615, 20140011099.
6. Atmospheres: TP-2010-216134, 20130013505 (errata), 20260002050 (2026 surface vehicle atmospheres).
7. Detection: 20110020262, 20130000422, 20010074094, 19960008413.

NTRS rights determinations are NASA's, not open licenses; for the product we should cite and paraphrase, and review any document marked "may include copyright material" (for example 20210011521, 20240002981, 20260001992, 20260002050) before quoting spans.

## 10. Open questions (need a person)
1. ~~Download the two over-size reports~~ Done in M2: both contain per-test tables (FLEX Table IX; BASS-II Appendix A).
2. Is the PSI-10 license CC0? Contact PSI or check the page "Cite this Investigation".
3. Read the Task Book terms and run a search for combustion/fire projects; read JAXA/ISAS data terms.
4. PSI file lists are incomplete: check the per-run CSV/xlsx files (PSI-10, 23, 159, 98-100 and SAME) for outcomes missing from the summary tables.
5. Confirm the FLEX pressure unit (mmHg) and the `CO` column meaning from the FLEX report.
6. Partner resources are pending the official challenge page.
