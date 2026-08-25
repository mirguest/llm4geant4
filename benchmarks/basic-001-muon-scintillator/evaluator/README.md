# Evaluator

Automated evaluation tooling will be added here in a future milestone.

## Planned capabilities

- Build and compile-check the submitted application against the target Geant4 version.
- Run the application and verify it completes without errors.
- Compare output histograms against the frozen reference (chi-squared, KS test).
- Check geometry: material composition, volume dimensions, overlap detection.
- Score each criterion from `rubric.yaml` and produce a summary report.

## Design constraint

The evaluator must work with output from any coding agent, not just a specific one. It operates on the generated source files and simulation output — it does not need to know which agent produced them.
