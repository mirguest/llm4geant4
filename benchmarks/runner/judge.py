#!/usr/bin/env python3
"""Score the manual_review-flagged criteria in one or more completed runs
using an LLM judge. Optional and explicit -- never invoked automatically by
score.py or run_matrix.py.

Updates each run's score.json in place, replacing manual_review criteria
the judge could confidently score with a judged score + justification.

Examples:
    python3 judge.py --run-dir results/<run_id> --model claude-sonnet-5
    python3 judge.py --results-dir results --all --model claude-sonnet-5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

from lib.judge import judge_run  # noqa: E402
from lib.pipeline import BENCHMARKS_DIR  # noqa: E402

DEFAULT_JUDGE_CONFIG = Path(__file__).resolve().parent / "judge.example.yaml"
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", help="judge a single run directory (must already have a score.json)")
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--all", action="store_true", help="judge every run under --results-dir with a score.json")
    parser.add_argument("--judge-config", default=str(DEFAULT_JUDGE_CONFIG))
    parser.add_argument("--judge", default="claude-code", help="judge entry name in --judge-config")
    parser.add_argument("--model", required=True, help="model identifier passed to the judge")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    if args.run_dir:
        targets = [Path(args.run_dir)]
    elif args.all:
        targets = sorted(p.parent for p in Path(args.results_dir).glob("*/score.json"))
    else:
        sys.exit("pass either --run-dir <dir> or --results-dir <dir> --all")

    judges_cfg = yaml.safe_load(Path(args.judge_config).read_text())["judges"]
    if args.judge not in judges_cfg:
        sys.exit(f"unknown judge '{args.judge}' in {args.judge_config}")
    cfg = judges_cfg[args.judge]

    for run_dir in targets:
        manifest = json.loads((run_dir / "manifest.json").read_text())
        benchmark_dir = BENCHMARKS_DIR / manifest["benchmark"]
        try:
            score = judge_run(
                run_dir=run_dir,
                benchmark_dir=benchmark_dir,
                command_template=cfg["command"],
                model=args.model,
                timeout=cfg.get("timeout_seconds", args.timeout),
            )
        except Exception as exc:  # noqa: BLE001 - report and continue across a batch
            print(f"[ERROR] {run_dir}: {exc}")
            continue
        print(
            f"{manifest['run_id']}: {score['automated_score']}/{score['automated_max']} after judging "
            f"(needs_manual_review={score['needs_manual_review']})"
        )


if __name__ == "__main__":
    main()
