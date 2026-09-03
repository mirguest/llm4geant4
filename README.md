# LLM4Geant4

LLM4Geant4 provides trusted Geant4 domain knowledge, development practices, examples, and validation guidance for general-purpose coding agents.

## What LLM4Geant4 is (and is not)

- **LLM4Geant4 is not an LLM and not a coding agent.** It does not generate code, run simulations, or make decisions. It provides structured domain knowledge that coding agents can consult.
- **LLM4Geant4 is agent-agnostic.** Users may choose Claude Code, Codex, OpenCode, or another compatible agent. The knowledge is designed to be portable across agent frameworks.
- **LLM4Geant4 is model-agnostic.** It does not assume a specific LLM provider or model. The philosophy is: let the model reason; let LLM4Geant4 provide trusted Geant4 knowledge.
- **Skills are one delivery mechanism, not the core identity.** The canonical Geant4 knowledge lives in `knowledge/`. Skills are thin wrappers that tell an agent how to use that knowledge.

## Philosophy

> Let the model reason; let LLM4Geant4 provide trusted Geant4 knowledge.

LLM4Geant4 should NOT become another coding agent. It should provide reusable Geant4 knowledge that general-purpose coding agents can use to build correct, idiomatic Geant4 applications.

## Structure

```
llm4geant4/
├── README.md
├── skills/                          # Agent skill definitions
│   └── llm4geant4/
│       └── SKILL.md                 # Meta Skill: entry point for coding agents
├── knowledge/                       # Canonical Geant4 domain knowledge
│   ├── examples.md                  # Application patterns and class hierarchy
│   ├── development.md               # Build system, workflow, common mistakes
│   ├── geometry.md                  # Solids, placement, regions, fields, GDML
│   ├── physics-lists.md             # Reference lists, EM/optical physics, cuts, biasing
│   ├── scoring-and-output.md        # Sensitive detectors, scorers, G4AnalysisManager
│   ├── multithreading.md            # Run manager, master/worker responsibilities, shared state
│   ├── validation.md                # Physics and software validation
│   └── troubleshooting.md           # Common failure symptoms and causes
├── benchmarks/                      # Scored benchmarks for agent evaluation
│   ├── basic-001-muon-scintillator/
│   │   ├── task.md                  # Task presented to the agent
│   │   ├── rubric.yaml              # Evaluation criteria
│   │   ├── reference/               # Frozen reference simulations (future)
│   │   └── evaluator/               # Automated (heuristic) scoring for this benchmark
│   └── runner/                      # Automates running/scoring benchmarks across agents and models
│       └── README.md                # How to run and compare an agent x model matrix
└── adapters/                        # Agent-specific adapters (future)
    └── README.md
```

## Development strategy

The project follows **benchmark-driven development**:

1. **Define a benchmark** — a specific Geant4 simulation task with evaluation criteria.
2. **Run with a coding agent alone** — measure baseline performance.
3. **Run with LLM4Geant4 available** — measure improvement.
4. **Compare** — software correctness, Geant4 correctness, physics plausibility, development behavior.

The first experiment (benchmark `basic-001-muon-scintillator`) is designed to answer:

> Does providing a coding agent with structured Geant4 domain knowledge improve the quality of the generated simulation software?

`benchmarks/runner/` automates steps 2–4 across a matrix of coding agents (Claude Code, OpenCode, etc.) and models: it builds an isolated workspace per run (enforcing the baseline/treatment isolation rules in code, not just prose), invokes each agent non-interactively, scores the result against the benchmark's rubric, and produces a comparison report. See `benchmarks/runner/README.md`.

Future benchmarks will cover more complex geometries, physics, and detector configurations.

## Requirements

- Geant4 11.x (installed and sourceable)
- C++17 or later
- CMake 3.16+
- A compatible coding agent (Claude Code, Codex, OpenCode, etc.)
- Python 3.9+ and PyYAML, only for `benchmarks/runner/` (the automated comparison tooling)

## Usage

### With Claude Code

Register this repository as a skill source, or load `skills/llm4geant4/SKILL.md` directly.

### With other agents

Copy or link the `skills/` and `knowledge/` directories into a location your agent can access. The SKILL.md uses minimal, portable frontmatter compatible with the common Agent Skills subset.
