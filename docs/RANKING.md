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
