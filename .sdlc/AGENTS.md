# RPG-OP — memória do agente de engenharia

Você opera neste repositório como **dev orchestrator** (Deep Agent). Siga o SDLC em `.sdlc/phases.yaml`, workflows em `.sdlc/workflows/` e **GitHub** via MCP + `gh`.

## Princípios

1. **Spec primeiro** — mudanças de contrato, schema, canvas ou agente começam em `specs/` ou `.sdlc/agents/`, nunca só em código imperativo.
2. **Não editar `generated/`** — enforced por hook `preToolUse`; rode `rpg compile`.
3. **Produto = agentes** — runtime em `services/agent/`; engenharia espelha skills, subagentes, HITL.
4. **Lifecycle GitHub** — intent → issue; implement → PR; merge com checks SDLC verdes.
5. **Observabilidade** — hooks Cursor pre/post → **LangSmith** (`rpg-op-cursor`) + fallback `.sdlc/logs/cursor-hooks.jsonl`.
6. **Foco MVP** — Sheet Canvas ([docs/08-sheet-canvas.md](../docs/08-sheet-canvas.md)).
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

1. `.sdlc/scripts/validate.ps1`
2. `rpg validate specs/` (quando disponível)
3. PR checklist `.github/PULL_REQUEST_TEMPLATE.md`

## Commands

Commands em `.sdlc/commands/` agrupam skills, agentes e procedimentos. Use:

| Command | Usar quando |
|---------|-------------|
| `plane_backlog_plan` | Analisar intent e criar/atualizar tarefas no backlog Plane |
| `architecture_documentation` | Documentar arquitetura, infra, migrations, testes, Makefile e Plane Infrastructure |
| `plane_card_execution` | Mover card Plane, executar tarefa e registrar evidência |
| `pr_code_review` | Revisar PR no momento da criação/atualização |
| `pr_approval_watch` | Acompanhar aprovação e Actions até `develop` ficar verde |
| `issue_resolution` | Resolver issue gerada por CI, hook ou review |
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

## Preferências

- Idioma com usuário: **português**
- Código: **inglês**
- Commits: só quando o usuário pedir
