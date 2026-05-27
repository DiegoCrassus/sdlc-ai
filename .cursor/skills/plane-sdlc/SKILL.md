# Skill: Plane SDLC (MCP)

> **Workflow authority:** `docs/sdlc/change-lifecycle.md`

## Purpose

Criar, atualizar estados e encerrar **work items exclusivamente no Plane**. Nunca backlog local (`specs/`).

## State lifecycle (mandatory)

| Momento | Estado Plane | Como |
|---------|--------------|------|
| Plano criado (Planner) | **Todo** ou Backlog | MCP create issue |
| `start-change` / início implementação | **In Progress** | `python3 .sdlc/scripts/plane_state.py in-progress --card INVES-N` |
| PR aberto | In Progress (+ comentário PR) | comment no card |
| Merge + CI verde | **Done** | `auto_merge_pr.py --plane-comment` ou `plane_state.py done` |

**Falha de processo:** implementar com card em Todo/Backlog, ou marcar Done sem passar por In Progress.

## MCP

- Config: `.cursor/mcp.json` — server `plane` (token **must** match `.env` `PLANE_API_KEY`)
- Env: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_PROJECT_NAME`

| Campo | Valor |
|-------|-------|
| Workspace | `investments-sdlc` |
| Project | `investiments` |
| Card ID | `INVES-N` |

## Procedure — criar work item

1. Conectar via Plane MCP ou REST (`.sdlc/scripts/plane_state.py` usa REST).
2. Criar issue no project `investiments`.
3. Título: `[AI][TYPE] Short imperative title`
4. Descrição: plano completo (11 secções)
5. Estado inicial: **Todo** (epic) ou **Todo** (sub-task aguardando start-change)
6. Anotar `INVES-N` retornado

## Procedure — In Progress

Executar **no start-change**, antes de branch/código:

```bash
python3 .sdlc/scripts/plane_state.py in-progress --card INVES-N
```

## Procedure — evidência e Done

1. Comentar: link PR, pytest, doctor
2. **Done** somente após merge autônomo em `develop` + CI verde
3. Usar `auto_merge_pr.py --plane-comment` ou `plane_state.py done`

## Proibições

- Nunca `specs/` ou tickets locais
- Nunca GitHub Issue como tracker primário (Issue Analyst tria/fecha duplicatas)
- Nunca inventar `INVES-N`
