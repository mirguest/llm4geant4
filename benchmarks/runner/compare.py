#!/usr/bin/env python3
"""Build a Markdown comparison report across all scored runs.

Example:
    python3 compare.py --results-dir results --output report.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.report import render_markdown  # noqa: E402

DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--output", help="write report to this file instead of stdout")
    args = parser.parse_args()

    report = render_markdown(Path(args.results_dir))
    if args.output:
        Path(args.output).write_text(report)
        print(f"wrote {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
