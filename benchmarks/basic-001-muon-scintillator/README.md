# Benchmark 001: Muon Through Scintillator

## Goal

Simulate a 1 GeV muon passing through a single plastic scintillator slab. Record energy deposit and hit position.

## Geometry

- World: 1 m × 1 m × 1 m air box
- Scintillator: 10 cm × 10 cm × 1 cm plastic scintillator (C₉H₁₀), centered at origin

## Physics

- `QGSP_BERT` reference physics list
- Default production cuts

## Source

- 1 GeV muon (µ⁻), directed along +z axis
- Uniformly distributed on a 1 cm² region at z = -50 cm

## Deliverables

- `main.cc` — application with geometry, physics, generator, SD, and output
- `CMakeLists.txt` — build file
- `run.mac` — macro for 10,000 events

## Expected results

- Mean energy deposit: ~2.25 MeV (MIP at ~2 MeV·cm²/g in scintillator)
- Energy deposit distribution peaks near the Landau most-probable value
- Hit positions uniformly distributed in XY over the scintillator area

## Scoring

| Criterion | Points |
|-----------|--------|
| Compiles and runs without errors | 20 |
| Correct geometry (materials, dimensions, placements) | 20 |
| Sensitive detector records energy deposit and position | 20 |
| Output: energy deposit histogram in ROOT/AIDA format | 20 |
| Mean energy deposit within 20% of reference | 10 |
| Clean build with no warnings | 10 |
