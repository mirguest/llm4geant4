# Geant4 Development Workflow

## Build system

Use CMake with Geant4's built-in support:

```cmake
cmake_minimum_required(VERSION 3.16)
project(MySimulation)

find_package(Geant4 REQUIRED)
include(${Geant4_USE_FILE})

add_executable(myapp myapp.cc)
target_link_libraries(myapp ${Geant4_LIBRARIES})
```

Enable multi-threading in the application, not in the build:
```cpp
G4MTRunManager* rm = new G4MTRunManager();
rm->SetNumberOfThreads(n);
```

## Typical development iteration

1. **Define geometry** — write `DetectorConstruction`, verify with `/vis/drawVolume`
2. **Set physics** — choose factory physics list or build custom
3. **Generate primaries** — configure source via `GPS` or `ParticleGun`
4. **Add sensitive detectors** — instrument volumes that matter
5. **Add output** — histogram energy spectra, fill ntuples
6. **Run batch** — use macros with `/run/beamOn N`
7. **Validate** — compare against known energy deposits, ranges, and cross sections

## Interactive debugging

Launch with visualization:
```bash
./myapp -g           # Qt viewer (requires Qt build of Geant4)
./myapp              # Terminal-only, control via /run/ commands
```

Useful UI commands:
```
/vis/drawVolume
/vis/scene/add/trajectories
/run/beamOn 1
/tracking/verbose 1
```

## Common mistakes to avoid

- Forgetting to call `SetSensitiveDetector()` on logical volumes
- Using `new` in ConstructSDandField without registering with `G4SDManager`
- Failing to set materials on the world volume
- Not defining particles before processes in custom physics lists
- Using the wrong coordinate system (G4 rotation matrices)
- Not checking overlaps with `/geometry/test/run`
- Accumulating results in stepping action without guarding against per-thread race conditions
- Hardcoding the number of threads without checking `G4Threading::G4GetNumberOfCores()`

## Code organization

For applications beyond a single file:
```
MyApp/
├── CMakeLists.txt
├── myapp.cc
├── include/
│   ├── MyDetectorConstruction.hh
│   ├── MyPrimaryGenerator.hh
│   └── MySensitiveDetector.hh
└── src/
    ├── MyDetectorConstruction.cc
    ├── MyPrimaryGenerator.cc
    └── MySensitiveDetector.cc
```

Header guards: use `#pragma once` or traditional `#ifndef` guards. Include Geant4 headers as `#include "G4RunManager.hh"`.

## Environment setup

Source the Geant4 environment script before building:
```bash
source /path/to/geant4/bin/geant4.sh
```

Or use `Geant4Config.cmake` with `-DGeant4_DIR=/path/to/geant4/lib/Geant4-version`.
