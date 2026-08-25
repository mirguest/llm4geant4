# Geant4 Validation Strategy

## Levels of validation

### 1. Geometry validation

- Run `/geometry/test/run` to check for overlaps
- Visual inspection with `/vis/drawVolume`
- Verify mass of each volume against analytical calculation
- Check boundary crossing: place a track and verify navigation

### 2. Physics validation

- Compare against an appropriate trusted external reference for the particle, material, and energy regime when available.
- For electrons: NIST ESTAR stopping-power and CSDA range tables.
- For hadrons and muons: PDG or established experimental data where applicable.
- Cross-check with independent simulation results when external data is unavailable.

### 3. Output validation

- Confirm event count equals `/run/beamOn N`
- Check that histograms integrate to expected values
- Verify energy conservation (sum of deposits + escaping energy = incident energy)
- Validate that energy deposits are non-negative

### 4. Statistical validation

- Run enough events to achieve the statistical precision required by the benchmark or analysis. The required event count depends on the variance of the observable.
- Check that statistical uncertainties scale as 1/sqrt(N)
- Use independent random seeds across jobs
- Merge results from multiple independent runs

## Common validation plots

For a calorimeter or scintillator simulation, produce:

- Energy deposit spectrum per event
- Hit position distribution in XY, XZ, YZ
- Timing distribution of hits
- Energy deposit per layer (if segmented)
- Particle type composition of secondaries

## Regression testing

For each benchmark, maintain a reference histogram file. Compare new results:

- Chi-squared test against reference
- Kolmogorov-Smirnov test for distributions

Regression tolerances should be benchmark-specific and based on expected statistical fluctuations, reference sample size, physics configuration, and known Geant4-version effects.

## Reproducibility checklist

- [ ] Seed random engine with `G4Random::setTheSeed()`
- [ ] Use the same Geant4 version and physics list
- [ ] Document production cuts (range cuts) used
- [ ] Record geometry materials with their density and composition
- [ ] Fix all random seeds (geometry construction, physics, general)
