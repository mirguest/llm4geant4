# Reference Simulation

A frozen Geant4 reference configuration and reference run will be added here in a future milestone.

## Planned reference

- A complete, reviewed Geant4 application implementing this benchmark with the exact geometry, physics list, and source configuration specified in `task.md`.
- A reference output file (ROOT) from a statistically significant run (e.g., 1M events) with a fixed random seed.
- Metadata: Geant4 version, physics list version, production cuts, and build environment.

## Reference Geant4 version

- **Compatibility target:** Geant4 11.x (the task should be solvable with any 11.x installation).
- **Reference evaluation environment:** Geant4 11.4.2 (the specific version used to produce frozen reference results).

The reference will serve as the ground truth for automated evaluation once produced.
