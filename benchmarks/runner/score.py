#!/usr/bin/env python3
"""Score a completed run (or all completed runs) against its benchmark's rubric.

Examples:
    python3 score.py --run-dir results/basic-001-muon-scintillator__claude-code__claude-sonnet-5__treatment__t1
    python3 score.py --results-dir results --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.pipeline import score_one  # noqa: E402

DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", help="score a single run directory")
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR), help="root results directory")
    parser.add_argument("--all", action="store_true", help="score every run under --results-dir that has a manifest.json")
    args = parser.parse_args()

    if args.run_dir:
        targets = [Path(args.run_dir)]
    elif args.all:
        results_dir = Path(args.results_dir)
        targets = sorted(p.parent for p in results_dir.glob("*/manifest.json"))
    else:
        sys.exit("pass either --run-dir <dir> or --results-dir <dir> --all")

    for run_dir in targets:
        try:
            result = score_one(run_dir=run_dir)
        except Exception as exc:  # noqa: BLE001 - report and continue across a batch
            print(f"[ERROR] {run_dir}: {exc}")
            continue
        flag = " (needs manual review)" if result["needs_manual_review"] else ""
        print(f"{result['run_id']}: {result['automated_score']}/{result['automated_max']} automated"
              f" (rubric total {result['total_max']}){flag}")


if __name__ == "__main__":
    main()
