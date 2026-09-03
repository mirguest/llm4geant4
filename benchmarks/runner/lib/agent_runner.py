"""Invokes a coding agent non-interactively as a subprocess.

Agent CLIs are configured, not hardcoded: each entry in agents.yaml supplies
a shell command template with `{model}` and `{prompt_file}` placeholders.
This intentionally uses shell=True -- the command template comes from local
config the user controls (like a Makefile target), not from untrusted
external input. Do not source agents.yaml or matrix.yaml from anywhere you
would not trust to run a shell command on your machine.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

from .template import substitute


def run_agent(
    command_template: str,
    *,
    model: str,
    prompt_file: Path,
    workdir: Path,
    timeout: int,
    log_path: Path,
    runner_dir: Path | None = None,
) -> dict:
    """Run one agent invocation and capture its outcome.

    Returns a dict with: command, exit_code, timed_out, duration_seconds.
    Combined stdout/stderr is written to log_path.

    Command templates may use `{model}`, `{prompt_file}`, and `{runner_dir}`
    (the benchmarks/runner directory, useful for referencing fixtures such
    as the mock agent used in tests).
    """
    workdir.mkdir(parents=True, exist_ok=True)
    command = substitute(
        command_template,
        model=model,
        prompt_file=str(prompt_file),
        runner_dir=str(runner_dir) if runner_dir is not None else "",
    )

    start = time.monotonic()
    timed_out = False
    exit_code = None
    with open(log_path, "w") as logf:
        logf.write(f"$ {command}\n\n")
        logf.flush()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=workdir,
                stdout=logf,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            logf.write(f"\n[runner] timed out after {timeout}s\n")
    duration = time.monotonic() - start

    return {
        "command": command,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_seconds": round(duration, 2),
    }
