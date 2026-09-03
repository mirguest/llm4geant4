#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"

RunAction::RunAction() {
    auto* analysisManager = G4AnalysisManager::Instance();
    analysisManager->CreateH1("Edep", "Energy deposit in scintillator", 100, 0.0, 10.0 * MeV);
}

void RunAction::BeginOfRunAction(const G4Run*) {
    G4AnalysisManager::Instance()->OpenFile("muonScintillator");
}

void RunAction::EndOfRunAction(const G4Run*) {
    auto* analysisManager = G4AnalysisManager::Instance();
    analysisManager->Write();
    analysisManager->CloseFile();
}
