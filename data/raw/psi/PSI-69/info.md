# PSI-69: Flame Extinguishment Experiment

- Acronym: FLEX
- Record version: 5
- Source URL: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- API record: https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-69 (saved as PSI-69_record.json)
- Retrieved: 2026-10-19
- License (PSI record): CC0-1.0
- DOI: 10.60555/mbq8-0451
- Platform: ISS: CIR/MDCA

## Objective (PSI record)
The FLEX (Flame Extinguishment Experiment) investigation aims to map the flammability limits of liquid fuels in microgravity environments, measure the effectiveness of various gaseous fire suppressants such as CO2, He, and SF6, and develop reliable predictive models for combustion limits under reduced gravity conditions. The mission seeks to validate and improve simplified models by incorporating detailed chemical reactions, heat transfer, and material movement, using both space-based data and extensive ground-based tests. Key flight experiment goals include obtaining high-resolution measurements of droplet burning rates, flame extinction behavior, heat radiation, soot levels, and temperature profiles, while systematically analyzing the effects of different ambient conditions and suppressant concentrations. These investigations are essential for advancing the fundamental understanding of combustion processes in microgravity and enhancing fire safety protocols for future space missions.

## Approach (PSI record)
The FLEX experiments involve igniting and observing the burning behavior of relatively large droplets. A primary objective of the experiments is to determine the Limiting Oxygen Index (LOI) as a function of ambient pressure and determine how the presence of a suppressant influences the LOI .
The basic outline of the procedure to construct this diagram is as follows:
  1. Select the test pressure (0.5 − 1.5 atm) for the LOI tests.
  2. Select a smaller droplet size (≈ 3 mm)
  3. Select an ambient oxygen mole fraction that, based on ground-based testing, will support droplets burning to completion (as opposed to extinguishing at a finite droplet size).
  4. Perform a droplet combustion test.
  5. Increase the droplet size or repeat the test (if finite extinction diameter at flame extinction observed).
  6. Continue steps 4 and 5 until flame exists for only a short time after ignition (radiative extinction).
  7. Continue steps 4 thru 6 at a decreased ambient oxygen mole fraction.
  8. Continue step 7 to an ambient oxygen mole fraction where the droplet does not ignite.

There were ambient conditions where the extinction droplet sizes at all ambient oxygen mole fractions were too small to either be observed or measured with the available diagnostics. In this case, the determination of the LOI is similar, but more iterative. Instead of observing flame extinction, however, the procedure  involved an iterative sequence of tests (burn to completion followed by a no ignition test) with progressively smaller increments in ambient oxygen mole fraction to determine the LOI . For the slow flow tests (in the flight experiment), the configuration of the flight hardware did not allow for adequate diagnostics over the entire test for a droplet in a uniform, steady convective flow.  In these tests, the procedure will be to duplicate tests above which yield finite-sized extinction droplet diameters. Near the end of the tests, prior to flame extinction, the droplet will be subjected to a small, sub-buoyant, convective flow (imparted by translating the droplet at a slow, uniform speed).

The goal of the experiment is then to see how the presence of this flow influences the extinction process. Note, a large number of the tests involve free droplets (as opposed to fiber-supported droplets) and a number of these tests will have droplets with a slow drift velocity. Data gathered from these tests to examine the influences of a small, sub-buoyant flow on both the burning and extinction process.

## Conditions varied (from the downloaded table, where one exists)
Table: ambient pressure (mmHg), mole fractions O, N, CO (header; likely CO2 but not stated), He; initial droplet diameter. Observed ranges: O 0.12-0.34, He 0-0.45, pressure 526-2320 mmHg excluding one 0.0 entry

## Outcomes measured
Visible flame extinction diameter, burning rate, burn time, test end class (Extinction 186, Disruption 61, Completion 27)

## Files downloaded
- PSI-69_Experimental table_FLEX.csv
- PSI-69_record.json (metadata)

## Known problems
One pressure entry is 0.0; one duplicated FLEX Identifier; header "CO ..." ambiguous (CO vs CO2); some diameters blank (extinction diameter numeric in 197 rows).
