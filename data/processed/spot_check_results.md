# Spot check results (seed 20261019, simple random, 20 rows of 885)

| # | test_id | family | data_origin | checks passed | checks failed |
|---|---|---|---|---|---|
| 1 | PSI-159:normal:21291C1 | CFI-G | psi_table | 11 | 0 |
| 2 | PSI-159:inverse:21216H2 | CFI-G | psi_table | 9 | 0 |
| 3 | PSI-25:T7 | BASS-II | psi_table | 8 | 0 |
| 4 | PSI-69:118 | FLEX | psi_table | 11 | 0 |
| 5 | PSI-69:212 | FLEX | psi_table | 11 | 0 |
| 6 | PSI-159:normal:21112A4 | CFI-G | psi_table | 11 | 0 |
| 7 | PSI-159:normal:21137A7 | CFI-G | psi_table | 11 | 0 |
| 8 | PSI-159:inverse:21202A4 | CFI-G | psi_table | 9 | 0 |
| 9 | PSI-69:268 | FLEX | psi_table | 11 | 0 |
| 10 | PSI-25:T28a | BASS-II | psi_table | 9 | 0 |
| 11 | PSI-69:023 | FLEX | psi_table | 11 | 0 |
| 12 | PSI-159:inverse:21228K2 | CFI-G | psi_table | 9 | 0 |
| 13 | PSI-69:136 | FLEX | psi_table | 11 | 0 |
| 14 | NTRS20150023456:FLEX-280 | FLEX | transcribed_from_table | 11 | 0 |
| 15 | PSI-100:S2 | Saffire | psi_table | 9 | 0 |
| 16 | PSI-159:normal:21153A1 | CFI-G | psi_table | 11 | 0 |
| 17 | PSI-159:inverse:21202H2 | CFI-G | psi_table | 9 | 0 |
| 18 | PSI-159:normal:21102C1 | CFI-G | psi_table | 11 | 0 |
| 19 | PSI-25:M9 | BASS-II | psi_table | 12 | 0 |
| 20 | PSI-69:272 | FLEX | psi_table | 11 | 0 |

**Rows with at least one failed check: 0 of 20**

## Details

### 1. PSI-159:normal:21291C1  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Normal Flames.csv#data_row=169`  
- PASS test_id PSI-159:normal:21291C1 vs source key PSI-159:normal:21291C1
- PASS orig burn_duration_s: recorded '246' vs source cell '246'
- PASS burn_duration_s: pipeline 246 vs recomputed 246 (246 s)
- PASS orig oxygen_fraction: recorded '0.394233062' vs source cell '0.394233062'
- PASS oxygen_fraction: pipeline 0.394233 vs recomputed 0.394233 (0.394233062 mole fraction)
- PASS orig oxygen_fraction_final: recorded '0.389271344' vs source cell '0.389271344'
- PASS oxygen_fraction_final: pipeline 0.389271 vs recomputed 0.389271 (0.389271344 mole fraction)
- PASS orig pressure_kpa: recorded '2.0266' vs source cell '2.0266'
- PASS pressure_kpa: pipeline 202.66 vs recomputed 202.66 (2.0266 bar)
- PASS material_or_fuel '30% butane' vs source cell '30% butane'
- PASS outcome end=FT hot=Yes -> externally_terminated (expected externally_terminated)

### 2. PSI-159:inverse:21216H2  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Inverse Flames.csv#data_row=51`  
- PASS test_id PSI-159:inverse:21216H2 vs source key PSI-159:inverse:21216H2
- PASS orig burn_duration_s: recorded '18' vs source cell '18'
- PASS burn_duration_s: pipeline 18 vs recomputed 18 (18 s)
- PASS orig oxygen_fraction: recorded '0.85' vs source cell '0.85'
- PASS oxygen_fraction: pipeline 0.85 vs recomputed 0.85 (0.85 mole fraction)
- PASS orig pressure_kpa: recorded '1.1033' vs source cell '1.1033'
- PASS pressure_kpa: pipeline 110.33 vs recomputed 110.33 (1.1033 bar)
- PASS material_or_fuel 'ethane' vs source cell 'ethane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 3. PSI-25:T7  
source_ref: `data/raw/psi/PSI-25/PSI-25_Experimental table_BASS-II.csv#data_row=107`  
- PASS test_id PSI-25:T7 vs source key PSI-25:T7
- PASS orig oxygen_fraction: recorded '17.3' vs source cell '17.3'
- PASS oxygen_fraction: pipeline 0.173 vs recomputed 0.173 (17.3 vol%)
- PASS orig oxygen_fraction_final: recorded '17.1' vs source cell '17.1'
- PASS oxygen_fraction_final: pipeline 0.171 vs recomputed 0.171 (17.1 vol%)
- PASS material_or_fuel '4 cm spherical section' vs source cell '4 cm spherical section'
- PASS outcome_class unknown until a human approves the LLM proposal
- PASS observation words found on PDF p.121 (missing [])

