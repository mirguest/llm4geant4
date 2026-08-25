# Benchmark: Muon Through Scintillator

## Goal

Simulate a 1 GeV muon passing through a single plastic scintillator slab and measure the deposited energy.

## Geometry

- **World:** a 120 cm × 120 cm × 120 cm box of air.
- **Scintillator:** a 10 cm × 10 cm × 1 cm slab, centered at the origin. Use `G4_PLASTIC_SC_VINYLTOLUENE` from Geant4/NIST materials.

## Physics

Use `QGSP_BERT` as the reference physics list, with default production cuts.

## Source

- Particle: muon (µ⁻) with 1 GeV kinetic energy.
- Direction: along the +z axis.
- Starting position: uniformly distributed over a 1 cm × 1 cm region centered on the z-axis, at z = -50 cm (upstream of the scintillator).

## Deliverables

A working Geant4 application that:

- Builds with CMake against Geant4 11.x.
- Runs in batch mode via a macro that executes 10,000 events.
- Records the energy deposited in the scintillator per event.
- Produces an output file (ROOT or AIDA format) containing the energy deposit distribution.

## Output

- The application source files and `CMakeLists.txt`.
- A batch macro (`run.mac`) for 10,000 events.
- The generated output file with the energy deposit histogram.
