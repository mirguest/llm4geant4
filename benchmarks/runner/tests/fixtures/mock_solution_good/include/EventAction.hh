#pragma once
#include "G4UserEventAction.hh"

class EventAction : public G4UserEventAction {
public:
    void BeginOfEventAction(const G4Event*) override;
    void EndOfEventAction(const G4Event*) override;
    void AddEdep(G4double edep) { fEdep += edep; }

private:
    G4double fEdep = 0.0;
};
