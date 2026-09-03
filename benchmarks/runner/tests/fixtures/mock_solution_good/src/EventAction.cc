#include "EventAction.hh"
#include "G4AnalysisManager.hh"

void EventAction::BeginOfEventAction(const G4Event*) {
    fEdep = 0.0;
}

void EventAction::EndOfEventAction(const G4Event*) {
    G4AnalysisManager::Instance()->FillH1(0, fEdep);
}
