# Geant4 Geometry

## Solids

- **CSG primitives** — `G4Box`, `G4Tubs`, `G4Sphere`, `G4Cons`, `G4Trd`, `G4Trap`, `G4Orb`, `G4Torus`. Prefer these for simple shapes; they are fast to navigate.
- **Specific solids** — `G4Polycone`, `G4Polyhedra` (arbitrary z-sections), `G4GenericTrap`, `G4ExtrudedSolid` (2D polygon extrusion), `G4TwistedBox`/`G4TwistedTrap` for twisted shapes.
- **Boolean solids** — `G4UnionSolid`, `G4SubtractionSolid`, `G4IntersectionSolid` combine two solids with a relative transform. Nest sparingly: deeply nested booleans are expensive to navigate and can produce degenerate surfaces if the operands only just touch. Prefer a native solid when one exists instead of building it from booleans.
- **Imported meshes** — `G4TessellatedSolid` or CAD import (e.g. via GDML or the community CADMesh library) for shapes with no analytic description. These are the slowest to navigate; use only when necessary.

## Logical and physical volumes

- `G4LogicalVolume(solid, material, name)` binds shape + material. It also carries optional `G4VisAttributes`, `G4UserLimits` (e.g. `SetMaxAllowedStep` to force fine stepping in a thin or field region), and a `G4FieldManager` for a local field.
- Placement choices:
  - `G4PVPlacement` — a single, individually placed copy. Use for one-off volumes.
  - `G4PVReplica` — N identical, non-overlapping divisions of a mother volume along an axis (kXAxis/kYAxis/kZAxis/kRAxis/kPhiAxis), all sharing one logical volume. Fast and memory-cheap; use for regular segmentation (e.g. calorimeter layers, wire planes).
  - `G4PVParameterised` — like a replica but each copy can differ (size, material, transform) via a `G4VPVParameterisation` subclass implementing `ComputeTransformation`/`ComputeDimensions`. Use for systematically varying repeated structures (e.g. a wedge-shaped calorimeter, staggered tracker layers). For very large counts of near-identical volumes, prefer replicas/parameterised volumes over thousands of individual `G4PVPlacement` calls — it keeps navigation voxelization efficient and avoids the memory cost of one physical-volume object per copy.
- **Placement pitfalls**:
  - The position passed to `G4PVPlacement` is the daughter's origin *in the mother's frame*.
  - The rotation is applied to the *frame*, not intuitively to the object: `G4RotationMatrix` passed to `G4PVPlacement` rotates the mother's axes to obtain the daughter's local axes (an "active" rotation of the frame). If a placed object appears rotated the wrong way, try the inverse rotation before suspecting anything else.
  - A daughter volume must be geometrically contained entirely within its mother. Partial overlap between mother/daughter or between two siblings leads to undefined navigation behavior — tracks can jump, get stuck, or silently skip volumes.

## Overlap checking

- Run `/geometry/test/run` after construction to sample points and report overlapping placements.
- Pass `true` as the last constructor argument to `G4PVPlacement` (`checkOverlaps`) to have it self-check at construction time against sibling volumes (samples a fixed number of surface points — useful during development, disable for production runs since it adds startup cost).
- Overlaps are one of the most common sources of "physically implausible" results (double-counted energy deposit, particles disappearing) without any crash, so check early, not only when something looks wrong.

## Regions

- `G4Region` groups logical volumes for regional physics configuration: production cuts (`G4ProductionCuts` + `region->SetProductionCuts(cuts)`), user limits, or biasing.
- Attach a region to a logical volume subtree with `logicalVolume->SetRegion(region)` and `region->AddRootLogicalVolume(logicalVolume)`. A finer cut in a thin detector region (e.g. a thin scintillator or tracker layer) is often necessary to get correct energy deposition — the global default cut can be too coarse to produce secondaries inside a thin volume at all.

## Fields

- Attach a magnetic (or EM) field via a `G4FieldManager` set on the world logical volume (global field) or on a specific logical volume (local field, overriding the parent's).
- Typical chain: field object (e.g. `G4UniformMagField`) → equation of motion (`G4Mag_UsualEqRhs`) → stepper (`G4ClassicalRK4`, `G4DormandPrince745`, ...) → `G4ChordFinder` → `G4FieldManager`.
- In a field region, set a sensible `G4UserLimits` max step and driver accuracy (`SetDeltaChord`, `SetMinimumEpsilonStep`); otherwise stepping can become extremely slow or numerically unstable in strong or highly non-uniform fields.

## GDML

- `G4GDMLParser` reads (`Read(file)`) and writes (`Write(file, logicalVolume)`) geometry in GDML for interchange with ROOT, CAD tools, or other Geant4 applications. Useful for decoupling geometry description from application code, or for large/complex geometries maintained outside the source tree.

## Geometry lifecycle

- The geometry is "closed" (optimized/voxelized) once the run manager initializes it (`Initialize()` or the first `BeamOn`). The `Construct()` method of `G4VUserDetectorConstruction` must return the world physical volume — a `nullptr` or missing return is a common source of an immediate crash.
- If placements must change after initialization, call `G4RunManager::GetRunManager()->GeometryHasBeenModified()` (or the `/run/geometryModified` UI command) so the geometry is re-closed before the next run; otherwise stale navigation history can cause incorrect results.

## Common mistakes

- Not setting a material on the world (or any) logical volume.
- Building daughter volumes larger than their mother, or with the wrong mother-frame offset (units left off, or fraction of the actual mm value).
- Forgetting `checkOverlaps` during development, only to debug a physics anomaly caused by an overlap much later.
- Confusing `G4PVReplica` (identical copies, no per-copy parameterisation) with `G4PVParameterised` (per-copy variation) and hand-building a loop of individual placements instead of either.
