# .cursor — Cursor Agent Configuration

This directory contains all Cursor-specific configuration for the `sdlc-ai` project.

## Structure

| Directory     | Purpose                                                         |
|---------------|-----------------------------------------------------------------|
| `rules/`      | Persistent rules applied to every agent interaction             |
| `commands/`   | Reusable command instructions for SDLC operations               |
| `skills/`     | Specialized skill procedures for each SDLC activity             |
| `subagents/`  | Specialized agent roles with defined responsibilities           |
| `hooks/`      | Pre/post task and review operational procedures                 |
| `hooks.json`  | Executable Cursor hooks (SDLC observability on sessionStart/stop) |

## Rules

| File                         | Applied When                             |
|------------------------------|------------------------------------------|
| `000-project-governance.mdc` | Always                                   |
| `010-ai-native-sdlc.mdc`     | Always                                   |
| `020-code-quality.mdc`       | During implementation and review         |
| `030-docs-and-handoff.mdc`   | When docs or interfaces change           |
| `040-doctor-gates.mdc`       | After structural changes                 |

## Commands

Use these commands by referencing them in Cursor:

| Command            | Purpose                                        |
|--------------------|------------------------------------------------|
| `sdlc-doctor`      | Validate repository structure                  |
| `sdlc-plan`        | Convert a ticket into a structured plan        |
| `sdlc-implement`   | Implement a planned task                       |
| `sdlc-review`      | Review a PR or diff                            |
| `sdlc-handoff`     | Generate a handoff summary                     |

## Quick Reference

```bash
# Validate the repository
make sdlc-doctor

# Plan a new task
# Use: @sdlc-plan in Cursor chat

# Implement a planned task
# Use: @sdlc-implement in Cursor chat
```
