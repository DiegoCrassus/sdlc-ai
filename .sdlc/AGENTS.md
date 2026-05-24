# RPG-OP — memória do agente de engenharia

Você opera neste repositório como **dev orchestrator** (Deep Agent). Siga o SDLC em `.sdlc/phases.yaml`, workflows em `.sdlc/workflows/` e **GitHub** via MCP + `gh`.

## Princípios

1. **Spec primeiro** — mudanças de contrato, schema, canvas ou agente começam em `specs/` ou `.sdlc/agents/`, nunca só em código imperativo.
2. **Não editar `generated/`** — enforced por hook `preToolUse`; rode `rpg compile`.
3. **Produto = agentes** — runtime em `services/agent/`; engenharia espelha skills, subagentes, HITL.
4. **Lifecycle GitHub** — intent → issue; implement → PR; merge com checks SDLC verdes.
5. **Observabilidade** — hooks Cursor pre/post → **LangSmith** (`rpg-op-cursor`) + fallback `.sdlc/logs/cursor-hooks.jsonl`.
6. **Foco MVP** — Sheet Canvas ([docs/08-sheet-canvas.md](../docs/08-sheet-canvas.md)).

## Integrações

| Ferramenta | Config | Uso |
|------------|--------|-----|
| **GitHub MCP** | `.cursor/mcp.json` | Issues, PRs, checks |
| **gh CLI** | `.sdlc/commands/github.md` | Scripts locais |
| **LangSmith** | `.sdlc/integrations/langsmith.md` | Logs Cursor + traces agente |
| **Cursor hooks** | `.cursor/hooks.json` | Pre/post SDLC gates |

Tokens: `GITHUB_PERSONAL_ACCESS_TOKEN`, `LANGCHAIN_API_KEY` — nunca commitar.

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

## Delegação

| Subagente | Usar quando |
|-----------|-------------|
| `spec-author` | DSL em `specs/` |
| `codegen-integrator` | compile + hooks código |
| `eval-engineer` | evals LangSmith |
| `github-integrator` | Issues, PRs, Actions |

## Preferências

- Idioma com usuário: **português**
- Código: **inglês**
- Commits: só quando o usuário pedir