### 4. PSI-69:118  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=118`  
- PASS test_id PSI-69:118 vs source key PSI-69:118
- PASS orig burn_duration_s: recorded '2.5' vs source cell '2.5'
- PASS burn_duration_s: pipeline 2.5 vs recomputed 2.5 (2.5 s)
- PASS orig outcome_class: recorded 'Extinction' vs source cell 'Extinction'
- PASS orig oxygen_fraction: recorded '0.2' vs source cell '0.2'
- PASS oxygen_fraction: pipeline 0.2 vs recomputed 0.2 (0.2 mole fraction)
- PASS orig pressure_kpa: recorded '532.8' vs source cell '532.8'
- PASS pressure_kpa: pipeline 71.0342 vs recomputed 71.0342 (532.8 mmHg)
- PASS material_or_fuel 'Heptane' vs source cell 'Heptane'
- PASS outcome from Test end 'Extinction' -> self_extinguished (expected self_extinguished)
- PASS diameter '2.93' vs label 'Extinction': disagree=False matches the flag

### 5. PSI-69:212  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=212`  
- PASS test_id PSI-69:212 vs source key PSI-69:212
- PASS orig burn_duration_s: recorded '3.4' vs source cell '3.4'
- PASS burn_duration_s: pipeline 3.4 vs recomputed 3.4 (3.4 s)
- PASS orig outcome_class: recorded 'Extinction' vs source cell 'Extinction'
- PASS orig oxygen_fraction: recorded '0.15' vs source cell '0.15'
- PASS oxygen_fraction: pipeline 0.15 vs recomputed 0.15 (0.15 mole fraction)
- PASS orig pressure_kpa: recorded '764' vs source cell '764'
- PASS pressure_kpa: pipeline 101.858 vs recomputed 101.858 (764 mmHg)
- PASS material_or_fuel 'Heptane' vs source cell 'Heptane'
- PASS outcome from Test end 'Extinction' -> self_extinguished (expected self_extinguished)
- PASS diameter '2.31' vs label 'Extinction': disagree=False matches the flag

### 6. PSI-159:normal:21112A4  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Normal Flames.csv#data_row=48`  
- PASS test_id PSI-159:normal:21112A4 vs source key PSI-159:normal:21112A4
- PASS orig burn_duration_s: recorded '185' vs source cell '185'
- PASS burn_duration_s: pipeline 185 vs recomputed 185 (185 s)
- PASS orig oxygen_fraction: recorded '0.386794842' vs source cell '0.386794842'
- PASS oxygen_fraction: pipeline 0.386795 vs recomputed 0.386795 (0.386794842 mole fraction)
- PASS orig oxygen_fraction_final: recorded '0.379543758' vs source cell '0.379543758'
- PASS oxygen_fraction_final: pipeline 0.379544 vs recomputed 0.379544 (0.379543758 mole fraction)
- PASS orig pressure_kpa: recorded '0.9443956' vs source cell '0.9443956'
- PASS pressure_kpa: pipeline 94.4396 vs recomputed 94.4396 (0.9443956 bar)
- PASS material_or_fuel 'propane' vs source cell 'propane'
- PASS outcome end=FT hot=Yes -> externally_terminated (expected externally_terminated)

