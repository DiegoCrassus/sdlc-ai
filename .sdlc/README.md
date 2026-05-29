# .sdlc — SDLC Operating System (v5.2)

> **Single entry:** [`sdlc.yaml`](sdlc.yaml) — read **`core`** first (vendors, env, paths).  
> **Module map:** `contract.modules` → each folder README.

## Loading order

1. [`AGENTS.md`](../AGENTS.md)
2. [`docs/sdlc/master-workflow.md`](../docs/sdlc/master-workflow.md) + [`change-lifecycle.md`](../docs/sdlc/change-lifecycle.md)
3. **[`sdlc.yaml`](sdlc.yaml)** — `core` + `contract.modules`
4. Module README for your task

## Modules

| Module | README | Data |
|--------|--------|------|
| [Manifest](manifest/README.md) | Agent/skill catalog | `manifest/catalog.yaml` |
| [Stages](stages/README.md) | Lifecycle + definitions | `stages/lifecycle.yaml`, `stages/definitions.yaml` |
| [Gates](gates/README.md) | Write gate | `gates/paths.yaml` |
| [Workboard](workboard/README.md) | Card rules | `workboard/granularity.yaml` |
| [Pipeline](pipeline/README.md) | Agents ↔ stages | `pipeline/agents.yaml` |
| [Workflows](workflows/README.md) | Transitions | `workflows/transitions.yaml` |
| [Rules](rules/README.md) | Governance | `rules/governance.yaml` |
| [Integrations](integrations/README.md) | Service roles | `integrations/services.yaml` |
| [Doctor](doctor/README.md) | Structure checks | `doctor/checks.yaml` |
| [Meta](meta/README.md) | Meta-tools | `meta/tools.yaml` |
| [Settings](settings/README.md) | Flags & memory | `settings/config.yaml` |

## Commands

```bash
make sdlc-doctor      # always writes health Canvas + doctor-health.json
make sdlc-validate
make sdlc-stages
```

## Canvases (IDE)

- **Doctor health:** `sdlc-doctor-health.canvas.tsx` (generated each doctor run)
- **FEATURE flow:** `sdlc-feature-flow-simulation.canvas.tsx` (reference simulation)
