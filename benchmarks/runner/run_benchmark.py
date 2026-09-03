#!/usr/bin/env python3
"""Run one (benchmark, agent, model, condition) combination.

Example:
    python3 run_benchmark.py \\
        --benchmark basic-001-muon-scintillator \\
        --agent claude-code --model claude-sonnet-5 \\
        --condition treatment
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

from lib.pipeline import run_one  # noqa: E402

DEFAULT_AGENTS_CONFIG = Path(__file__).resolve().parent / "agents.example.yaml"
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, help="benchmark id, e.g. basic-001-muon-scintillator")
    parser.add_argument("--agent", required=True, help="agent name as defined in --agents-config")
    parser.add_argument("--model", required=True, help="model identifier passed to the agent")
    parser.add_argument("--condition", choices=["baseline", "treatment"], required=True)
    parser.add_argument("--trial", default="1", help="trial label, for repeated runs (default: 1)")
    parser.add_argument("--agents-config", default=str(DEFAULT_AGENTS_CONFIG))
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--timeout", type=int, default=1800, help="fallback timeout in seconds if not set per-agent")
    args = parser.parse_args()

    agents_cfg = yaml.safe_load(Path(args.agents_config).read_text())["agents"]

    manifest = run_one(
        benchmark=args.benchmark,
        agent=args.agent,
        model=args.model,
        condition=args.condition,
        trial=args.trial,
        agents_cfg=agents_cfg,
        results_dir=Path(args.results_dir),
        default_timeout=args.timeout,
    )
    status = "OK" if manifest["exit_code"] == 0 and not manifest["timed_out"] else "FAILED"
    print(f"[{status}] {manifest['run_id']} (exit_code={manifest['exit_code']}, "
          f"timed_out={manifest['timed_out']}, duration={manifest['duration_seconds']}s)")


if __name__ == "__main__":
    main()
