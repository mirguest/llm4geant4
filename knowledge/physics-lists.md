# Geant4 Physics Lists

## Choosing a reference physics list

Factory (“reference”) physics lists cover most applications. Do not hand-roll a physics list unless there is a specific reason (custom EM precision, custom hadronic model mix, biasing, optical-only simulation).

| List | Typical use |
|---|---|
| `FTFP_BERT` | General HEP default; FTF string model + Bertini cascade. Good general-purpose starting point above a few hundred MeV. |
| `QGSP_BERT` | Quark-gluon string model at high energy + Bertini cascade; historically common for collider/cosmic-ray applications. |
| `QGSP_BIC` / `QGSP_BIC_HP` | Binary cascade instead of Bertini for intermediate-energy hadron/ion interactions; `_HP` variants use high-precision (evaluated data library) neutron transport below ~20 MeV — needed for accurate low-energy neutron work but requires the `G4NDL` (Neutron Data Library) dataset to be installed and `G4NEUTRONHPDATA` set. |
| `QBBC` | Quark-gluon string + Binary + Bertini + FTF mix tuned as another general-purpose default. |
| `Shielding` | Radiation shielding / dosimetry: HP neutron transport, radioactive decay, tuned low-energy hadronic models. |
| `FTFP_BERT_HP` | `FTFP_BERT` with high-precision neutron transport. |

If unsure which to pick, `FTFP_BERT` or `QBBC` are safe general defaults; switch to a `_HP` or `Shielding`-family list once low-energy neutron transport accuracy matters, and re-run validation before trusting results.

## Instantiating a physics list

```cpp
runManager->SetUserInitialization(new FTFP_BERT());
```

Alternatively, build by name at runtime with `G4PhysListFactory` (useful for letting the physics list be a run-time/macro choice rather than a compile-time one):

```cpp
G4PhysListFactory factory;
runManager->SetUserInitialization(factory.GetReferencePhysList("FTFP_BERT"));
```

## Building a custom modular list

Inherit from `G4VModularPhysicsList` and register constructors; each is called in registration order for both `ConstructParticle()` and `ConstructProcess()`:

```cpp
class MyPhysicsList : public G4VModularPhysicsList {
public:
    MyPhysicsList() {
        RegisterPhysics(new G4EmStandardPhysics());
        RegisterPhysics(new G4DecayPhysics());
        RegisterPhysics(new G4RadioactiveDecayPhysics());
        RegisterPhysics(new G4HadronPhysicsFTFP_BERT());
        RegisterPhysics(new G4HadronElasticPhysics());
        RegisterPhysics(new G4IonPhysics());
    }
};
```

Reference hadronic physics builders live in `source/physics_lists/builders/include/` of the Geant4 source tree — the factory lists are themselves thin compositions of these builders, and are a good reference for constructing a custom list.

## EM physics options

`G4EmStandardPhysics` (option "0", the default used by most factory lists) is a reasonable general choice. More accurate — and slower — alternatives exist for specific regimes:

- `G4EmStandardPhysics_option3` / `_option4` — higher-accuracy multiple scattering and EM cross sections, common for precision tracking detectors.
- `G4EmStandardPhysicsSS` / `_WVI` / `_GS` — alternative multiple-scattering models.
- `G4EmLivermorePhysics` / `G4EmPenelopePhysics` — low-energy precision EM (down to ~100 eV–1 keV), used for medical physics, space science, low-energy X-ray work.
- `G4EmDNAPhysics` — track-structure physics for radiobiology/DNA-damage simulation (sub-keV scale, very fine stepping — expensive).

Swap the EM constructor in a custom `G4VModularPhysicsList` rather than modifying a factory list.

## Optical physics

Register `G4OpticalPhysics` as an additional physics constructor (`RegisterPhysics(new G4OpticalPhysics())`). Optical photon transport further requires:

- A `G4MaterialPropertiesTable` on relevant materials with properties such as `RINDEX` (refractive index vs. energy), `ABSLENGTH`, and, for scintillators, `SCINTILLATIONYIELD`/`SCINTILLATIONCOMPONENT1` etc.
- Boundary properties via `G4OpticalSurface` attached with `G4LogicalBorderSurface` (between two specific placed volumes) or `G4LogicalSkinSurface` (all boundaries of one logical volume) — needed for reflection/refraction behavior (polish, reflectivity, specular vs. diffuse lobes) that isn't purely determined by refractive index mismatch.
- Cerenkov and scintillation are opted into automatically once the relevant material properties are present; they do not need separate registration beyond `G4OpticalPhysics`.

## Production cuts

- Production cuts (range cuts) set the secondary-production threshold, converted internally to an energy threshold per particle/material/region — not a hard interaction cutoff. `G4VUserPhysicsList`'s default cut is conventionally `1 mm` unless a list overrides it; do not assume a specific value without checking (`/run/getCutValue`, `/run/dumpCouples`, or `G4EmParameters` and the physics list's own `SetCuts()`).
- Region-specific cuts: build a `G4Region`, assign a `G4ProductionCuts` object with `SetProductionCut(value, particleName)` (or `SetProductionCut(value)` for all particles), and attach to a logical-volume subtree. This matters for thin sensitive volumes — a coarse global cut can suppress secondary production entirely inside a volume thinner than the cut's equivalent range, biasing the deposited-energy distribution.
- `G4EmParameters::Instance()` exposes fine-grained tuning (e.g. `SetMinEnergy`, `SetLowestElectronEnergy`) if the default energy range needs adjusting — rarely necessary for standard applications.

## Biasing

For variance reduction (e.g. deep shielding problems where the interesting events are rare), wrap the physics list's processes with `G4GenericBiasingPhysics` rather than modifying transport by hand, and drive it with the biasing operator/manager classes (`G4VBiasingOperator`, importance sampling via `G4IStore`/weight windows). Reach for biasing only once an unbiased run is confirmed too slow for the required statistical precision — it adds real complexity and needs its own validation (unbiased mean must be recovered).
