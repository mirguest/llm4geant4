# Benchmark Methodology

## Evaluation setup

During an actual benchmark run, the tested agent must receive only the public task (`task.md`) and its normal development environment (Geant4 installation, build tools, etc.).

### Baseline

```
task.md
+ Geant4 environment
+ coding agent
```

### Treatment

```
task.md
+ Geant4 environment
+ coding agent
+ LLM4Geant4 knowledge/skill
```

### Evaluator

```
rubric.yaml
+ reference data
+ evaluator
```

## Isolation rules

The agent must NOT have access to:

- `rubric.yaml`
- `reference/`
- Evaluator implementation
- Expected answers or scoring criteria
- Any LLM4Geant4 knowledge (in the baseline condition)

The public `task.md` describes scientific and functional requirements. It does not teach Geant4 best practices that LLM4Geant4 is supposed to provide. The benchmark measures whether the agent independently uses good Geant4 practices, and whether LLM4Geant4 improves that behavior.

## Reference environment

- **Compatibility target:** Geant4 11.x
- **Reference evaluation environment:** Geant4 11.4.2

The compatibility target means the task should be solvable with any Geant4 11.x installation. The reference evaluation environment is the specific version used to produce frozen reference results for regression comparisons.

## Scoring

Each criterion in `rubric.yaml` is scored independently by the evaluator. The total score is the sum of all criteria (max 100). The evaluator operates on the generated source files and simulation output — it does not need to know which agent produced them.
