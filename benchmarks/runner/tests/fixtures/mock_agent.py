#!/usr/bin/env python3
"""Mock 'agent' for exercising the runner pipeline without a real coding
agent or a Geant4 installation.

Copies a canned fixture solution into the current directory (the run's
workspace, since the runner sets subprocess cwd to the workspace). Which
fixture is copied is controlled by the MOCK_AGENT_QUALITY environment
variable: "good" (default) mimics a mostly-correct submission, "bad" mimics
an incomplete/wrong one -- used to sanity-check that the evaluator actually
discriminates between them.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent
QUALITY = os.environ.get("MOCK_AGENT_QUALITY", "good")
SRC = FIXTURES_DIR / f"mock_solution_{QUALITY}"

if not SRC.exists():
    sys.exit(f"[mock-agent] no fixture solution at {SRC}")

for item in SRC.iterdir():
    dest = Path.cwd() / item.name
    if item.is_dir():
        shutil.copytree(item, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(item, dest)

print(f"[mock-agent] wrote '{QUALITY}' fixture solution into {Path.cwd()}")
