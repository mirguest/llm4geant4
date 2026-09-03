#!/usr/bin/env python3
"""Run a full agent x model x benchmark x condition x trial matrix, then score and report.

Example:
    python3 run_matrix.py --matrix matrix.example.yaml --agents-config agents.example.yaml

Matrix file format (see matrix.example.yaml):

    benchmarks: [basic-001-muon-scintillator]
    conditions: [baseline, treatment]
    repeats: 3
    runs:
      - agent: claude-code
        models: [claude-sonnet-5, claude-opus-5]
      - agent: opencode
        models: [some-model-id]

Each (benchmark, run entry, model, condition, trial) combination is run,
scored, and included in the final comparison report. A failed or timed-out
agent invocation does not stop the sweep -- it is recorded and scored (an
empty/partial workspace will simply score low), and the sweep continues.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

from lib.pipeline import run_one, score_one  # noqa: E402
from lib.report import render_markdown  # noqa: E402

DEFAULT_AGENTS_CONFIG = Path(__file__).resolve().parent / "agents.example.yaml"
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--matrix", required=True, help="path to a matrix YAML file")
    parser.add_argument("--agents-config", default=str(DEFAULT_AGENTS_CONFIG))
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--report", help="write the final Markdown comparison report to this file")
    args = parser.parse_args()

    matrix = yaml.safe_load(Path(args.matrix).read_text())
    agents_cfg = yaml.safe_load(Path(args.agents_config).read_text())["agents"]
    results_dir = Path(args.results_dir)

    benchmarks = matrix["benchmarks"]
    conditions = matrix.get("conditions", ["baseline", "treatment"])
    repeats = int(matrix.get("repeats", 1))

    total = 0
    failed = 0

    for benchmark in benchmarks:
        for entry in matrix["runs"]:
            agent = entry["agent"]
            for model in entry["models"]:
                for condition in conditions:
                    for trial in range(1, repeats + 1):
                        total += 1
                        try:
                            manifest = run_one(
                                benchmark=benchmark,
                                agent=agent,
                                model=model,
                                condition=condition,
                                trial=str(trial),
                                agents_cfg=agents_cfg,
                                results_dir=results_dir,
                                default_timeout=args.timeout,
                            )
                            status = "OK" if manifest["exit_code"] == 0 and not manifest["timed_out"] else "AGENT-FAILED"
                            if status != "OK":
                                failed += 1
                            print(f"[{status}] {manifest['run_id']}")
                            score_one(run_dir=results_dir / manifest["run_id"])
                        except Exception as exc:  # noqa: BLE001 - keep the sweep going
                            failed += 1
                            print(f"[ERROR] {benchmark}/{agent}/{model}/{condition}/t{trial}: {exc}")

    print(f"\n{total - failed}/{total} runs completed without agent errors.")

    report = render_markdown(results_dir)
    if args.report:
        Path(args.report).write_text(report)
        print(f"wrote {args.report}")
    else:
        print(report)


if __name__ == "__main__":
    main()
