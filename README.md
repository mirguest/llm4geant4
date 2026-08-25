# llm4geant4

Meta-skills and skills for AI agents to develop Geant4 simulation applications.

## Purpose

This project equips LLM-powered coding agents with the domain knowledge, patterns, and benchmarks needed to build correct, idiomatic Geant4 applications. Instead of treating Geant4 as a generic C++ library, agents learn the simulation framework's conventions, common traps, and validation workflows.

## Structure

```
├── skills/           # Agent skill definitions (loaded at runtime)
│   └── llm4geant4/
│       └── SKILL.md  # Main skill: Geant4 application development
│
├── knowledge/        # Reference material loaded by skills
│   ├── examples.md       # Canonical Geant4 application patterns
│   ├── development.md    # Development workflow and best practices
│   └── validation.md     # Testing and physics validation strategies
│
└── benchmarks/       # Scored benchmarks for evaluating agent quality
    └── basic-001-muon-scintillator/  # Benchmark 001
```

## Usage

Add this repository as a skill source in your agent harness. The agent loads `skills/llm4geant4/SKILL.md` which brings in the knowledge base and defines the Geant4 development workflow.

## Requirements

- Geant4 11.x (installed and sourceable)
- C++17 or later
- CMake 3.16+
