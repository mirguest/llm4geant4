# Benchmark Runner

Automates the comparison workflow described in the root `README.md`'s
"Development strategy": run a benchmark with different coding agents and
different models, under baseline (no LLM4Geant4) and treatment (with
LLM4Geant4) conditions, then score and compare the results.

```
create isolated workspace (task.md, + skills/knowledge if "treatment")
        → invoke the agent non-interactively
        → score the resulting workspace against the benchmark's rubric.yaml
        → (optional) LLM-judge the criteria automated checks couldn't decide
        → aggregate everything into a comparison report
```

## Requirements

- Python 3.9+ and PyYAML (`pip install pyyaml`) — the only hard dependency.
- Whichever coding agent CLIs you're comparing (e.g. the `claude` CLI, `opencode`), installed and authenticated.
- A Geant4 installation on PATH (`geant4-config`) if you want `build_and_run`/`output`/`physics_plausibility` scored from an actual build+run rather than static heuristics. Everything still works without it — those criteria are just flagged `manual_review`.

## Quick start (no real agent or Geant4 needed)

Sanity-check the pipeline itself with the built-in `mock` agent, which copies a canned fixture solution into the workspace instead of calling a real model:

```bash
cd benchmarks/runner
python3 run_matrix.py --matrix matrix.mock.yaml --report /tmp/mock-report.md
cat /tmp/mock-report.md
```

## Running for real

1. Copy `agents.example.yaml` to `agents.yaml` and adjust the command templates to match the CLIs you have installed (see comments in the file — exact flags vary by agent and version).
2. Copy `matrix.example.yaml` to `matrix.yaml` and list the agents/models/benchmarks/conditions you want to compare, and how many repeats per cell (agent output is stochastic — 3+ repeats gives you a mean and spread instead of one noisy sample).
3. Run the sweep:

   ```bash
   python3 run_matrix.py --matrix matrix.yaml --agents-config agents.yaml --report report.md
   ```

   This runs every combination, scores it immediately, and writes a Markdown comparison report. Each run's workspace, agent log, manifest, and score are kept under `results/<run_id>/` for inspection or re-scoring.

4. (Optional) Score the criteria that static checks couldn't decide with an LLM judge:

   ```bash
   cp judge.example.yaml judge.yaml   # adjust the command template if needed
   python3 judge.py --results-dir results --all --model claude-sonnet-5
   python3 compare.py --results-dir results --report report.md   # regenerate with judged scores included
   ```

You can also drive one combination at a time with `run_benchmark.py` + `score.py`, useful while debugging an agent adapter's command template.

## Isolation

Regardless of condition, an agent workspace is built from scratch and never contains `rubric.yaml`, `reference/`, `evaluator/`, or `METHODOLOGY.md` — `lib/workspace.py` enforces this in code (see `tests/test_workspace.py`), not just in the benchmark's own `METHODOLOGY.md` prose. `baseline` gets only `task.md`; `treatment` additionally gets a copy of `skills/` and `knowledge/` under `llm4geant4/` in the workspace, with the agent told where to find it.

## Scoring model

Each benchmark can provide `evaluator/evaluate.py` implementing:

```python
def evaluate(workspace: Path, benchmark_dir: Path) -> dict:
    return {
        criterion_id: {"score": <0..max_points>, "notes": "...", "manual_review": <bool>},
        ...
    }
```

`lib/scoring.py` loads this dynamically per benchmark, cross-checks it against `rubric.yaml`, and computes `automated_score`/`automated_max` from the criteria *not* flagged `manual_review`. See `benchmarks/basic-001-muon-scintillator/evaluator/README.md` for what that benchmark's evaluator actually checks (mostly static source inspection, plus a real `cmake`/`make` attempt when Geant4 is available) and what it honestly can't determine without one (chiefly `physics_plausibility`).

Automated scores are a heuristic proxy, not a final grade — a submission can reference the right keywords without correct behavior, and static checks cannot judge physics plausibility or code-quality nuance at all. Use `automated_score` for fast triage across many runs, `judge.py` to fill in what it can from a configured model, and spot-check a sample of runs by hand before drawing conclusions from a comparison.

## Layout

```
runner/
├── agents.example.yaml   # agent CLI command templates (copy to agents.yaml)
├── matrix.example.yaml   # agent x model x benchmark x condition sweep definition
├── matrix.mock.yaml       # sweep using the built-in mock agent, for smoke-testing
├── judge.example.yaml    # LLM-judge command templates (copy to judge.yaml)
├── run_benchmark.py      # CLI: run one combination
├── score.py               # CLI: score one or all completed runs
├── judge.py               # CLI: LLM-judge the manual_review criteria of one or all runs
├── run_matrix.py          # CLI: run + score a full matrix, then report
├── compare.py              # CLI: (re)build the comparison report from results/
├── lib/                    # importable orchestration/scoring/reporting logic
└── tests/                  # unit tests + mock-agent fixtures (no Geant4/agent CLI required)
```

## Testing

```bash
python3 -m unittest discover -s tests -v
```

No external dependencies beyond PyYAML; no Geant4 or agent CLI required — the tests use the fixture "good"/"bad" solutions under `tests/fixtures/` and a fake local judge command to exercise the full workspace → score → judge → report pipeline.
