"""Shared orchestration: one (benchmark, agent, model, condition, trial) run."""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import workspace as ws
from .agent_runner import run_agent
from .scoring import score_workspace

RUNNER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RUNNER_DIR.parents[1]
BENCHMARKS_DIR = REPO_ROOT / "benchmarks"

PROMPT_SUFFIX_TREATMENT = (
    "\n\n---\n\n"
    "Additional Geant4 development guidance is available in this workspace under "
    "`llm4geant4/skills/llm4geant4/SKILL.md` and `llm4geant4/knowledge/`. "
    "Consult it as needed while completing the task above.\n"
)


def build_prompt(task_text: str, condition: str) -> str:
    if condition == "treatment":
        return task_text + PROMPT_SUFFIX_TREATMENT
    return task_text


def run_id_for(benchmark: str, agent: str, model: str, condition: str, trial: str) -> str:
    safe_model = model.replace("/", "-")
    return f"{benchmark}__{agent}__{safe_model}__{condition}__t{trial}"


def run_one(
    *,
    benchmark: str,
    agent: str,
    model: str,
    condition: str,
    trial: str,
    agents_cfg: dict,
    results_dir: Path,
    default_timeout: int,
) -> dict:
    benchmark_dir = BENCHMARKS_DIR / benchmark
    if not benchmark_dir.exists():
        raise FileNotFoundError(f"unknown benchmark: {benchmark}")
    if agent not in agents_cfg:
        raise KeyError(f"unknown agent '{agent}' (not found in agents config)")

    agent_cfg = agents_cfg[agent]
    command_template = agent_cfg["command"]
    timeout = agent_cfg.get("timeout_seconds", default_timeout)

    run_id = run_id_for(benchmark, agent, model, condition, trial)
    run_dir = results_dir / run_id
    workspace_dir = run_dir / "workspace"

    ws.create_workspace(benchmark_dir, condition, REPO_ROOT, workspace_dir)

    task_text = (benchmark_dir / "task.md").read_text()
    prompt_text = build_prompt(task_text, condition)
    prompt_file = run_dir / "prompt.md"
    prompt_file.write_text(prompt_text)

    log_path = run_dir / "agent.log"
    result = run_agent(
        command_template,
        model=model,
        prompt_file=prompt_file,
        workdir=workspace_dir,
        timeout=timeout,
        log_path=log_path,
        runner_dir=RUNNER_DIR,
    )

    manifest = {
        "run_id": run_id,
        "benchmark": benchmark,
        "agent": agent,
        "model": model,
        "condition": condition,
        "trial": trial,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **result,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def score_one(*, run_dir: Path) -> dict:
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    benchmark_dir = BENCHMARKS_DIR / manifest["benchmark"]
    workspace_dir = run_dir / "workspace"

    result = score_workspace(benchmark_dir, workspace_dir)
    result["run_id"] = manifest["run_id"]
    (run_dir / "score.json").write_text(json.dumps(result, indent=2))
    return result
