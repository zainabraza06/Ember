<!-- Official text as supplied by the team on 2026-11-14 (pasted from the published challenge page and its Resources tab). The page itself could not be fetched from the development machine (TLS certificate error), so this copy was not re-checked against the live page by Claude. -->
# Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data

**Event:** 2026 NASA Space Apps Challenge
**Difficulty:** Advanced, Intermediate
**Subjects:** Space Exploration
**Source:** https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
**Last checked:** 14 November 2026 (full details now published; the title now reads "SI-Powered")

## Summary (as published)

For decades, NASA has studied how flames and fire behave in microgravity, gathering a trove of experimental data along the way. That knowledge matters more than ever as humans gear up to return to the Moon and press on to Mars, yet the volume of results makes them hard to find, compare, and understand. Your challenge is to create an interactive, super intelligence (SI) powered dashboard that summarizes, ranks, and interprets those findings to deliver fire safety insights for human space exploration.

## Background

- Fire hazards in space exploration: the Artemis II commander described a smoke alarm going off about 80,000 miles from home; Apollo 13 (oxygen tank explosion); Mir fire (oxygen generator failure); Apollo 1 (pre-launch fire in an oxygen-filled spacecraft, 1967).
- Without buoyancy, microgravity flames differ strongly from Earth flames (a candle flame becomes a blue sphere that relies on diffusion for oxygen).
- NASA spacecraft fire safety focuses on **prevention, detection and suppression**.
  - Prevention: control of ignition sources and material selection, which depends on flammability limits. Flammability depends strongly on oxygen concentration, and airflow matters in microgravity. Solid materials (fabrics, plastics) were studied in **BASS, BASS-II, Saffire-I, -II, -III**.
  - Detection: **SAME and SAME-R** (Smoke and Aerosol Measurement Experiment).
  - Suppression: **FLEX** (Flame Extinguishment Experiment), dilution with carbon dioxide and helium.
- An atmosphere with increased oxygen and reduced pressure is expected within the planned Moon Base and pressurized rovers, to facilitate spacesuit use.

## Objectives

Results from low-gravity combustion experiments (for example on the ISS) are publicly available through NASA's Physical Sciences Informatics (PSI) database, but the amount of data can be overwhelming: hard to find, harder to compare, harder yet to interpret.

Build an SI-powered, web-based dashboard that summarizes, ranks, and interprets combustion science investigations to deliver critical foundational insights for fire safety. You may consider enabling users to:

1. Identify investigations most relevant to the fire safety needs of habitable crew environments, including spacecraft, space stations, bases on the lunar and Martian surfaces, and pressurized rovers.
2. Extract data that supports predictive modeling of flammability and fire scenarios in space exploration.
3. Highlight research that informs the development of next-generation fire safety controls and equipment.

The dashboard could also address applications of the PSI data to fire safety on Earth (fine-water-mist extinguishers developed for the ISS; terrestrial smoke detection; firefighter gear and protective clothing).

Scope note: fire safety involving rockets and propellants is generally beyond the scope of the PSI research (rocket-engine combustion is effectively independent of gravity).

## Potential Considerations (optional)

- Target audience: professors, graduate and undergraduate students, aerospace researchers and engineers.
- Summarize and display for each investigation: experimental objectives; fuels, including shape and size of samples or burners; other test conditions such as oxygen concentration and airflow speed; variables (how tests within an investigation differed and how they were the same); sensors or types of measurements.
- Summarize and display similarities and differences between investigations.
- Other PSI investigations: DAFT and DAFT-2 (dust detection with the SAME instrument); BRE (ACME; materials flammability in still atmospheres as a function of material properties, gaseous fuel); other combustion investigations are relevant but less directly.
- Hardware groups:
  - ACME: six experiments with gaseous fuels, modular hardware in the Combustion Integrated Rack (CIR).
  - FLEX, FLEX-2, Cool Flames Investigation (CFI): burning liquid droplets, Multi-user Droplet Combustion Apparatus (MDCA) in the CIR.
  - BASS, BASS-II, SPICE, SLICE: solid and gaseous fuels, Microgravity Science Glovebox (MSG), fan-driven flow duct built for SPICE.
- Spacesuits and oxygen concentration: spacesuits use 100% oxygen at 4.3 psi (Earth sea level 14.7 psi). The Moon Base and pressurized rovers are expected at an intermediate pressure: oxygen likely 30% or greater, pressure 10.2 psi or less, which makes materials much more flammable. The highest-oxygen microgravity tests were ACME CFI-G (up to 85% oxygen from a spherical burner).
- Partial-gravity data: **there is currently no partial-gravity combustion data in PSI.** Expected in future from LUCI (Lunar-g Combustion Investigation) and FM2 (Flammability of Materials on the Moon). Partial gravity was mimicked in ACME E-FIELD Flames through the effect of an electric field on flame ions. Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels.

## NASA Data & Resources (Resources tab)

- PSI Data Repository, Combustion Science: https://psi.nasa.gov/physci/repo/search?q=combustion
- NASA Combustion Science: https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/
- NASA ScienceCasts: The Power of Studying Combustion on the ISS (video, 2018): https://www.youtube.com/watch?v=W1oXykoz9zg
- A Researcher's Guide to International Space Station Combustion Science (2015, 50+ pages): https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/
- Apollo 1: https://sma.nasa.gov/sma-disciplines/accllp/apollo-1
- Apollo 13: https://sma.nasa.gov/sma-disciplines/accllp/apollo-13
- 25 Years Ago: Fire Aboard Space Station Mir: https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/
- Fireman's Air Tanks (spinoff): https://spinoff.nasa.gov/node/9582
- Fire Detector (spinoff): https://spinoff.nasa.gov/node/9407
- New Technology for the Fire Attire (spinoff): https://spinoff.nasa.gov/node/9918

## Space Agency Partner Resources

None listed on the Resources tab as of 14 November 2026.
