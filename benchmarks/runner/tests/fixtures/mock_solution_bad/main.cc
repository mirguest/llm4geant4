// Minimal, non-idiomatic submission used only to test that the evaluator
// discriminates between a reasonable and a poor solution. It reproduces
// several of the "common mistakes" from knowledge/development.md on
// purpose: G4RunManager constructed directly, actions registered in
// main(), wrong particle, no physics list reference, no analysis output.

#include "G4RunManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4Material.hh"
#include "G4ParticleGun.hh"

int main() {
    auto* runManager = new G4RunManager();

    auto* air = new G4Material("Air", 1.0, 14.0, 0.0012);
    auto* worldSolid = new G4Box("World", 1000, 1000, 1000); // no units!
    auto* worldLV = new G4LogicalVolume(worldSolid, air, "WorldLV");
    new G4PVPlacement(nullptr, {}, worldLV, "WorldPV", nullptr, false, 0);

    auto* gun = new G4ParticleGun(1);
    // wrong particle, no explicit units, no scintillator volume at all

    runManager->Initialize();
    runManager->BeamOn(10);

    delete runManager;
    return 0;
}
