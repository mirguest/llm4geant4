# Benchmark: Muon Through Scintillator

## Goal

Simulate a 1 GeV muon passing through a single plastic scintillator slab and measure the deposited energy.

## Geometry

- **World:** a box of air large enough to contain the scintillator and the particle source (e.g., 1 m per side).
- **Scintillator:** a 10 cm × 10 cm × 1 cm slab. Use `G4_PLASTIC_SC_VINYLTOLUENE` from Geant4/NIST materials. Center it at the origin.

## Physics

Use `QGSP_BERT` as the reference physics list, with default production cuts.

## Source

- Particle: muon (µ⁻) with 1 GeV kinetic energy.
- Direction: along the +z axis.
- Starting position: uniformly distributed over a 1 cm × 1 cm region centered on the z-axis, at z = -50 cm (upstream of the scintillator).

## Deliverables

A working and idiomatic Geant4 application with a reasonable source-file structure. The application must:

- Build with CMake against Geant4 11.x.
- Run in batch mode via a macro that executes 10,000 events.
- Record the energy deposited in the scintillator per event.
- Produce an output file (ROOT or AIDA format) containing the energy deposit distribution.

## Output

- The application source files (`.cc`, `.hh`, `CMakeLists.txt`).
- A batch macro (`run.mac`) for 10,000 events.
- The generated output file with the energy deposit histogram.

## Constraints

- Do not force all geometry, physics, generator, sensitive-detector, and output logic into a single file. Use a reasonable multi-file structure appropriate for a Geant4 application.
- Use explicit Geant4 units (`GeV`, `cm`, `mm`, etc.) for all physical quantities.
- The application should use `G4RunManagerFactory::CreateRunManager()` to create the run manager.
