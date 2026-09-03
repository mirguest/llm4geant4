"""Aggregates results/<run_id>/{manifest,score}.json into a comparison report."""
from __future__ import annotations

import json
import statistics
from pathlib import Path


def load_runs(results_dir: Path) -> list[dict]:
    runs = []
    for run_dir in sorted(results_dir.iterdir()):
        manifest_path = run_dir / "manifest.json"
        score_path = run_dir / "score.json"
        if not manifest_path.exists() or not score_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        score = json.loads(score_path.read_text())
        runs.append({**manifest, "score": score})
    return runs


def group_runs(runs: list[dict]) -> dict:
    """benchmark -> agent -> model -> condition -> [runs]"""
    grouped: dict = {}
    for run in runs:
        b = grouped.setdefault(run["benchmark"], {})
        a = b.setdefault(run["agent"], {})
        m = a.setdefault(run["model"], {})
        m.setdefault(run["condition"], []).append(run)
    return grouped


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return (float("nan"), 0.0)
    mean = statistics.mean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return (mean, std)


def render_markdown(results_dir: Path) -> str:
    runs = load_runs(results_dir)
    if not runs:
        return "No completed runs (with both manifest.json and score.json) found.\n"

    grouped = group_runs(runs)
    lines = ["# LLM4Geant4 Benchmark Comparison", ""]

    for benchmark, agents in sorted(grouped.items()):
        lines.append(f"## {benchmark}")
        lines.append("")
        lines.append("| Agent | Model | Condition | Trials | Automated score | Build/run OK | Needs manual review |")
        lines.append("|---|---|---|---|---|---|---|")

        deltas = []  # (agent, model, treatment_mean - baseline_mean)

        for agent, models in sorted(agents.items()):
            for model, conditions in sorted(models.items()):
                means = {}
                for condition in ("baseline", "treatment"):
                    condition_runs = conditions.get(condition, [])
                    if not condition_runs:
                        continue
                    scores = [r["score"]["automated_score"] for r in condition_runs]
                    max_scores = [r["score"]["automated_max"] for r in condition_runs]
                    mean, std = _mean_std(scores)
                    max_mean = max_scores[0] if max_scores else float("nan")
                    ran_ok = sum(
                        1 for r in condition_runs if r.get("exit_code") == 0 and not r.get("timed_out")
                    )
                    manual = any(r["score"]["needs_manual_review"] for r in condition_runs)
                    means[condition] = mean
                    lines.append(
                        f"| {agent} | {model} | {condition} | {len(condition_runs)} "
                        f"| {mean:.1f} ± {std:.1f} / {max_mean:.0f} "
                        f"| {ran_ok}/{len(condition_runs)} "
                        f"| {'yes' if manual else 'no'} |"
                    )
                if "baseline" in means and "treatment" in means:
                    deltas.append((agent, model, means["treatment"] - means["baseline"]))

        if deltas:
            lines.append("")
            lines.append("Treatment vs. baseline (automated score delta):")
            lines.append("")
            for agent, model, delta in deltas:
                sign = "+" if delta >= 0 else ""
                lines.append(f"- {agent} / {model}: {sign}{delta:.1f}")
        lines.append("")

    lines.append(
        "Automated scores are heuristic proxies (static checks, build/run success, output presence). "
        "Runs flagged `needs manual review` have at least one rubric criterion (typically physics "
        "plausibility or code-quality judgment) that automated checks cannot score and must be "
        "confirmed by a human or an LLM judge before treating the total as final."
    )
    return "\n".join(lines) + "\n"