### 7. PSI-159:normal:21137A7  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Normal Flames.csv#data_row=121`  
- PASS test_id PSI-159:normal:21137A7 vs source key PSI-159:normal:21137A7
- PASS orig burn_duration_s: recorded '33' vs source cell '33'
- PASS burn_duration_s: pipeline 33 vs recomputed 33 (33 s)
- PASS orig oxygen_fraction: recorded '0.352403076' vs source cell '0.352403076'
- PASS oxygen_fraction: pipeline 0.352403 vs recomputed 0.352403 (0.352403076 mole fraction)
- PASS orig oxygen_fraction_final: recorded '0.350765374' vs source cell '0.350765374'
- PASS oxygen_fraction_final: pipeline 0.350765 vs recomputed 0.350765 (0.350765374 mole fraction)
- PASS orig pressure_kpa: recorded '1.0133' vs source cell '1.0133'
- PASS pressure_kpa: pipeline 101.33 vs recomputed 101.33 (1.0133 bar)
- PASS material_or_fuel '30% propane' vs source cell '30% propane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 8. PSI-159:inverse:21202A4  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Inverse Flames.csv#data_row=20`  
- PASS test_id PSI-159:inverse:21202A4 vs source key PSI-159:inverse:21202A4
- PASS orig burn_duration_s: recorded '5' vs source cell '5'
- PASS burn_duration_s: pipeline 5 vs recomputed 5 (5 s)
- PASS orig oxygen_fraction: recorded '0.85' vs source cell '0.85'
- PASS oxygen_fraction: pipeline 0.85 vs recomputed 0.85 (0.85 mole fraction)
- PASS orig pressure_kpa: recorded '2.2066' vs source cell '2.2066'
- PASS pressure_kpa: pipeline 220.66 vs recomputed 220.66 (2.2066 bar)
- PASS material_or_fuel 'ethane' vs source cell 'ethane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 9. PSI-69:268  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=268`  
- PASS test_id PSI-69:268 vs source key PSI-69:268
- PASS orig burn_duration_s: recorded '3.5' vs source cell '3.5'
- PASS burn_duration_s: pipeline 3.5 vs recomputed 3.5 (3.5 s)
- PASS orig outcome_class: recorded 'Extinction' vs source cell 'Extinction'
- PASS orig oxygen_fraction: recorded '0.18' vs source cell '0.18'
- PASS oxygen_fraction: pipeline 0.18 vs recomputed 0.18 (0.18 mole fraction)
- PASS orig pressure_kpa: recorded '530.3' vs source cell '530.3'
- PASS pressure_kpa: pipeline 70.7009 vs recomputed 70.7009 (530.3 mmHg)
- PASS material_or_fuel 'Heptane' vs source cell 'Heptane'
- PASS outcome from Test end 'Extinction' -> self_extinguished (expected self_extinguished)
- PASS diameter '0.84' vs label 'Extinction': disagree=False matches the flag

### 10. PSI-25:T28a  
source_ref: `data/raw/psi/PSI-25/PSI-25_Experimental table_BASS-II.csv#data_row=127`  
- PASS test_id PSI-25:T28a vs source key PSI-25:T28a
- PASS orig oxygen_fraction: recorded '20.7' vs source cell '20.7'
- PASS oxygen_fraction: pipeline 0.207 vs recomputed 0.207 (20.7 vol%)
- PASS orig oxygen_fraction_final: recorded '0.9' vs source cell '0.9'
- PASS oxygen_fraction_final: pipeline 0.009 vs recomputed 0.009 (0.9 vol%)
- PASS material_or_fuel '1 cm SIBAL' vs source cell '1 cm SIBAL'
- PASS outcome_class unknown until a human approves the LLM proposal
- PASS observation words found on PDF p.121 (missing [])
- PASS stated pressure "1 atm" on PDF p.102 -> 101.325 kPa (flag nominal: True)

### 11. PSI-69:023  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=23`  
- PASS test_id PSI-69:023 vs source key PSI-69:023
- PASS orig burn_duration_s: recorded '13.1' vs source cell '13.1'
- PASS burn_duration_s: pipeline 13.1 vs recomputed 13.1 (13.1 s)
- PASS orig outcome_class: recorded 'Disruption' vs source cell 'Disruption'
- PASS orig oxygen_fraction: recorded '0.34' vs source cell '0.34'
- PASS oxygen_fraction: pipeline 0.34 vs recomputed 0.34 (0.34 mole fraction)
- PASS orig pressure_kpa: recorded '541.8' vs source cell '541.8'
- PASS pressure_kpa: pipeline 72.2341 vs recomputed 72.2341 (541.8 mmHg)
- PASS material_or_fuel 'Heptane' vs source cell 'Heptane'
- PASS outcome from Test end 'Disruption' -> other (expected other)
- PASS diameter '' vs label 'Disruption': disagree=False matches the flag

