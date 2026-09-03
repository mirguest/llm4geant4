"""Builds isolated agent workspaces for a benchmark run.

Enforces the isolation rules from METHODOLOGY.md in code rather than only in
prose: an agent workspace never contains rubric.yaml, reference/,
evaluator/, or METHODOLOGY.md, regardless of condition. The "treatment"
condition additionally receives a copy of skills/ and knowledge/ so the
agent can consult LLM4Geant4 guidance; "baseline" gets only task.md.
"""
from __future__ import annotations

import shutil
from pathlib import Path

VALID_CONDITIONS = ("baseline", "treatment")

# Files/directories that must never be copied into an agent's workspace,
# under any condition -- these carry the answer key.
FORBIDDEN_NAMES = {"rubric.yaml", "reference", "evaluator", "METHODOLOGY.md"}


def create_workspace(benchmark_dir: Path, condition: str, repo_root: Path, dest: Path) -> Path:
    """Create (or overwrite) an isolated workspace at `dest` for one run.

    Args:
        benchmark_dir: path to benchmarks/<benchmark-id>/
        condition: "baseline" or "treatment"
        repo_root: path to the llm4geant4 repository root (for skills/knowledge)
        dest: destination directory for the workspace (created if missing)
    """
    if condition not in VALID_CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}, expected one of {VALID_CONDITIONS}")

    task_file = benchmark_dir / "task.md"
    if not task_file.exists():
        raise FileNotFoundError(f"benchmark {benchmark_dir} has no task.md")

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    shutil.copy2(task_file, dest / "task.md")

    if condition == "treatment":
        skill_root = dest / "llm4geant4"
        shutil.copytree(repo_root / "skills", skill_root / "skills")
        shutil.copytree(repo_root / "knowledge", skill_root / "knowledge")

    _assert_no_forbidden_content(dest)
    return dest


def _assert_no_forbidden_content(workspace: Path) -> None:
    for path in workspace.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            raise AssertionError(
                f"isolation violation: {path} must never be copied into an agent workspace"
            )
