# Geant4 Development Workflow

## Build system

Use CMake with Geant4's built-in support:

```cmake
cmake_minimum_required(VERSION 3.16)
project(MySimulation)

find_package(Geant4 REQUIRED)
include(${Geant4_USE_FILE})

add_executable(myapp myapp.cc src/MyDetectorConstruction.cc ...)
target_link_libraries(myapp ${Geant4_LIBRARIES})
```

For applications with multiple source files, use a conventional layout:

```
MyApp/
├── CMakeLists.txt
├── myapp.cc
├── include/
│   ├── MyDetectorConstruction.hh
│   ├── MyPrimaryGenerator.hh
│   ├── MyActionInitialization.hh
│   └── MySensitiveDetector.hh
└── src/
    ├── MyDetectorConstruction.cc
    ├── MyPrimaryGenerator.cc
    ├── MyActionInitialization.cc
    └── MySensitiveDetector.cc
```

Header guards: use `#pragma once` or traditional `#ifndef` guards. Include Geant4 headers as `#include "G4RunManager.hh"`.

## Environment setup

Source the Geant4 environment script before building:

```bash
source /path/to/geant4/bin/geant4.sh
```

Verify the version:

```bash
geant4-config --version
```

Or use `Geant4Config.cmake` with `-DGeant4_DIR=/path/to/geant4/lib/Geant4-11.X`.

## Iterative development cycle

```text
understand the problem
→ find the closest official Geant4 example
→ make a small change
→ build
→ run a small test (few events)
→ inspect output
→ validate physics plausibility
→ repeat
```

### Step by step

1. **Understand** — clarify what is being simulated, what observables matter, what physics processes are relevant
2. **Find example** — check `examples/` in the Geant4 installation for the closest match to your use case
3. **Make a small change** — one class, one volume, one detector at a time
4. **Build** — `cmake .. && make -j$(nproc)` in the build directory
5. **Run a small test** — 10 events is enough; use `/tracking/verbose 1` for the first few
6. **Inspect** — check the output, histograms, log messages
7. **Validate** — does the result make physical sense? If not, investigate before scaling up

Do not attempt to write the entire application in one pass. Iteration catches mistakes early and builds confidence.

## Interactive debugging

Run the application in its interactive mode. Use Geant4 UI and visualization commands to inspect the geometry and a few events:

```
/vis/open
/vis/drawVolume
/vis/scene/add/trajectories
/run/beamOn 1
/tracking/verbose 1
```

## Common mistakes to avoid

- Forgetting to call `SetSensitiveDetector()` on logical volumes that need hits
- Using `new` in ConstructSDandField without registering with `G4SDManager`
- Failing to set materials on the world volume
- Not defining particles before processes in custom physics lists
- Using the wrong coordinate system with G4 rotation matrices
- Not checking overlaps with `/geometry/test/run`
- Accumulating results in stepping action without guarding against per-thread race conditions
- Registering user actions directly in `main()` instead of through `G4VUserActionInitialization` (breaks MT)
- Directly constructing `G4RunManager` or `G4MTRunManager` instead of using `G4RunManagerFactory::CreateRunManager()`
- Using `cout` instead of `G4cout` (not thread-safe)
