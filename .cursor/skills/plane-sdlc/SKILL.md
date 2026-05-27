# Skill: Plane SDLC (MCP)

> **Workflow authority:** `docs/sdlc/change-lifecycle.md`

## Purpose

Criar, atualizar e encerrar **work items exclusivamente no Plane** via MCP. Nunca criar tarefas, backlogs ou evidências de ticket em arquivos locais (`specs/`, `TICKETS.md`, etc.).

## When to use

- Antes de qualquer implementação (**start-change** passo 1)
- Ao planejar epic ou sub-tarefas (Planner / **task-creation**)
- Ao registrar evidência e mover card para Done (**finish-change**)

## MCP

- Config: `.cursor/mcp.json` — server `plane`
- Env: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_PROJECT_NAME` (`.env`)

| Campo | Valor |
|-------|-------|
| Workspace | `investments-sdlc` |
| Project | `investiments` |
| Card ID | `INVESTIMENTS-N` (identifier do project) |

## Procedure — criar work item

1. Conectar via Plane MCP (stdio).
2. Criar issue/work item no project `investiments`.
3. **Título:** `[AI][TYPE] Short imperative title` (ver `task-creation.md`).
4. **Descrição:** story, scope, non-goals, acceptance criteria, DoD (markdown no corpo do card).
5. **Estado:** In Progress (ou equivalente do board).
6. Anotar `INVESTIMENTS-N` retornado — obrigatório para branch e commits.

## Procedure — evidência e conclusão

1. Comentar no card: link do PR, saída de testes, `make sdlc-doctor`.
2. Mover card para **Done** somente após merge em `develop` + CI verde.
3. Nunca duplicar evidência em pasta local.

## Proibições

- **Nunca** criar `specs/` ou arquivos `INVESTIMENTS-N.md` no repositório para gestão de tarefas.
- **Nunca** usar GitHub Issue como substituto do Plane quando MCP/API estiver disponível.
- **Nunca** inventar `INVESTIMENTS-N` sem ID real do Plane.

## Failure modes

| Situation | Action |
|-----------|--------|
| MCP/ API indisponível | **Parar** — corrigir token/workspace; não criar backlog local |
| Token 401 | Validar `PLANE_API_KEY` e `PLANE_WORKSPACE_SLUG=investments-sdlc` |
| Sem card ID | **Parar** — criar card no Plane primeiro |
