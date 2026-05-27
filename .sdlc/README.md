# .sdlc — SDLC Operating System

This directory contains the machine-readable SDLC configuration for the `sdlc-ai` project.

## Files

| File                | Purpose                                              |
|---------------------|------------------------------------------------------|
| `sdlc.yaml`         | Main entrypoint — references all other files         |
| `lifecycle.yaml`    | 10-stage lifecycle definition                        |
| `stages.yaml`       | Stage inputs, outputs, evidence, and gates           |
| `workflows.yaml`    | Stage transition workflows                           |
| `agents.yaml`       | Agent-to-stage mapping                               |
| `skills.yaml`       | Skill-to-stage mapping                               |
| `rules.yaml`        | Governance rules                                     |
| `integrations.yaml` | External service placeholders                        |
| `doctor.yaml`       | Doctor validation rules                              |

## Directories

| Directory  | Purpose                                              |
|------------|------------------------------------------------------|
| `memory/`  | Persistent context for agents (architecture, rules, ops, incidents) |
| `dsl/`     | Python DSL for loading, validating, and running the Doctor |

## Usage

```bash
# Run the Doctor
make sdlc-doctor

# Validate YAML consistency
make sdlc-validate

# List lifecycle stages
make sdlc-stages
```

## Rules

Never edit YAML files to make the Doctor pass artificially.
All changes must reflect the actual repository state.
