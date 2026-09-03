#include "SteppingAction.hh"
#include "EventAction.hh"
#include "G4Step.hh"

void SteppingAction::UserSteppingAction(const G4Step* step) {
    if (step->GetPreStepPoint()->GetPhysicalVolume()->GetName() != "ScintillatorPV") return;
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep > 0.0) fEventAction->AddEdep(edep);
}
