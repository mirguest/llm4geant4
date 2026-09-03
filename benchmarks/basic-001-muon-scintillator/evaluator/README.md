# Evaluator

`evaluate.py` implements automated (heuristic) scoring for this benchmark's `rubric.yaml`. It is loaded dynamically by `benchmarks/runner/lib/scoring.py` — see `benchmarks/runner/README.md` for how to run it as part of a full agent/model comparison.

## What is actually automated

- **Static source checks** (`geometry`, `primary_source`, `physics`, `energy_scoring`, `idiomatic_geant4`): regex/keyword checks across the submitted source files. These are a fast triage signal, not semantic verification — a submission could reference the right keywords without correct behavior.
- **Build and run** (`build_and_run`): attempted for real with `cmake`/`make` when `geant4-config` is available in the evaluation environment. Falls back to a structural presence check (are `CMakeLists.txt`, a `.mac` file, and source files present) when Geant4 isn't installed where the evaluator runs, and flags the criterion `manual_review` in that case.
- **Output** (`output`): scored from an actual produced `.root`/`.aida` file when a real build+run succeeded; otherwise falls back to a static check for `G4AnalysisManager` usage and flags `manual_review`.
- **Physics plausibility** (`physics_plausibility`): always flagged `manual_review`. Confirming the mean energy deposit is physically sensible requires actually running the application and reading the resulting histogram (e.g. with `uproot` against the ROOT output) — this evaluator does not attempt that yet.

## Design constraint

The evaluator works with output from any coding agent — it operates on the generated source files and simulation output and does not need to know which agent produced them.

## Planned next steps

- Once a frozen `reference/` run exists, extract the reference mean/spread and use it to score `physics_plausibility` automatically (with a defined tolerance) instead of always deferring to manual review.
- Compare geometry more precisely (parse actual `G4Box` construction arguments rather than keyword presence).
- Add an LLM-judge pass (see `benchmarks/runner/README.md`) for the criteria that remain `manual_review` here.
