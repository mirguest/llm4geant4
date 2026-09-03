"""LLM-judge scoring for rubric criteria that automated static/build checks
flag as manual_review (e.g. physics plausibility, subjective code quality).

This is optional and off by default -- score.py and run_matrix.py never
invoke it automatically; run judge.py explicitly once you trust a
configured judge model to read a rubric criterion plus the submitted
source and return a defensible score. Treat its output the way you would
treat any single model's opinion: useful triage, not ground truth --
spot-check it against your own judgment, especially early on.

Uses the same command-template mechanism as lib/agent_runner.py (see
judge.example.yaml), but captures the judge's text response instead of
just an exit code, and runs it with cwd set to a scratch temp directory
(never the candidate workspace) since the judge only needs to read the
prompt and answer -- it should never modify the submission it's scoring.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from .scoring import load_rubric
from .template import substitute

MAX_SOURCE_CHARS = 20000  # keep the judge prompt bounded

JUDGE_INSTRUCTIONS = (
    "You are scoring one submission against a fixed rubric for a Geant4 simulation benchmark. "
    'Score ONLY the criteria listed below under "CRITERIA TO SCORE". For each, assign a score '
    "between 0 and its max_points based on the submitted source code and (if present) run output "
    'listed under "SUBMISSION". Be skeptical: partial or superficial implementations should not '
    "receive full marks. Respond with ONLY a single JSON object, no prose before or after, mapping "
    'each criterion id to {"score": <number>, "justification": "<one or two sentences>"}. Do not '
    "include any criteria other than the ones listed.\n"
)


def _gather_source(workspace: Path, max_chars: int = MAX_SOURCE_CHARS) -> str:
    relevant_suffixes = {".cc", ".cpp", ".cxx", ".hh", ".hpp", ".h", ".mac", ".txt"}
    chunks = []
    total = 0
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or path.name == "task.md":
            continue
        if path.suffix not in relevant_suffixes and path.name != "CMakeLists.txt":
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        header = f"\n\n--- {path.relative_to(workspace)} ---\n"
        if total + len(header) + len(text) > max_chars:
            text = text[: max(0, max_chars - total - len(header))] + "\n...[truncated]..."
        chunks.append(header + text)
        total += len(header) + len(text)
        if total >= max_chars:
            break
    return "".join(chunks)


def build_prompt(benchmark_dir: Path, workspace: Path, criteria_to_judge: dict) -> str:
    task_text = (benchmark_dir / "task.md").read_text()
    criteria_block = "\n".join(
        f"- id: {cid}\n  label: {c['label']}\n  max_points: {c['max_points']}\n  description: {c['description']}"
        for cid, c in criteria_to_judge.items()
    )
    source_text = _gather_source(workspace)
    return (
        JUDGE_INSTRUCTIONS
        + "\nTASK GIVEN TO THE AGENT:\n" + task_text
        + "\n\nCRITERIA TO SCORE:\n" + criteria_block
        + "\n\nSUBMISSION (source files, possibly truncated):\n" + source_text
    )


def invoke_judge(command_template: str, *, model: str, prompt_text: str, timeout: int, log_path: Path) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as pf:
        pf.write(prompt_text)
        prompt_file = Path(pf.name)

    command = substitute(command_template, model=model, prompt_file=str(prompt_file))
    try:
        proc = subprocess.run(
            command, shell=True, cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=timeout
        )
        output = proc.stdout
    finally:
        prompt_file.unlink(missing_ok=True)

    log_path.write_text(f"$ {command}\n\n{output}")
    return output


def parse_judge_output(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("judge output did not contain a JSON object")
    return json.loads(match.group(0))


def judge_run(*, run_dir: Path, benchmark_dir: Path, command_template: str, model: str, timeout: int) -> dict:
    """Judge every manual_review criterion in run_dir/score.json, update it in place, return it."""
    score = json.loads((run_dir / "score.json").read_text())
    rubric = load_rubric(benchmark_dir)
    criteria = {c["id"]: c for c in rubric["criteria"]}

    to_judge = {
        cid: criteria[cid]
        for cid, r in score["criteria"].items()
        if r.get("manual_review") and cid in criteria
    }
    if not to_judge:
        return score

    prompt_text = build_prompt(benchmark_dir, run_dir / "workspace", to_judge)
    raw = invoke_judge(
        command_template, model=model, prompt_text=prompt_text, timeout=timeout, log_path=run_dir / "judge.log"
    )

    try:
        judged = parse_judge_output(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        for cid in to_judge:
            score["criteria"][cid]["notes"] += f" | judge failed: {exc}"
        (run_dir / "score.json").write_text(json.dumps(score, indent=2))
        return score

    for cid, c in to_judge.items():
        result = judged.get(cid)
        if not result:
            continue
        try:
            judged_score = max(0.0, min(float(result["score"]), float(c["max_points"])))
        except (KeyError, TypeError, ValueError):
            continue
        score["criteria"][cid] = {
            "score": judged_score,
            "max_points": c["max_points"],
            "notes": f"[LLM judge] {result.get('justification', '')}",
            "manual_review": False,
            "judged": True,
        }

    score["automated_score"] = sum(r["score"] for r in score["criteria"].values() if not r["manual_review"])
    score["automated_max"] = sum(r["max_points"] for r in score["criteria"].values() if not r["manual_review"])
    score["needs_manual_review"] = any(r["manual_review"] for r in score["criteria"].values())

    (run_dir / "score.json").write_text(json.dumps(score, indent=2))
    return score
