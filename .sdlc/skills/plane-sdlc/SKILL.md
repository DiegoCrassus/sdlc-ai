---
name: plane-sdlc
description: >-
  Opera Plane via MCP — work items, cycles, modules, pages (documentação).
  Use para backlog de produto, sprints, wiki e sincronizar contexto com GitHub SDLC.
---

# Plane SDLC

## Prerequisites

- Plane MCP enabled (`.cursor/mcp.json`, server `plane`)
- Env: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`
- Setup: `.sdlc/integrations/plane.md`

## SDLC ↔ Plane mapping

| Phase | Plane artifact | GitHub (paralelo) |
|-------|----------------|-------------------|
| intent | Work item (Backlog/Todo) | Issue `sdlc:intent` |
| spec | Project Page ou descrição do work item | Issue + branch |
| implement | Work item → In Progress | Commits + PR |
| review | Work item → In Review | PR review |
| done | Work item → Done + comment | Merged PR |

## MCP workflow (agent)

1. **`get_me`** — confirmar autenticação
2. **`list_projects`** — resolver `project_id` e `identifier` (ex.: `RPG`)
3. **Tarefas** — `list_work_items`, `create_work_item`, `update_work_item`
4. **Busca por ID legível** — `retrieve_work_item_by_identifier` (`RPG-12`)
5. **Documentação** — `create_project_page` / `retrieve_project_page` para specs e ADRs
6. **Comentários** — `create_work_item_comment` ao concluir fase ou linkar PR

## Convenções RPG-OP

- Projeto Plane sugerido: mesmo nome do repo ou produto (`RPG-OP`)
- Título de work item: `[Intent] …`, `[Spec] …`, `[Implement] …` (espelha GitHub)
- Ao criar tarefas, carregar e seguir [.sdlc/skills/plane-task-creation/SKILL.md](../plane-task-creation/SKILL.md)
- Antes de implementar: command `start_change` + [.sdlc/workflows/change-lifecycle.md](../../workflows/change-lifecycle.md)
- Ao abrir PR no GitHub, comentar no work item Plane com link do PR
- Pages: usar para documentação de produto; specs declarativas continuam em `specs/`

## Pages (documentação)

```text
create_project_page:
  project_id: <uuid>
  name: "ADR-001 Sheet Canvas"
  description_html: "<p>Decisão arquitetural…</p>"
```

Para wiki transversal ao workspace: `create_workspace_page`.

## Do not

- Commitar `PLANE_API_KEY` ou tokens
- Duplicar specs inteiras no Plane — linkar para `specs/` no repo
- Deletar work items sem confirmação humana

## Docs

- [.sdlc/integrations/plane.md](../../integrations/plane.md)
- [.sdlc/workflows/plane-lifecycle.md](../../workflows/plane-lifecycle.md)
