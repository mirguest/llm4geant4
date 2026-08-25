---
name: llm4geant4
description: Geant4 domain knowledge and development guidance for coding agents.
---

# LLM4Geant4

You are building or modifying a Geant4 simulation application. LLM4Geant4 provides trusted Geant4 domain knowledge — use it to guide your decisions, but you are the agent that writes, builds, and tests the code.

## High-level principles

- **Understand the scientific problem first.** Before writing code, clarify what is being simulated, what observables matter, and what physics processes are relevant.
- **Detect the installed Geant4 version and environment.** Always check which Geant4 version is available (`geant4-config --version`) and that the environment is sourced before building.
- **Consult relevant LLM4Geant4 knowledge when needed.** The knowledge base covers canonical examples, development practices, and validation criteria. Load the relevant parts; do not cargo-cult everything.
- **Prefer adapting official Geant4 examples over generating applications from scratch.** The Geant4 distribution includes a rich set of validated examples in `examples/`. Find the closest match and adapt it incrementally.
- **Use version-compatible and idiomatic Geant4 APIs.** Match the API conventions of the installed Geant4 version. When in doubt, consult the Toolkit Developer's Guide and the relevant example for that version.
- **Make minimal and incremental changes.** Each change should be small enough that you can build, run, and verify it before moving on.
- **Build and test after meaningful modifications.** Do not accumulate many untested changes.
- **Run small tests before large simulations.** Start with a few events (`/run/beamOn 10`), inspect verbose output, then scale up.
- **Validate both software correctness and physics correctness before declaring success.** Compiling and running without crashes is necessary but not sufficient. Check that the output is physically plausible.
- **Explain important Geant4-specific decisions when the user is learning.** When choices about geometry representation, physics list selection, hit recording strategy, or MT setup matter, make them explicit.

## Knowledge areas

LLM4Geant4 maintains canonical Geant4 domain knowledge in a top-level `knowledge/` directory. Consult the relevant area when you need deeper guidance:

- **Examples** — canonical skeleton patterns, class hierarchy, common component patterns
- **Development** — build system, CMake, iterative development workflow, common mistakes
- **Validation** — geometry, physics, output, and statistical validation strategies

The canonical source is the `knowledge/` directory. When a particular agent runtime bundles selected knowledge into a `references/` directory, prefer the bundled version for that runtime, but understand that `knowledge/` remains authoritative.

## Development workflow

```text
understand the problem
→ find the closest official Geant4 example
→ make a small change
→ build
→ run a small test (few events)
→ inspect output (verbose, histograms, log)
→ validate physics plausibility
→ repeat
```

Avoid generating a complete application in one large step. Iteration catches mistakes early.

## After completing work

- Confirm the code compiles with no warnings against the detected Geant4 version.
- Confirm that a short test run (e.g., 10 events) produces physically plausible output.
- If a benchmark or validation reference exists, compare against it.
- Report which Geant4 version, physics list, and production cuts were used.
