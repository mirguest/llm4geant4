# Geant4 Validation Strategy

## Levels of validation

### 1. Geometry validation
- Run `/geometry/test/run` to check for overlaps
- Visual inspection with `/vis/drawVolume`
- Verify mass of each volume against analytical calculation
- Check boundary crossing: place a track and verify navigation

### 2. Physics validation
- Compare energy deposit in known materials against NIST ESTAR values
- Check particle range against CSDA range tables
- Validate backscatter coefficients for electrons
- Compare shower shapes for electromagnetic cascades
- Verify neutron capture cross sections for thermal neutrons

### 3. Output validation
- Confirm event count equals `/run/beamOn N`
- Check that histograms integrate to expected values
- Verify energy conservation (sum of deposits + escaping energy = incident energy)
- Validate that no negative energy deposits appear (unless Cherenkov is enabled with correct sign convention)

### 4. Statistical validation
- Run ≥10k events for percent-level precision
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
- Mean and RMS within 2% of reference

## Reproducibility checklist

- [ ] Seed random engine with `G4Random::setTheSeed()`
- [ ] Use the same Geant4 version and physics list
- [ ] Document production cuts (range cuts) used
- [ ] Record geometry materials with their density and composition
- [ ] Fix all random seeds (geometry construction, physics, general)
