"""Automated (heuristic) scoring for the basic-001-muon-scintillator benchmark.

This module is loaded dynamically by benchmarks/runner/lib/scoring.py. It
implements `evaluate(workspace, benchmark_dir) -> dict` as documented there.

Scope and honesty about limitations:

- Criteria that can be checked by actually building and running the
  application (`build_and_run`, and confirming `output` was produced) are
  only scored with confidence when a Geant4 installation is available in
  the evaluation environment (`geant4-config` on PATH). Otherwise they fall
  back to static structural checks and are flagged `manual_review`.
- Criteria that require physics judgment on the actual output distribution
  (`physics_plausibility`) require a Geant4 + ROOT (or uproot) environment
  to extract real numbers; without that, `physics_plausibility` is always
  flagged `manual_review`.
- All other criteria are scored via static source-code inspection (regex
  keyword/pattern checks across the submitted source files). This is a
  heuristic proxy, not semantic verification -- it can be fooled by a
  submission that mentions the right keywords without correct behavior.
  Treat automated scores as a fast triage signal, not a final grade.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

SOURCE_GLOBS = ("*.cc", "*.cpp", "*.cxx", "*.hh", "*.hpp", "*.h", "*.mac", "CMakeLists.txt")


def _gather_source(workspace: Path) -> str:
    chunks = []
    for pattern in SOURCE_GLOBS:
        for path in workspace.rglob(pattern):
            try:
                chunks.append(path.read_text(errors="ignore"))
            except OSError:
                continue
    return "\n".join(chunks)


def _weighted_score(text: str, checks: list[tuple[float, str, str]], max_points: float) -> tuple[float, list[str]]:
    """checks: list of (weight, regex_pattern, description). Weights should sum to ~1.0."""
    earned = 0.0
    notes = []
    for weight, pattern, description in checks:
        if re.search(pattern, text, re.IGNORECASE):
            earned += weight
            notes.append(f"found: {description}")
        else:
            notes.append(f"missing: {description}")
    return round(earned * max_points, 1), notes


def _check_geometry(text: str, max_points: float) -> tuple[float, str]:
    checks = [
        (0.35, r"G4_PLASTIC_SC_VINYLTOLUENE", "NIST plastic scintillator material"),
        (0.2, r"120\.?0?\s*\*?\s*cm", "120 cm world dimension"),
        (0.25, r"10\.?0?\s*\*?\s*cm", "10 cm scintillator lateral dimension"),
        (0.2, r"G4NistManager", "standard material lookup via G4NistManager"),
    ]
    score, notes = _weighted_score(text, checks, max_points)
    return score, "; ".join(notes)


def _check_primary_source(text: str, max_points: float) -> tuple[float, str]:
    checks = [
        (0.3, r'"mu-"', "mu- particle name"),
        (0.25, r"1\.?0?\s*\*?\s*GeV", "1 GeV energy"),
        (0.2, r"-\s*50\.?0?\s*\*?\s*cm", "z = -50 cm source position"),
        (0.25, r"G4UniformRand|Rndm\(\)", "randomized transverse (XY) source position"),
    ]
    score, notes = _weighted_score(text, checks, max_points)
    return score, "; ".join(notes)


def _check_physics(text: str, max_points: float) -> tuple[float, str]:
    if re.search(r"QGSP_BERT", text):
        return max_points, "found: QGSP_BERT physics list"
    return 0.0, "missing: QGSP_BERT physics list"


def _check_energy_scoring(text: str, max_points: float) -> tuple[float, str]:
    checks = [
        (0.5, r"GetTotalEnergyDeposit|G4PSEnergyDeposit|MultiFunctionalDetector", "an energy-deposit scoring mechanism"),
        (0.25, r"BeginOfEventAction", "per-event reset/accumulation hook"),
        (0.25, r"FillH1|FillNtupleDColumn|FillNtupleFColumn", "filling a histogram/ntuple with the result"),
    ]
    score, notes = _weighted_score(text, checks, max_points)
    return score, "; ".join(notes)


def _check_output(workspace: Path, text: str, max_points: float, build_succeeded: bool | None) -> tuple[float, str, bool]:
    produced_files = list(workspace.rglob("*.root")) + list(workspace.rglob("*.aida"))
    if build_succeeded and produced_files:
        names = ", ".join(p.name for p in produced_files[:3])
        return max_points, f"found: run produced output file(s) ({names})", False

    checks = [
        (0.6, r"G4AnalysisManager", "use of G4AnalysisManager"),
        (0.2, r"OpenFile|CloseFile|->Write\(\)", "explicit open/write/close of the output file"),
        (0.2, r"CreateH1|CreateNtuple", "a booked histogram or ntuple"),
    ]
    score, notes = _weighted_score(text, checks, max_points)
    note = "; ".join(notes) + "; not verified by an actual run in this environment"
    return score, note, True


def _check_idiomatic(text: str, max_points: float) -> tuple[float, str]:
    checks = [
        (0.4, r"G4RunManagerFactory", "G4RunManagerFactory::CreateRunManager()"),
        (0.3, r"G4VUserActionInitialization", "action registration via G4VUserActionInitialization"),
        (0.3, r"\*\s*(cm|mm|GeV|MeV|keV|ns|ms)\b", "explicit Geant4 unit multipliers"),
    ]
    score, notes = _weighted_score(text, checks, max_points)
    return score, "; ".join(notes)


def _try_build_and_run(workspace: Path) -> tuple[float | None, str, bool]:
    """Attempt an actual build + short run if Geant4 is available. Returns
    (score_or_None, notes, manual_review)."""
    if shutil.which("geant4-config") is None:
        has_cmake = (workspace / "CMakeLists.txt").exists()
        has_macro = any(workspace.rglob("*.mac"))
        has_source = any(workspace.rglob("*.cc")) or any(workspace.rglob("*.cpp"))
        structural = sum([has_cmake, has_macro, has_source]) / 3
        return (
            None,
            "Geant4 not available in this evaluation environment; build/run not attempted. "
            f"Structural presence only (CMakeLists.txt={has_cmake}, macro={has_macro}, source={has_source}, "
            f"~{structural:.0%} of expected files present).",
            True,
        )

    build_dir = workspace / "_build"
    build_dir.mkdir(exist_ok=True)
    try:
        configure = subprocess.run(
            ["cmake", ".."], cwd=build_dir, capture_output=True, text=True, timeout=300
        )
        if configure.returncode != 0:
            return 0.0, f"cmake configure failed: {configure.stderr[-500:]}", False
        build = subprocess.run(
            ["make", "-j2"], cwd=build_dir, capture_output=True, text=True, timeout=600
        )
        if build.returncode != 0:
            return 0.0, f"build failed: {build.stderr[-500:]}", False
    except subprocess.TimeoutExpired:
        return 0.0, "build timed out", False
    except FileNotFoundError as exc:
        return None, f"could not invoke build tools: {exc}", True

    return 15.0, "cmake configure and build both succeeded", False


def evaluate(workspace: Path, benchmark_dir: Path) -> dict:
    text = _gather_source(workspace)
    results = {}

    build_score, build_notes, build_manual = _try_build_and_run(workspace)
    build_succeeded = build_score == 15.0 if build_score is not None else None
    results["build_and_run"] = {"score": build_score if build_score is not None else 0.0, "notes": build_notes, "manual_review": build_manual}

    score, notes = _check_geometry(text, 15)
    results["geometry"] = {"score": score, "notes": notes, "manual_review": False}

    score, notes = _check_primary_source(text, 15)
    results["primary_source"] = {"score": score, "notes": notes, "manual_review": False}

    score, notes = _check_physics(text, 10)
    results["physics"] = {"score": score, "notes": notes, "manual_review": False}

    score, notes = _check_energy_scoring(text, 20)
    results["energy_scoring"] = {"score": score, "notes": notes, "manual_review": False}

    score, notes, manual = _check_output(workspace, text, 10, build_succeeded)
    results["output"] = {"score": score, "notes": notes, "manual_review": manual}

    results["physics_plausibility"] = {
        "score": 0.0,
        "notes": "requires parsing the actual output distribution from a real run; not attempted",
        "manual_review": True,
    }

    score, notes = _check_idiomatic(text, 5)
    results["idiomatic_geant4"] = {"score": score, "notes": notes, "manual_review": False}

    return results