### 12. PSI-159:inverse:21228K2  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Inverse Flames.csv#data_row=78`  
- PASS test_id PSI-159:inverse:21228K2 vs source key PSI-159:inverse:21228K2
- PASS orig burn_duration_s: recorded '12' vs source cell '12'
- PASS burn_duration_s: pipeline 12 vs recomputed 12 (12 s)
- PASS orig oxygen_fraction: recorded '0.5' vs source cell '0.5'
- PASS oxygen_fraction: pipeline 0.5 vs recomputed 0.5 (0.5 mole fraction)
- PASS orig pressure_kpa: recorded '1.1033' vs source cell '1.1033'
- PASS pressure_kpa: pipeline 110.33 vs recomputed 110.33 (1.1033 bar)
- PASS material_or_fuel 'propane' vs source cell 'propane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 13. PSI-69:136  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=136`  
- PASS test_id PSI-69:136 vs source key PSI-69:136
- PASS orig burn_duration_s: recorded '17' vs source cell '17'
- PASS burn_duration_s: pipeline 17 vs recomputed 17 (17 s)
- PASS orig outcome_class: recorded 'Completion' vs source cell 'Completion'
- PASS orig oxygen_fraction: recorded '0.24' vs source cell '0.24'
- PASS oxygen_fraction: pipeline 0.24 vs recomputed 0.24 (0.24 mole fraction)
- PASS orig pressure_kpa: recorded '768.1' vs source cell '768.1'
- PASS pressure_kpa: pipeline 102.405 vs recomputed 102.405 (768.1 mmHg)
- PASS material_or_fuel 'Heptane' vs source cell 'Heptane'
- PASS outcome from Test end 'Completion' -> burned_to_completion (expected burned_to_completion)
- PASS diameter '–' vs label 'Completion': disagree=False matches the flag

### 14. NTRS20150023456:FLEX-280  
source_ref: `NTRS 20150023456, PDF p.34 (printed p.28), Table IX, row FLEX-280 | data/transcribed/NTRS20150023456_flex_tests_275_280.csv#data_row=6`  
- PASS cited pages/slides [34]
- PASS pressure 766.2 mmHg in cited page
- PASS droplet_initial_diameter_mm=2.82 found in cited page
- PASS extinction_diameter_mm=.73 found in cited page
- PASS burning_rate_mm2_s=.65 found in cited page
- PASS cir_identifier=H19H201 found in cited page
- PASS O2 0.21 found in cited page
- PASS burn time 11.7 found in cited page
- PASS Test end 'Extinction' found in cited page (kept raw)
- PASS outcome from Test end 'Extinction' -> self_extinguished (expected self_extinguished)
- PASS diameter '.73' vs label 'Extinction': disagree=False matches the flag

### 15. PSI-100:S2  
source_ref: `data/raw/psi/PSI-100/PSI-100_Experimental table_SAFFIRE-3.csv#data_row=2`  
- PASS test_id PSI-100:S2 vs source key PSI-100:S2
- PASS orig flow_velocity_cm_s: recorded '30 cm/s' vs source cell '30 cm/s'
- PASS flow_velocity_cm_s: pipeline 30 vs recomputed 30 (30 cm/s cm/s)
- PASS orig sample_length_cm: recorded '94 cm' vs source cell '94 cm'
- PASS sample_length_cm: pipeline 94 vs recomputed 94 (94 cm cm)
- PASS orig sample_thickness_mm: recorded '.33 cm' vs source cell '.33 cm'
- PASS sample_thickness_mm: pipeline 3.3 vs recomputed 3.3 (.33 cm cm)
- PASS orig sample_width_cm: recorded '40.6 cm' vs source cell '40.6 cm'
- PASS sample_width_cm: pipeline 40.6 vs recomputed 40.6 (40.6 cm cm)

