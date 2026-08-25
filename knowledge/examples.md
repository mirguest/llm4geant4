# Canonical Geant4 Application Patterns

## Minimal application skeleton

Every Geant4 application requires `G4RunManager`, detector construction, physics list, and primary generator action.

```cpp
int main(int argc, char** argv) {
    auto* runManager = G4RunManagerFactory::CreateRunManager(
        G4RunManagerType::Default);

    runManager->SetUserInitialization(new MyDetectorConstruction());
    runManager->SetUserInitialization(new QBBC);
    runManager->SetUserAction(new MyPrimaryGenerator());
    runManager->Initialize();
    runManager->BeamOn(1000);
}
```

## Detector construction

- Inherit from `G4VUserDetectorConstruction`
- Build world volume first, then daughter volumes
- Use `G4NistManager` for standard materials
- Define custom materials with `G4Element` and `G4Material`
- Use `G4PVPlacement` for most placements; `G4PVParameterised` for repeated structures
- Attach sensitive detectors via `G4SDManager` in `ConstructSDandField()`

## Sensitive detector pattern

- Inherit from `G4VSensitiveDetector`
- Override `ProcessHits(G4Step*, G4TouchableHistory*)`
- Create `G4THitsCollection<MyHit>` per event
- Store hits in `G4HCofThisEvent` via `GetCollectionID()`
- Hits should capture: energy deposit, position, time, track ID, particle type

## Primary generator

- Inherit from `G4VUserPrimaryGeneratorAction`
- Use `G4ParticleGun` for simple single-particle sources
- Use `G4GeneralParticleSource` for configurable spectra/spatial distributions
- Set particle type via `G4ParticleTable::GetParticleDefinition()`
- Set energy, position, and momentum direction

## Physics list

- Factory lists (e.g., `QGSP_BERT`, `FTFP_BERT`, `QBBC`) cover most use cases
- For custom physics, inherit from `G4VModularPhysicsList`
- Register particles with `G4ParticleDefinition` constructors
- Register processes with `RegisterPhysics(new G4XxxPhysics())` constructors
- Reference physics lists are in `source/physics_lists/builders/include/`

## User action hooks

| Class | Purpose |
|-------|---------|
| `G4UserRunAction` | BeginOfRunAction, EndOfRunAction — book histograms, write output |
| `G4UserEventAction` | BeginOfEventAction, EndOfEventAction — per-event reset/accumulate |
| `G4UserStackingAction` | ClassifyNewTrack — filter which secondaries get tracked |
| `G4UserTrackingAction` | Pre/PostUserTrackingAction — track-level decisions |
| `G4UserSteppingAction` | UserSteppingAction — per-step monitoring (expensive) |

## Common patterns

- Use `G4AnalysisManager` for histogramming and ntuples (built into Geant4)
- Use `G4UImanager` for macro-based control rather than hardcoding parameters
- Messenger classes (`G4GenericMessenger`) for interactive command registration
- Multi-threading: inherit from `G4VUserActionInitialization` to build worker-local user actions
- Use `G4GDMLParser` to read/write geometry for complex setups
