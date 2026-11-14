# PSI-117: Effect of External Thermo-Convective Perturbation on Cool Flame Dynamics: A Multidimensional Multi-Physics CFD Analysis

- Acronym: none
- Record version: 2
- Source URL: https://psi.nasa.gov/physci/repo/data/investigations/PSI-117
- API record: https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-117 (saved as PSI-117_record.json)
- Retrieved: 2026-10-19
- License (PSI record): CC0-1.0
- DOI: 10.60555/gz0q-b577
- Platform: Ground (CFD of FLEX cool flames)

## Objective (PSI record)
The objective of this ground investigation was to use flight data obtained from PSI through NASA’s Flame Extinguishment Experiment (FLEX) to quantify how externally imposed thermal and convective perturbations regulated the dynamics and ultimate fate of already established droplet cool flames, and to explain run-to-run variability by isolating the roles of deliberate heating and unintentional drift-induced convection. Focusing on both small and large droplets, the work mapped stability windows for ignition, sustained oscillation, transitions to hot ignition and warm-flame behavior, and extinction under microgravity. By leveraging and extending the FLEX data in the PSI, this study produced reusable models and sensitivity analyses that coupled low-temperature chemistry with transport and radiative effects.

## Approach (PSI record)
OpenFOAM was used to develop a 3-D CFD model of n-alkane droplet cool flames in microgravity, coupling variable-density Navier–Stokes flow with low-temperature combustion chemistry, coupled heat and mass transfer, and radiation. Model fidelity was established against ISS FLEX measurements, after which controlled simulations examined three forcing modes (i) convection alone to mimic droplet drift, (ii) imposed heat flux, and (iii) combined convection plus heating applied to both large (1–4 mm) and sub-millimeter (~0.5 mm) droplets.

To accelerate progress, the study began with simplified chemistry and transitioned to reduced mechanisms for parameter sweeps over forcing amplitude and frequency, ambient composition (including ozone-assisted cases), and pressure. From each case, predictive observables were extracted (ignition delay, oscillation frequency and amplitude, stand-off and extinction diameters), and were used to construct stability maps that delineated conditions for cool-flame onset, persistence, and quenching. These maps were reconciled with FLEX observations and were used to guide next-generation test matrices for both large- and small-droplet experiments.

## Conditions varied (from the downloaded table, where one exists)
n/a (simulation)

## Outcomes measured
Cool-flame dynamics and extinction (simulated)

## Files downloaded
None (no experimental table in PSI record).
- PSI-117_record.json (metadata)

## Known problems
Release date 10-Jun-2026 per PSI record.
