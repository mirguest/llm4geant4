#include "PrimaryGeneratorAction.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() {
    fGun = new G4ParticleGun(1);
    auto* particle = G4ParticleTable::GetParticleTable()->FindParticle("mu-");
    fGun->SetParticleDefinition(particle);
    fGun->SetParticleEnergy(1.0 * GeV);
    fGun->SetParticleMomentumDirection(G4ThreeVector(0, 0, 1));
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) {
    G4double x = (G4UniformRand() - 0.5) * 1.0 * cm;
    G4double y = (G4UniformRand() - 0.5) * 1.0 * cm;
    fGun->SetParticlePosition(G4ThreeVector(x, y, -50.0 * cm));
    fGun->GeneratePrimaryVertex(event);
}
