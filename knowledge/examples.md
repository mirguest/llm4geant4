# Canonical Geant4 Application Patterns

## Application skeleton

Use `G4RunManagerFactory` to create the run manager. This supports both sequential and MT modes without changing application code:

```cpp
auto* runManager = G4RunManagerFactory::CreateRunManager();
```

For multi-threading-aware applications, use `G4VUserActionInitialization` to build worker-local user actions:

```cpp
class MyActionInitialization : public G4VUserActionInitialization {
public:
    void BuildForMaster() const override {
        SetUserAction(new MyRunAction());
    }
    void Build() const override {
        SetUserAction(new MyPrimaryGeneratorAction());
        SetUserAction(new MyRunAction());
        SetUserAction(new MyEventAction());
    }
};
```

In `main()`:

```cpp
auto* runManager = G4RunManagerFactory::CreateRunManager();
runManager->SetUserInitialization(new MyDetectorConstruction());
runManager->SetUserInitialization(new QGSP_BERT);
runManager->SetUserInitialization(new MyActionInitialization());
runManager->Initialize();
runManager->BeamOn(1000);
```

Do not register user actions directly in `main()` via `runManager->SetUserAction()` if you want the application to work correctly with multi-threading. Always route them through `G4VUserActionInitialization`.

## Detector construction

- Inherit from `G4VUserDetectorConstruction`
- Build world volume first, then daughter volumes
- Use `G4NistManager` for standard materials (e.g., `G4_PLASTIC_SC_VINYLTOLUENE`, `G4_AIR`)
- Define custom materials with `G4Element` and `G4Material` only when needed
- Use `G4PVPlacement` for most placements; `G4PVParameterised` for repeated structures
- Attach sensitive detectors via `G4SDManager` in `ConstructSDandField()`

## Sensitive detector pattern

- Inherit from `G4VSensitiveDetector`
- Override `ProcessHits(G4Step*, G4TouchableHistory*)`
- Create `G4THitsCollection<MyHit>` per event
- Store hits in `G4HCofThisEvent` via `GetCollectionID()`
- Hits should capture: energy deposit, position, time, track ID, particle type

## Primary generator

- Inherit from `G4VUserPrimaryGeneratorAction` (placed in action initialization)
- Use `G4ParticleGun` for simple single-particle sources
- Use `G4GeneralParticleSource` for configurable spectra/spatial distributions
- Set particle type via `G4ParticleTable::GetParticleDefinition()`
- Set energy, position, and momentum direction with explicit Geant4 units:
  ```cpp
  gun->SetParticleEnergy(1.0 * GeV);
  gun->SetParticlePosition(G4ThreeVector(0., 0., -50.0 * cm));
  ```

## Physics list

- Factory lists (e.g., `QGSP_BERT`, `FTFP_BERT`, `QBBC`) cover most use cases
- For custom physics, inherit from `G4VModularPhysicsList`
- Register particles before processes
- Reference physics lists are in `source/physics_lists/builders/include/`

## User action hooks

| Class | Purpose |
|-------|---------|
| `G4UserRunAction` | BeginOfRunAction, EndOfRunAction — book histograms, write output |
| `G4UserEventAction` | BeginOfEventAction, EndOfEventAction — per-event reset/accumulate |
| `G4UserStackingAction` | ClassifyNewTrack — filter which secondaries get tracked |
| `G4UserTrackingAction` | Pre/PostUserTrackingAction — track-level decisions |
| `G4UserSteppingAction` | UserSteppingAction — per-step monitoring (expensive, beware MT races) |

All user actions should be created inside `G4VUserActionInitialization::Build()` for MT safety.

## Units

Always use explicit Geant4 units:

```cpp
1.0 * GeV
10.0 * cm
0.5 * mm
```

Do not rely on Geant4's internal unit system being mm/MeV — use the named units.

## Common patterns

- Use `G4AnalysisManager` for histogramming and ntuples (built into Geant4)
- Use `G4UImanager` for macro-based control rather than hardcoding parameters
- Messenger classes (`G4GenericMessenger`) for interactive command registration
- Use `G4GDMLParser` to read/write geometry for complex setups
