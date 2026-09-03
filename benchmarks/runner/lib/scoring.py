"""Scores a completed agent workspace against a benchmark's rubric.yaml.

Each benchmark may provide benchmarks/<id>/evaluator/evaluate.py exposing:

    def evaluate(workspace: Path, benchmark_dir: Path) -> dict:
        return {
            criterion_id: {
                "score": float,        # 0..max_points, or None if not determinable
                "notes": str,          # brief justification
                "manual_review": bool, # True if a human/LLM judge must confirm this
            },
            ...
        }

Automated checks are necessarily heuristic (static source inspection, build
success, presence of output files) -- they are a proxy for the rubric, not a
replacement for judgment on subjective criteria like physics plausibility or
code quality. Criteria an evaluator flags (or omits) as manual_review are
excluded from `automated_score`/`automated_max` and must be scored by a
human or an LLM judge (see judge.py) before treating a run as fully scored.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


def load_rubric(benchmark_dir: Path) -> dict:
    with open(benchmark_dir / "rubric.yaml") as f:
        return yaml.safe_load(f)


def load_evaluator(benchmark_dir: Path):
    """Dynamically import benchmarks/<id>/evaluator/evaluate.py, if present."""
    eval_path = benchmark_dir / "evaluator" / "evaluate.py"
    if not eval_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{benchmark_dir.name}_evaluator", eval_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    if not hasattr(module, "evaluate"):
        raise AttributeError(f"{eval_path} does not define evaluate(workspace, benchmark_dir)")
    return module


def score_workspace(benchmark_dir: Path, workspace: Path) -> dict:
    rubric = load_rubric(benchmark_dir)
    criteria = {c["id"]: c for c in rubric["criteria"]}

    evaluator = load_evaluator(benchmark_dir)
    raw = evaluator.evaluate(workspace, benchmark_dir) if evaluator is not None else {}

    results = {}
    for cid, c in criteria.items():
        r = raw.get(cid)
        if r is None:
            results[cid] = {
                "score": None,
                "max_points": c["max_points"],
                "notes": "no automated check for this criterion" if evaluator else "no evaluator implemented for this benchmark",
                "manual_review": True,
            }
        else:
            score = r.get("score")
            manual_review = bool(r.get("manual_review", False)) or score is None
            if score is not None:
                score = max(0.0, min(float(score), float(c["max_points"])))
            results[cid] = {
                "score": score,
                "max_points": c["max_points"],
                "notes": r.get("notes", ""),
                "manual_review": manual_review,
            }

    automated_score = sum(r["score"] for r in results.values() if not r["manual_review"])
    automated_max = sum(r["max_points"] for r in results.values() if not r["manual_review"])
    total_max = sum(r["max_points"] for r in results.values())

    return {
        "benchmark": rubric.get("id", benchmark_dir.name),
        "criteria": results,
        "automated_score": automated_score,
        "automated_max": automated_max,
        "total_max": total_max,
        "needs_manual_review": any(r["manual_review"] for r in results.values()),
    }
