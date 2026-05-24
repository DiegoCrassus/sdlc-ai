---
name: langsmith-observability
description: >-
  Configure and use LangSmith for RPG-OP — Cursor hook logs (rpg-op-cursor project)
  and Deep Agent runtime traces (rpg-op). Use when debugging hooks, tracing SDLC, or evals.
---

# LangSmith observability

## Projects

- **rpg-op-cursor** — logs dos hooks Cursor (pre/post)
- **rpg-op** — Deep Agent produto + evals

## Env

```
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=rpg-op-cursor
```

## Hook events logged

See `.sdlc/integrations/langsmith.yaml` — pre: sessionStart, beforeSubmitPrompt, preToolUse, beforeShell*, beforeMCP*; post: sessionEnd, stop, postToolUse*, afterShell*, afterMCP*.

## Local fallback

`.sdlc/logs/cursor-hooks.jsonl`

## Docs

[.sdlc/integrations/langsmith.md](../../integrations/langsmith.md)
