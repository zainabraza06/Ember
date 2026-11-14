# Outcome mapping (decisions D5, D10, D12, D13, D14, D22, D23)

Every test keeps its original label or text in `outcome_raw` and gets one `outcome_class` from exactly these values: `no_ignition | self_extinguished | burned_to_completion | externally_terminated | other | unknown`.

- **externally_terminated** = stopped by the operator, a flow cut-off, a hardware limit or a timeout while the flame was still burning. It is **censored**: it means "sustained at least until termination" and must never be used as an extinction or as a negative flammability label. Use it as a lower bound on burn duration.
- The rules are implemented in `pipeline/outcome.py` and `pipeline/psi.py`; the counts below are reproduced by the pipeline (`data/processed/build_report.json`) and fixed by `pipeline/expected_counts.json`, so any change in a rule or a source file must be reviewed (the build fails otherwise).
- LLM-proposed classes (BASS-II) are **never used until a person approves them** (D12). Until then `outcome_class = unknown` and the proposal sits in `outcome_class_proposed` with `outcome_proposal_confidence` and `outcome_review_status`.
- Items needing a person are listed in [REVIEW_QUEUE.md](REVIEW_QUEUE.md).

## FLEX (PSI-69 and tests 275-280 from NTRS 20150023456), decision D22 (reverses D11)
**The "Test end" label is the outcome label.** D11 (use only the extinction diameter) was a team error and is withdrawn. Mapping: **Extinction -> self_extinguished, Completion -> burned_to_completion, Disruption -> other.** `outcome_raw` = the label. The report also prints Test end for tests 275-280, so those six rows are labelled too (no `unknown` FLEX rows remain).

The visible flame extinction diameter (defined in the report legend, NTRS 20150023456, PDF p.25: droplet diameter when the visible flame went out, dash = no extinction) is used **only as a consistency check**. A positive diameter is expected with "Extinction"; a dash or zero with "Completion" or "Disruption". Rows where they disagree get the flag `diameter_label_disagree`, keep the label's class, and are all listed in [REVIEW_QUEUE.md](REVIEW_QUEUE.md) section 3.

Reasoning: the label is the experimenters' own record of how the test ended, while the diameter is a measurement that can be missing (not recorded) or can describe a transient visible-flame loss in a test that was then classed as a disruption or a completion. Overriding the label with a derived number would replace a stated outcome with an inference. 58 of 280 tests disagree: 27 labelled Extinction without a usable diameter, 20 Disruption and 11 Completion with a positive diameter (including FLEX-276, Completion with 0.91 mm).

| Test end | outcome_class | Rows |
|---|---|---|
| Extinction | self_extinguished | 191 |
| Completion | burned_to_completion | 28 |
| Disruption | other | 61 |

## CFI-G (PSI-159), decision D10 (333 populated rows: 179 Normal + 154 Inverse)
**Label confirmation (source recorded).** The PSI-159 record text and the ACME overview papers do not define the abbreviations. The experiment's thesis does: Minhyeng Kim, *Spherical Gas-Fueled Cool Diffusion Flames*, M.S. thesis, University of Maryland, 2022 (advisor P. B. Sunderland; the CFI-G investigator), https://api.drum.lib.umd.edu/server/api/core/bitstreams/278c77a3-6e86-4dc5-8413-c0381ebe74a9/content (PDF SHA-256 b01d986ee1e47ef8a91c5b92a37e63d1594cf4eb2c813b878d79ec5a8e7771e6):
- **FT = flow terminated**: Table 4.1 note c, "FT indicates flow terminated" (PDF p.33). The text on the same page: "A total of 280 hot diffusion flames were ignited ... 189 extinguished radiatively and the others extinguished when the flow was terminated, in some cases because the burner temperature reached its limit of 723 K"; PDF p.20: "Tests were terminated if the burner reached 723 K to prevent burner damage." So FT is a termination, hence `externally_terminated`. **Confirmed.**
- **SE = self-extinguished**: the PSI column header is "Self-ext or flow term". The thesis does not use the letters SE; it calls these flames "RE", radiatively extinguished (note b of the same table). **Decision D23: SE -> `self_extinguished` is confirmed by this thesis** (Kim 2022 is cited as the source; cite only, not redistributed). the counts agree closely (thesis 280 hot flames: 189 radiatively extinguished and 91 flow terminated; this table after the rules below: 277 hot-flame rows with 173 SE and 91 externally terminated, plus 8 "flash" rows and a few other cases).
- **TFP = thin filament pyrometry** (the thesis, p.11, and NTRS 20210021781: SiC fibers measure flame temperature). The Yes/No column probably says whether the fiber array was in use; that reading is not documented. It is metadata, not an outcome (`ext.tfp_raw`).
- **"flash"** (Hot ignition) and **"PCI-A..G"** (Cool flame?) are not mentioned in the thesis (0 hits) and stay undocumented. "Day" is a metadata column. None of these is an outcome (D10).