### 16. PSI-159:normal:21153A1  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Normal Flames.csv#data_row=125`  
- PASS test_id PSI-159:normal:21153A1 vs source key PSI-159:normal:21153A1
- PASS orig burn_duration_s: recorded '59' vs source cell '59'
- PASS burn_duration_s: pipeline 59 vs recomputed 59 (59 s)
- PASS orig oxygen_fraction: recorded '0.3887' vs source cell '0.3887'
- PASS oxygen_fraction: pipeline 0.3887 vs recomputed 0.3887 (0.3887 mole fraction)
- PASS orig oxygen_fraction_final: recorded '0.375900202' vs source cell '0.375900202'
- PASS oxygen_fraction_final: pipeline 0.3759 vs recomputed 0.3759 (0.375900202 mole fraction)
- PASS orig pressure_kpa: recorded '0.50665' vs source cell '0.50665'
- PASS pressure_kpa: pipeline 50.665 vs recomputed 50.665 (0.50665 bar)
- PASS material_or_fuel '30% ethane' vs source cell '30% ethane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 17. PSI-159:inverse:21202H2  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Inverse Flames.csv#data_row=22`  
- PASS test_id PSI-159:inverse:21202H2 vs source key PSI-159:inverse:21202H2
- PASS orig burn_duration_s: recorded '16' vs source cell '16'
- PASS burn_duration_s: pipeline 16 vs recomputed 16 (16 s)
- PASS orig oxygen_fraction: recorded '0.85' vs source cell '0.85'
- PASS oxygen_fraction: pipeline 0.85 vs recomputed 0.85 (0.85 mole fraction)
- PASS orig pressure_kpa: recorded '2.2066' vs source cell '2.2066'
- PASS pressure_kpa: pipeline 220.66 vs recomputed 220.66 (2.2066 bar)
- PASS material_or_fuel 'ethane' vs source cell 'ethane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 18. PSI-159:normal:21102C1  
source_ref: `data/raw/psi/PSI-159/PSI-159_Experimental table_CFI-G_Normal Flames.csv#data_row=16`  
- PASS test_id PSI-159:normal:21102C1 vs source key PSI-159:normal:21102C1
- PASS orig burn_duration_s: recorded '41' vs source cell '41'
- PASS burn_duration_s: pipeline 41 vs recomputed 41 (41 s)
- PASS orig oxygen_fraction: recorded '0.393031985' vs source cell '0.393031985'
- PASS oxygen_fraction: pipeline 0.393032 vs recomputed 0.393032 (0.393031985 mole fraction)
- PASS orig oxygen_fraction_final: recorded '0.390548195' vs source cell '0.390548195'
- PASS oxygen_fraction_final: pipeline 0.390548 vs recomputed 0.390548 (0.390548195 mole fraction)
- PASS orig pressure_kpa: recorded '1.0133' vs source cell '1.0133'
- PASS pressure_kpa: pipeline 101.33 vs recomputed 101.33 (1.0133 bar)
- PASS material_or_fuel '50% butane' vs source cell '50% butane'
- PASS outcome end=SE hot=Yes -> self_extinguished (expected self_extinguished)

### 19. PSI-25:M9  
source_ref: `data/raw/psi/PSI-25/PSI-25_Experimental table_BASS-II.csv#data_row=35`  
- PASS test_id PSI-25:M9 vs source key PSI-25:M9
- PASS orig oxygen_fraction: recorded '18' vs source cell '18'
- PASS oxygen_fraction: pipeline 0.18 vs recomputed 0.18 (18 vol%)
- PASS orig oxygen_fraction_final: recorded '17.6' vs source cell '17.6'
- PASS oxygen_fraction_final: pipeline 0.176 vs recomputed 0.176 (17.6 vol%)
- PASS orig sample_thickness_mm: recorded '1 cm wide PMMA 3 mm thick' vs source cell '1 cm wide PMMA 3 mm thick'
- PASS orig sample_width_cm: recorded '1 cm wide PMMA 3 mm thick' vs source cell '1 cm wide PMMA 3 mm thick'
- PASS material_or_fuel '1 cm wide PMMA 3 mm thick' vs source cell '1 cm wide PMMA 3 mm thick'
- PASS outcome_class unknown until a human approves the LLM proposal
- PASS observation words found on PDF p.117 (missing [])
- PASS Table 5.1 row M9 (thickness, width, sides) present on PDF p.65
- PASS flow 14 equals the single Table 5.1 velocity '14'

### 20. PSI-69:272  
source_ref: `data/raw/psi/PSI-69/PSI-69_Experimental table_FLEX.csv#data_row=272`  
- PASS test_id PSI-69:272 vs source key PSI-69:272
- PASS orig burn_duration_s: recorded '2.9' vs source cell '2.9'
- PASS burn_duration_s: pipeline 2.9 vs recomputed 2.9 (2.9 s)
- PASS orig outcome_class: recorded 'Extinction' vs source cell 'Extinction'
- PASS orig oxygen_fraction: recorded '0.17' vs source cell '0.17'
- PASS oxygen_fraction: pipeline 0.17 vs recomputed 0.17 (0.17 mole fraction)
- PASS orig pressure_kpa: recorded '531.5' vs source cell '531.5'
- PASS pressure_kpa: pipeline 70.8608 vs recomputed 70.8608 (531.5 mmHg)
- PASS material_or_fuel 'Methanol' vs source cell 'Methanol'
- PASS outcome from Test end 'Extinction' -> self_extinguished (expected self_extinguished)
- PASS diameter '2.31' vs label 'Extinction': disagree=False matches the flag

