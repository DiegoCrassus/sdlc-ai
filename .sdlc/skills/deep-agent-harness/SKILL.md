---
name: deep-agent-harness
description: >-
  Configure LangChain Deep Agents for RPG-OP — create_deep_agent, subagents, skills, HITL.
  Use for services/agent/, .sdlc/agents/, and product agent specs.
---

# Deep Agent harness

## Product (runtime)

- Orchestrator: `rpg-sheet-orchestrator`
- MVP subagent: `sheet-template-analyst` — PDF/image → schema + canvas_spec
- Spec source: `specs/agents/` → compile → `generated/agent_manifest/`

## Engineering (SDLC)

- Dev orchestrator: `.sdlc/agents/dev-orchestrator.yaml`
- Subagents: spec-author, codegen-integrator, eval-engineer

## create_deep_agent checklist

```python
create_deep_agent(
    model=os.environ["AGENT_MODEL"],
    tools=[...],           # hooks in services/agent/tools/
    subagents=[...],       # from manifest or YAML
    skills=[...],          # skills/ + .sdlc/skills/
    memory=[".sdlc/AGENTS.md"],
    interrupt_on={...},
    permissions=[...],
)
```

## HITL MVP

- `publish_template` — GM confirms
- Block writes to `generated/**` in dev agent

## Docs

- [docs/03-deep-agent-harness.md](../../docs/03-deep-agent-harness.md)
- [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/index)
