#include "G4RunManagerFactory.hh"
#include "QGSP_BERT.hh"
#include "DetectorConstruction.hh"
#include "ActionInitialization.hh"

int main(int argc, char** argv) {
    auto* runManager = G4RunManagerFactory::CreateRunManager();
    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new QGSP_BERT());
    runManager->SetUserInitialization(new ActionInitialization());
    runManager->Initialize();

    if (argc > 1) {
        G4UImanager::GetUIpointer()->ApplyCommand(G4String("/control/execute ") + argv[1]);
    }

    delete runManager;
    return 0;
}
