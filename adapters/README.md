# Agent Adapters

This directory will hold agent-specific adapters if and when they become necessary.

## Purpose

The canonical Skill (`skills/llm4geant4/SKILL.md`) uses minimal, portable frontmatter compatible with the common Agent Skills subset. It should work across Claude Code, Codex, OpenCode, and similar agent frameworks without modification.

If a particular agent runtime requires host-specific configuration (e.g., Claude-specific `allowed-tools`, Codex-specific manifests, OpenCode-specific packaging), those should live here rather than in the canonical Skill:

```
adapters/
  claude/
    ...                 # Claude Code-specific configuration
  codex/
    ...                 # Codex-specific configuration
  opencode/
    ...                 # OpenCode-specific configuration
```

## Current status

No adapters are needed at this stage. The portable frontmatter is sufficient for the initial proof-of-concept milestone.

Add adapter directories only when there is a concrete, demonstrated need.
