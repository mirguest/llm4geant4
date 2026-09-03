#pragma once
#include "G4UserRunAction.hh"

class RunAction : public G4UserRunAction {
public:
    RunAction();
    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;
};
