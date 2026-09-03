#include "DetectorConstruction.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"

G4VPhysicalVolume* DetectorConstruction::Construct() {
    auto* nist = G4NistManager::Instance();
    auto* air = nist->FindOrBuildMaterial("G4_AIR");
    auto* scintMat = nist->FindOrBuildMaterial("G4_PLASTIC_SC_VINYLTOLUENE");

    auto* worldSolid = new G4Box("World", 60.0 * cm, 60.0 * cm, 60.0 * cm); // 120 cm full width
    auto* worldLV = new G4LogicalVolume(worldSolid, air, "WorldLV");
    auto* worldPV = new G4PVPlacement(nullptr, {}, worldLV, "WorldPV", nullptr, false, 0);

    auto* scintSolid = new G4Box("Scintillator", 5.0 * cm, 5.0 * cm, 0.5 * cm); // 10cm x 10cm x 1cm
    auto* scintLV = new G4LogicalVolume(scintSolid, scintMat, "ScintillatorLV");
    new G4PVPlacement(nullptr, G4ThreeVector(0, 0, 0), scintLV, "ScintillatorPV", worldLV, false, 0);

    return worldPV;
}