Rules, applied in order (`pipeline/outcome.py`):
1. Hot ignition = flash -> `unknown` (undocumented), flag `hot_ignition_value_flash_undocumented`.
2. SE -> `self_extinguished`, **unless** the comment says the burner temperature limit was hit or the flow was manually stopped (tests 21088 C1 and 21102A1) -> `externally_terminated`, flags `label_conflict_SE_vs_comment` and **`class_from_comment`** (consistent with the thesis: hitting the 723 K limit terminates a test).
3. FT -> `externally_terminated`. One row has Hot ignition = No with a positive burn time (21106 F4, comment "hot flame"): class stays `externally_terminated`, flag `label_conflict_hot_ignition_no_but_burn_time_positive`.
4. End state "-" with comment "direct cool - no hot ignition" (2 rows) -> `other`, flags `cool_flame_only`, `class_from_comment`. With comment "Aborted" (1 row, 21209 A2) -> `other`, flags `aborted_comment`, `class_from_comment`.
5. End state "-", Hot ignition = No, burn time 0 -> `no_ignition`.
6. Anything else -> `unknown`.

| Normal / Inverse rows | outcome_class |
|---|---|
| SE, 100 / 73 | self_extinguished (173) |
| FT 30 / 58, plus SE with a termination comment 2 / 0, plus the hot=No FT row 1 / 0 (counted in the 30) | externally_terminated (91) |
| "-", hot ignition No, burn time 0: 42 / 14 | no_ignition (56) |
| "direct cool" 2 / 0, "Aborted" 0 / 1 | other (3) |
| "flash" 0 / 8, "-" without a rule match 2 / 0 | unknown (10) |

The 5 `class_from_comment` rows (2 overrides of SE, 2 cool-flame-only, 1 aborted) are listed in REVIEW_QUEUE.md section 2. About 27% of CFI-G rows (91 of 333) are censored, so the envelope model must not treat them as extinctions.

## BASS-II (PSI-25), decision D12 (129 tests)
- The PSI-25 table has no outcome column. The outcomes are the free-text **"Test observations and anomalies"** of NTRS 20210011385 Appendix A (PDF p.111-121, Tables A.1-A.6), extracted for all 126 tests found there (`data/transcribed/sidecars/bass2_observations.csv`, by `scripts/extract_bass2_observations.py`). `outcome_raw` holds the original text. **O20, O21 and O22 are not in Appendix A: `outcome_raw` is empty, `outcome_class = unknown`.**
- **Proposals (LLM):** Claude (claude-sonnet-5-5) proposed a class for every test with a confidence and rationale (`data/llm/bass2_outcome_proposals.csv`, rubric in `data/llm/README.md`). Totals: self_extinguished 80 (30 high, 44 medium, 6 low), unknown 29 (18 high, 9 medium, 2 low), burned_to_completion 7 (4 high, 3 medium), externally_terminated 8 (4 high, 4 medium), no_ignition 5 (1 high, 2 medium, 2 low). 62 are medium and 10 low confidence.
- **Review:** all 126 observation-based proposals are in REVIEW_QUEUE.md section 1 (low confidence first). A person records a decision in `data/review/outcome_review.csv`; only `approved` or `changed` classes reach `outcome_class`. Currently 0 reviewed: all 129 BASS-II rows are `unknown`.
- **Flow (numeric only for Table 5.1):** `flow_velocity_cm_s` is filled only for the 20 tests of Table 5.1 (M1-M20, PDF p.65) that have a single velocity (M1, M5, M9, M15, M20); the other 15 have several velocity steps stored in `ext.flow_velocity_steps_cm_s` (flag `multiple_flow_steps`). Everywhere else the fan and air display codes stay raw.
- **Pressure:** only where the report text states it: "1 atm" for B3, B4, B11, B13 (PDF p.49) and for the 27 T'ien SIBAL tests (PDF p.102): 101.325 kPa, flag `nominal`, field origin `transcribed_from_text`. Others empty (REVIEW_QUEUE.md section 5 lists statements whose scope is unclear).

