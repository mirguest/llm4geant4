#pragma once
#include "G4UserSteppingAction.hh"

class EventAction;

class SteppingAction : public G4UserSteppingAction {
public:
    explicit SteppingAction(EventAction* eventAction) : fEventAction(eventAction) {}
    void UserSteppingAction(const G4Step* step) override;

private:
    EventAction* fEventAction;
};
