# Geant4 Multithreading

## Run manager

- Always create the run manager via `G4RunManagerFactory::CreateRunManager()`. It automatically selects MT mode if Geant4 was built with `G4MULTITHREADED` and falls back to serial otherwise — application code does not need to branch on this.
- Control the worker thread count with the `/run/numberOfThreads N` UI command (or the corresponding constructor/setter) before `Initialize()`. Do not hardcode a thread count the deployment environment may not have; a sensible default is fine.

## Master vs. worker responsibilities

- `G4VUserDetectorConstruction::Construct()` runs once, on the master; the resulting geometry (solids, logical volumes) is shared read-only across worker threads. Per-thread navigation state is handled internally by Geant4 — application code does not need to duplicate geometry.
- `ConstructSDandField()` runs once **per worker thread**. Sensitive detectors and field managers can hold thread-relevant state, so instantiate and register them there — not in `Construct()`. A sensitive detector created only in `Construct()` (or only on the master) will not be attached to worker-thread instances of the logical volume, and hits will silently go missing on multi-threaded runs while looking correct in single-threaded mode. This is one of the most common MT-vs-serial discrepancy bugs.
- User actions (`PrimaryGeneratorAction`, `RunAction`, `EventAction`, `SteppingAction`, ...) must be created through `G4VUserActionInitialization::Build()` (called once per worker) so each thread gets its own instances. `BuildForMaster()` is for master-only actions (e.g. a `RunAction` that only merges/writes final output). Registering actions directly via `runManager->SetUserAction()` in `main()` instead of through `G4VUserActionInitialization` breaks this per-thread instantiation.

## Shared mutable state

- Avoid `static` (non-thread-local) mutable variables in detector construction, stepping/event/run actions, or sensitive detectors — they are shared across worker threads without automatic synchronization and are a direct source of races and non-reproducible results.
- Use `G4ThreadLocal` for state that genuinely needs one instance per thread but can't naturally live in an already-per-thread object (rare if actions are built correctly through `G4VUserActionInitialization`).
- For state that truly must be shared and mutated across threads (e.g. writing to one shared external log/file, or a shared cache), protect access with `G4AutoLock` and a `G4Mutex` — do this only where necessary; global locking around per-event work destroys the benefit of MT.
- Prefer `G4Accumulable`/`G4AccumulableManager` (see `knowledge/scoring-and-output.md`) or `G4AnalysisManager`'s built-in merging over hand-rolled cross-thread accumulation — both handle the thread-safety for you.

## I/O and console

- Use `G4cout`/`G4cerr`, never `std::cout`/`std::cerr` — Geant4 synchronizes and (optionally) thread-prefixes its own streams; plain `std::cout` output from multiple workers can interleave mid-line.
- Each worker typically writes its own output file (e.g. via `G4AnalysisManager`), merged at end-of-run; avoid multiple threads opening/writing the same file path directly.

## Random numbers

- The run manager seeds each worker thread's RNG stream independently and reproducibly (derived from the master seed) — do not manually reseed per-event or per-thread from user code unless intentionally implementing a custom reproducibility scheme, as this can silently destroy independence between worker streams.
- Set the master seed once (e.g. `G4Random::setTheSeed(...)` before `Initialize()`, or `/random/setSeeds`) for reproducible runs; document the seed alongside results per the reproducibility checklist in `knowledge/validation.md`.

## Debugging MT-specific issues

- If results differ between single-threaded (`/run/numberOfThreads 1` or a serial build) and multi-threaded runs beyond expected statistical fluctuation, first suspect: sensitive detectors/fields registered in the wrong lifecycle method, shared mutable static state, or a stepping-action accumulator that isn't actually thread-local.
- Running with a single thread first (before scaling up) is a fast way to separate "wrong physics/geometry" bugs from "wrong MT wiring" bugs.