## BASS (PSI-26), decision D13
Removed from the structured test table (it has only date, test numbers and material). It will be used in the evidence ledger (M3). Its 122 rows no longer appear in `tests.csv`.

## Saffire I-III (PSI-98, 99, 100), decision D14
| Table | Raw outcome fields | Mapping |
|---|---|---|
| PSI-98 (S1, S2) | Burn Time 420, 70 | `unknown` (end state not in the table; flag `end_state_not_in_table`) |
| PSI-99 rows 2-1 to 2-4 | Burn Time "Insignificant" | `unknown`; **burn_duration_s empty, the word stays in `outcome_raw`** |
| PSI-99 2-5, 2-6 | microgravity burn length "29 cm" equals the sample length | `burned_to_completion` (flag `rule_burn_length_equals_sample_length`, `outcome_class_provisional`) |
| PSI-99 2-7 (PMMA and Nomex on one card) | table note 2 | two rows: `PSI-99:2-7-PMMA` burned_to_completion, `PSI-99:2-7-Nomex` no_ignition |
| PSI-99 2-8, 2-9 | burn length "~ 10 cm", note 4 | `unknown` |
| PSI-99 1 g columns | "1-g Burn Length", "1-g Spread Rate" | **separate rows** `PSI-99:<sample>:1g` at 1 g, linked to the microgravity row by `pair_id` (9 pairs). "Complete" -> burned_to_completion (6 rows); "7.6 cm", "~ 0" -> unknown. The 1 g spread rate (1.2 and 0.6 mm/s) goes to `spread_rate`; "Acceleratory" stays in `outcome_raw` |
| PSI-99 "?-g Spread Length" values in mm/s | 2.1 and 2.6 mm/s (2-5, 2-6) | **header corrected** (flag `header_corrected`): NTRS 20170008805 slide 29 names the column "?-g Spread Rate", so the values go to `spread_rate` |
| PSI-100 (S1, S2) | none | `unknown` |

## Transcribed reports (data/transcribed)
Limit rows (ULOI/MOC) have no per-test outcome: `unknown`. Text statements in NTRS 20010059376 and the LUCI burns carry classes (burned_to_completion 1, self_extinguished 5, rest unknown).

## Totals in the harmonized table (885 rows)
| Family | self_extinguished | burned_to_completion | externally_terminated | no_ignition | other | unknown |
|---|---|---|---|---|---|---|
| FLEX (280) | 191 | 28 | 0 | 0 | 61 | 0 |
| CFI-G (333) | 173 | 0 | 91 | 56 | 3 | 10 |
| BASS-II (129) | 0 | 0 | 0 | 0 | 0 | 129 |
| Saffire (23) | 0 | 9 | 0 | 1 | 0 | 13 |
| partial-gravity literature (29) | 5 | 1 | 0 | 0 | 0 | 23 |
| 1 g screening (91) | 0 | 0 | 0 | 0 | 0 | 91 |
| **All (885)** | **369** | **38** | **91** | **57** | **64** | **266** |

## Still needing a person
1. Approve, change or reject the 126 BASS-II proposals (REVIEW_QUEUE.md section 1).
2. Decide whether the 5 CFI-G `class_from_comment` rows stand; look at the 58 FLEX label/diameter disagreements (REVIEW_QUEUE.md section 3).
3. The "?-g" glyph in the Saffire column names (presumably the micro sign) and the end states for Saffire I and III.
4. How the envelope model treats `externally_terminated` rows (recommended: censored observations, not labels).
