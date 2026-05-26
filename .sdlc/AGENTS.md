# RPG-OP — memória do agente de engenharia

Você opera neste repositório como **dev orchestrator** (Deep Agent). Siga o SDLC em `.sdlc/phases.yaml`, workflows em `.sdlc/workflows/` e **GitHub** via MCP + `gh`.

## Princípios

1. **Plane primeiro** — toda alteração começa com task Plane `RPG-N` bem descrita.
2. **Lifecycle GitHub** — Plane task → `start_change` → branch → implement → `finish_change` → PR → Actions → aprovação humana → merge em `develop`.
3. **Branch obrigatória** — toda alteração de código em `feature/<RPG-N>` ou `bugfix/<RPG-N>`, sempre a partir de `develop`; nunca commit em `main`/`develop`.
4. **Qualidade obrigatória** — PR roda lint e testes; falha cria issue e aciona `issue_resolution`.
5. **Produto em `apps/`** — runtime vive em `apps/backend/` e `apps/frontend/`.
6. **Observabilidade** — hooks Cursor pre/post → **LangSmith** (`rpg-op-cursor`) + fallback `.sdlc/logs/cursor-hooks.jsonl`.
7. **Agentes canônicos em `.sdlc`** — YAML operacional vive em `.sdlc/agents/`; `.cursor/agents/` apenas adapta uso na IDE.

## Integrações

| Ferramenta | Config | Uso |
|------------|--------|-----|
| **GitHub MCP** | `.cursor/mcp.json` | Issues, PRs, checks |
| **Plane MCP** | `.cursor/mcp.json` | Tarefas, sprints, Pages (docs) |
| **Supabase MCP** | `.cursor/mcp.json` | Database/docs em modo read-only |
| **gh CLI** | `.sdlc/commands/github.md` | Scripts locais |
| **LangSmith** | `.sdlc/integrations/langsmith.md` | Logs Cursor + traces agente |
| **Cursor hooks** | `.cursor/hooks.json` | Pre/post SDLC gates |

Tokens: `GITHUB_PERSONAL_ACCESS_TOKEN`, `PLANE_API_KEY`, `SUPABASE_ACCESS_TOKEN`, `LANGCHAIN_API_KEY` — nunca commitar.

## Hooks (pre / post)

| Pre | Post |
|-----|------|
| sessionStart | sessionEnd |
| beforeSubmitPrompt | stop |
| preToolUse | postToolUse / postToolUseFailure |
| beforeShellExecution | afterShellExecution |
| beforeMCPExecution | afterMCPExecution |

Registry: `.sdlc/hooks.yaml` · Docs: `.cursor/hooks/README.md`

## Gates antes de PR

1. `make test`
2. `make lint`
3. `make validate`
4. PR checklist `.github/PULL_REQUEST_TEMPLATE.md`

## Commands

Commands em `.sdlc/commands/` agrupam skills, agentes e procedimentos. Use:

| Command | Usar quando |
|---------|-------------|
| `start_change` | Antes de qualquer edição de código — branch + Plane In Progress |
| `finish_change` | Ao concluir unidade de trabalho — test/lint/validate, commit, push, PR |
| `plane_backlog_plan` | Analisar intent e criar/atualizar tarefas no backlog Plane |
| `architecture_documentation` | Documentar arquitetura, infra, migrations, testes, Makefile e Plane Infrastructure |
| `plane_card_execution` | Mover card Plane, executar tarefa e registrar evidência |
| `pr_code_review` | Revisar PR no momento da criação/atualização |
| `pr_approval_watch` | Acompanhar aprovação e Actions até `develop` ficar verde |
| `issue_resolution` | Resolver issue gerada por CI, hook ou review |
| `issue_resolution_validation` | Validar issue resolvida e aprovar/mergear em `develop` ou comentar bloqueio |
| `technical_documentation` | Criar ou atualizar documentação técnica versionada |
| `business_documentation` | Criar ou atualizar documentação de negócio e Plane Pages |

## Delegação

| Subagente | Usar quando |
|-----------|-------------|
| `spec-author` | DSL em `specs/` |
| `codegen-integrator` | compile + hooks código |
| `eval-engineer` | evals LangSmith |
| `sdlc-doctor` | Diagnóstico de saúde SDLC AI-native |
| `github-integrator` | Issues, PRs, Actions |
| `plane-integrator` | Work items, sprints, Pages |
| `code-reviewer` | Revisão técnica de PR |
| `pr-approver` | Aprovação/watch de PR e Actions |
| `issue-resolver` | Correção autônoma de issues geradas |

## Workflows canônicos

| Workflow | Arquivo |
|----------|---------|
| Toda alteração | `.sdlc/workflows/change-lifecycle.md` |
| GitHub PR/merge | `.sdlc/workflows/github-lifecycle.md` |
| Plane backlog | `.sdlc/workflows/plane-lifecycle.md` |
| Lint e bugs | `.sdlc/workflows/lint-bug-resolution.md` |

## Preferências

- Idioma com usuário: **português**
- Código: **inglês**
- Commits: **obrigatório** ao concluir unidade de trabalho via `finish_change` (hooks bloqueiam commit em branch protegida)
