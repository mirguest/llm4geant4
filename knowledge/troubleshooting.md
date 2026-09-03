# Troubleshooting

Use this when a build succeeds but the application crashes, hangs, or produces suspicious output. Pair with `knowledge/validation.md` for confirming results are physically plausible once the application runs cleanly.

## Build / environment

| Symptom | Likely cause |
|---|---|
| CMake can't find Geant4 (`Could NOT find Geant4`) | Environment not sourced (`source .../geant4.sh`), or `-DGeant4_DIR=/path/to/lib/Geant4-11.X` not passed. |
| Link errors for specific Geant4 symbols | Geant4 built without a feature the app requires (e.g. `G4MULTITHREADED`, GDML support via Xerces-C, or vis drivers) — check `geant4-config --version` and the installation's enabled features. |
| `G4NDL`/data library errors at runtime (`G4ENSDFSTATEDATA`, `G4NEUTRONHPDATA`, `G4LEDATA`, ...) | Required Geant4 physics datasets not installed or environment variables not set — `geant4-config --datasets` (or the environment script) should point at them. Needed particularly for `_HP` physics lists and low-energy EM (Livermore/Penelope). |

## Startup / initialization crashes

| Symptom | Likely cause |
|---|---|
| Immediate segfault on `runManager->Initialize()` or first `BeamOn` | `DetectorConstruction::Construct()` returns `nullptr` or doesn't return the world physical volume. |
| `InvalidSetup` / physics-related exception at initialization | A process or particle used elsewhere isn't constructed by the registered physics list (e.g. optical processes without `G4OpticalPhysics`, or a decay used without `G4DecayPhysics`). |
| Exception mentioning overlapping or malformed geometry at run start | Run `/geometry/test/run` or re-check placements built with `checkOverlaps=true`; also check daughter-outside-mother containment (see `knowledge/geometry.md`). |

## Runtime warnings from the navigator

| Symptom | Likely cause |
|---|---|
| Repeated "track stuck" / "same next step" warnings (`GeomNav1002`-class exceptions), a run that appears to hang | Usually a geometry overlap or degenerate boolean-solid surface causing the navigator to loop at a boundary. Check overlaps first. Also occurs with pathologically small `G4UserLimits` steps combined with very low production cuts, generating enormous numbers of sub-threshold steps. |
| Warnings about a region and production cuts mismatch | A `G4Region` was created but never given cuts (`SetProductionCuts`), or two regions were accidentally attached to the same logical volume. |

## Empty or wrong scoring results

| Symptom | Likely cause |
|---|---|
| Hits collection / scorer always empty, even though geometry and physics look right | In MT mode, the sensitive detector was created in `Construct()` instead of `ConstructSDandField()` (each worker needs its own SD instance — see `knowledge/multithreading.md`). |
| Energy deposit always exactly zero | `SetSensitiveDetector()` was never called on the target logical volume; or the scoring volume's material/cuts are such that no secondaries are produced inside it (cut too coarse for a thin volume — see production cuts in `knowledge/physics-lists.md`); or the primary never actually enters the volume (check source position/direction against geometry placement). |
| Energy deposit far outside plausible order of magnitude | Wrong units somewhere (forgetting the explicit `* MeV`/`* mm` multiplier is the single most common cause), or double-counting from an overlapping volume. |
| Results differ between single-threaded and multi-threaded runs beyond statistical noise | See `knowledge/multithreading.md` — shared mutable state or SD/field lifecycle bug. |

## General debugging workflow

1. Reduce to the smallest reproducing case: fewer events, `/run/beamOn 1`.
2. Increase verbosity incrementally rather than guessing: `/control/verbose 2`, `/run/verbose 1`, `/event/verbose 1`, `/tracking/verbose 1`, `/process/verbose 1` (and `/process/em/verbose 1` for EM-specific issues).
3. Use `/vis/open` + `/vis/drawVolume` + `/vis/scene/add/trajectories` to visually inspect geometry and the first few tracks — many geometry and source-placement bugs are obvious once seen.
4. Isolate whether an issue is physics-related (swap physics list, or compare `/tracking/verbose 1` output for one event against expectation) or geometry/navigation-related (check overlaps, check the volume hierarchy with `/vis/drawVolume` or `/control/execute` dumping the geometry tree).
5. Only after software correctness is established, move to statistical/physics validation (`knowledge/validation.md`).
