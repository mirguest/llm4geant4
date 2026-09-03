# Scoring and Output

There are three idiomatic ways to collect per-event quantities (energy deposit, hit position, etc.) in Geant4. Pick based on what the task actually needs — do not default to the most complex one.

## 1. Primitive scorers via `G4MultiFunctionalDetector` (default choice for aggregate quantities)

Use this when you need aggregate per-volume quantities (total energy deposit, dose, particle flux, track length) and do not need per-hit track-level detail. No custom hit class required.

```cpp
auto* detector = new G4MultiFunctionalDetector("ScintillatorSD");
G4SDManager::GetSDMpointer()->AddNewDetector(detector);
detector->RegisterPrimitive(new G4PSEnergyDeposit("edep"));
SetSensitiveDetector("ScintillatorLV", detector); // in ConstructSDandField()
```

Common primitive scorers: `G4PSEnergyDeposit`, `G4PSDoseDeposit`, `G4PSNofStep`, `G4PSTrackLength`, `G4PSNofSecondary`, `G4PSFlatSurfaceCurrent`/`G4PSFlatSurfaceFlux`. Results are read out per event via a `G4THitsMap` obtained from the hits-collection ID (`G4SDManager::GetCollectionID`) in `EventAction::EndOfEventAction`.

This is the simplest correct mechanism for a task like "measure total energy deposited in this volume per event" — prefer it over a hand-rolled stepping-action accumulator.

## 2. Custom sensitive detector (`G4VSensitiveDetector`)

Use this when track-level detail is required per hit (position, time, track ID, particle type, individual step energy deposits) rather than just an aggregate.

- Inherit from `G4VSensitiveDetector`, override `ProcessHits(G4Step*, G4TouchableHistory*)`.
- Define a custom hit class (typically deriving from `G4VHit`) and a `G4THitsCollection<MyHit>`.
- Create the hits collection in `Initialize(G4HCofThisEvent*)`, register it with `G4SDManager` to obtain a collection ID, and store it in `G4HCofThisEvent` so it becomes retrievable from `EventAction`.
- See `knowledge/examples.md` for the class hierarchy summary.

## 3. Stepping-action accumulator

Accumulate a running total directly in `G4UserSteppingAction::UserSteppingAction`, e.g. summing `step->GetTotalEnergyDeposit()` into an event-level (thread-local or event-action-owned) variable, reset in `BeginOfEventAction`.

- Simplest to write for a single scalar quantity, but bypasses `G4SDManager`'s standard hit-collection bookkeeping, so it does not automatically benefit from the merging/output infrastructure the other two approaches get for free.
- Must guard against multithreading races: the accumulator should live in the `EventAction` instance (already thread-local per worker) or be explicitly thread-local — never a plain `static`/global.
- Reach for this only when the scorer/SD machinery is genuine overhead for the task (e.g. a minimal single-quantity example); prefer option 1 for anything that will grow.

## Analysis and output (`G4AnalysisManager`)

`G4AnalysisManager` is the version-agnostic entry point for histogramming/ntuples (it dispatches to a ROOT, XML, CSV, or HDF5 backend depending on configuration):

```cpp
auto* analysisManager = G4AnalysisManager::Instance();
analysisManager->OpenFile("output");
analysisManager->CreateH1("Edep", "Energy deposit", 100, 0., 10. * MeV);
analysisManager->CreateNtuple("Hits", "Per-event hits");
analysisManager->CreateNtupleDColumn("edep");
analysisManager->FinishNtuple();
// ... fill during the run with analysisManager->FillH1(id, value) / FillNtupleDColumn(...) + AddNtupleRow() ...
analysisManager->Write();
analysisManager->CloseFile();
```

- Book histograms/ntuples identically on the master and each worker thread (typically in `RunAction`, called from both `BuildForMaster()` and `Build()` in `ActionInitialization`) — `G4AnalysisManager` handles per-worker files and merges them automatically at end of run when the same structure is booked consistently.
- The output file format can be chosen at compile time (which manager headers are included) or partly at run time via macro commands like `/analysis/setDefaultFileType`.
- For arbitrary run-level scalar accumulation across threads (not going into a histogram), prefer `G4Accumulable` + `G4AccumulableManager`: register accumulables once in `RunAction`, update them per event/step, and they merge into the master automatically at `EndOfRunAction` — this avoids hand-writing a thread-safe `Merge()` on a custom `G4Run` subclass unless something more complex than simple sums/means is needed.
