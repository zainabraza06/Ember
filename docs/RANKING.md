# Ranking and evidence-strength rules

Implemented in `pipeline/ranking.py` and `pipeline/interpret.py`; outputs `data/processed/ranking.json` and `interpretations.json`. Both are deterministic: the same inputs always give the same numbers. **No model is involved.** The weights below are the team's judgement; they are shown next to every score on the site (Ranking tab).

## 1. What the ranking means
It orders the 24 PSI combustion investigations by **relevance to one mission atmosphere and to spacecraft fire safety**, using facts in the catalog, the PSI records, the unified test table and the official challenge text. It does **not** rank the quality or importance of the science, and an investigation with no per-test rows in the unified table cannot score on atmosphere or data (that is stated in its breakdown).

## 2. Score (0 to 100)
`score = 100 x (0.35 atmosphere + 0.20 safety_area + 0.20 fuel + 0.15 data + 0.10 gravity)`, each component between 0 and 1.

| Component | Weight | Rule |
|---|---|---|
| atmosphere | 0.35 | For investigations with rows that have oxygen and pressure: `0.6 x (share of rows inside the profile envelope) + 0.4 x nearness`. Nearness = `max over rows of max(0, 1 - d)`, where `d = sqrt((dO2 / 0.15)^2 + (dP / 50 kPa)^2)` and dO2, dP are how far the row lies outside the envelope (0 inside). Investigations without such rows score 0 here; record text is not parsed |
| safety_area | 0.20 | 1 if the investigation is tagged prevention, detection or suppression (official Background text or record metadata, see `scripts/build_site.py`), else 0 |
| fuel | 0.20 | solid materials 1.0; smoke or aerosol from heated materials 0.6; liquid droplets or gas flames 0.4; ground analysis or not documented 0.2 (from the catalog `material_class`) |
| data | 0.15 | `min(1, test rows in the unified table / 100)` |
| gravity | 0.10 | flight data in microgravity 1.0; ground analysis or modelling 0.4. No investigation has partial-gravity data, so no investigation gets credit for lunar or Martian gravity |

## 3. Profiles (envelopes)
| Profile | Oxygen | Pressure | Basis |
|---|---|---|---|
| Lunar base | 30% or more | 10.2 psi (70.33 kPa) or less | official challenge text |
| Pressurized rover | 30% or more | 10.2 psi or less | official challenge text (same envelope as the lunar base) |
| Spacesuit | 100% | 4.3 psi (29.65 kPa) | official challenge text |
| ISS-like cabin | 19% to 25% | within 10% of 14.7 psi (91.2 to 111.5 kPa) | **team-defined**: the official text gives no ISS cabin numbers; 14.7 psi is its Earth sea-level reference and 21% oxygen appears in the PSI-20 objective text |

kPa values are computed from psi (1 psi = 6.894757 kPa) in `pipeline/profiles.py`.

## 4. Evidence-strength label (Interpretation tab)
| Label | Rule |
|---|---|
| moderate | at least 100 tests, all in one experiment family |
| limited | 30 to 99 tests |
| very limited | fewer than 30 tests |
| strong | at least 100 tests agreeing across two or more independent experiment families (no current analysis qualifies) |
A recorded source conflict that touches the analysis lowers the label one step (never below "very limited"). Each summary also lists its caveats (label/diameter disagreements, one experiment family, other variables changing at the same time).

## 5. Known limits
- The atmosphere component uses only the 6 investigations with per-test rows; the other 18 score 0 there regardless of what their record text says.
- Weights are judgement. Different weights change the order; the site shows each component so a reader can disagree.
- The ISS-like cabin envelope is our assumption.
- With the current data CFI-G is the only investigation with tests inside the lunar and rover envelope, but it is untagged for a safety area and uses gas fuel, so it does not rank first.

## 6. Reproduce
`python -m pipeline && python -m pipeline.profiles && python -m pipeline.ranking && python -m pipeline.interpret && python scripts/build_site.py`

## 7. Data-gap ranking ("Where should NASA test next?", home page)
Not a safety judgement and not part of the investigation ranking above: it ranks **untested conditions**, using only the existing coverage grid of the Atmosphere map.

- **Grid.** The microgravity (0 g) coverage grid of the map: cells 20 kPa wide and 5 percentage points of O2 tall (17 x 20 = 340 cells). A cell is **untested** when no test and no oxygen-limit point at 0 g falls in it.
- **Envelope and design point.** NASA's own planned lunar-base atmosphere, from the challenge text (docs/CHALLENGE.md): "oxygen likely 30% or greater, pressure 10.2 psi or less". The envelope is O2 >= 30% and pressure <= 70.33 kPa; the **design point** is its corner, 30% O2 at 10.2 psi (70.33 kPa). Only untested cells whose centre is inside the envelope are considered.
- **Bands.** Untested cells that touch within one 20 kPa pressure column are merged into a band. A band is at most 3 cells (15 percentage points of O2) tall. A full-height run is a stripe up to 70 points tall and would leave only two non-touching candidates; with 4-cell bands only four non-touching bands exist inside the envelope; 3 cells is the tallest cap that yields five. Longer runs are cut into bands of 3 cells from the lowest oxygen upward.
- **Sort key for bands, in this order, ascending:**
  1. `d_nom` = distance from the design point to the nearest cell of the band, in cells: sqrt( ((p - 70.33) / 20)^2 + ((o - 0.30) / 0.05)^2 ), using cell centres.
  2. `n_nb` = number of **tests** (oxygen-limit rows excluded) in the cells surrounding the band (the 8-neighbourhood of every band cell, band cells excluded). Fewer first.
  3. Lower oxygen first (lowest oxygen row of the band), then lower pressure column, only to make the order deterministic.
- **Selection.** Bands are taken best-first; a band is skipped if it touches (is within one cell of, including diagonally) a band already selected, so no two cards cover the same stripe or neighbouring cells. The first five that remain are shown.
- **Card fields.** Oxygen range and pressure range of the band; `n_nb` ("tests nearby"); the investigation family of the test nearest the band centre, with its distance in cells; and one line with the number of merged cells, `d_nom` and `n_nb`. "Show the band on the map" switches the map to 0 g and highlights the whole band.
- **Limits.** It looks at oxygen and pressure only (not gravity, fuel, flow or sample size), uses 0 g coverage only, and says nothing about how dangerous a condition is.
