# SDLC AI-native — RPG-OP

Este diretório é o **harness de engenharia** do projeto. O [Deep Agent](https://docs.langchain.com/oss/python/deepagents/index) orquestra intent → spec → compile → implement → eval → deploy.

## Layout

```
.sdlc/
├── config.yaml           # Paths, gates, modelo do dev orchestrator
├── AGENTS.md             # Memória persistente do agente de engenharia
├── phases.yaml           # Fases SDLC e critérios de saída
├── agents/               # Definições do dev orchestrator + subagentes
├── skills/               # Agent Skills (padrão agentskills.io)
├── workflows/            # Playbooks executáveis pelo agente
├── evals/                # Suites e config de evals
├── integrations/         # GitHub MCP, plataformas (platforms.yaml)
├── commands/             # Registry de comandos, playbooks e gh reference
├── templates/            # ADR, intent, PR
└── scripts/              # validate, gh-issue-intent, gh-pr-open, …
```

## GitHub lifecycle

1. **Intent** — issue (template `.github/ISSUE_TEMPLATE/`)
2. **Spec** — branch + `specs/`
3. **PR** — checklist + workflow `SDLC`
4. **MCP** — agente opera GitHub no Cursor

Ver [integrations/github.md](integrations/github.md) e [workflows/github-lifecycle.md](workflows/github-lifecycle.md).

## Specs vs hooks

| Camada | Onde | Papel |
|--------|------|-------|
| **Declarativo** | `specs/` (repo root) | DSL Python — fonte da verdade |
| **Harness SDLC** | `.sdlc/` | Como o agente desenvolve o repo |
| **Agentes canônicos** | `.sdlc/agents/` | YAMLs operacionais: prompts, skills, tools, permissões e delegação |
| **IDE + MCP** | `.cursor/` | Regras, adapters, skills de atalho, hooks e MCP |
| **Adapters Cursor** | `.cursor/agents/` | Quando chamar cada agente no Cursor; não duplica configuração operacional |
| **Remote** | `.github/` | Issues, PRs, Actions |

## Comandos (quando `rpg_dsl` estiver instalado)

Commands combinam skills, agentes e procedimentos. Alguns são scripts locais;
outros são playbooks para delegação agentic.

```bash
rpg validate specs/
rpg compile --target all
pytest backend/ packages/
```

Playbooks iniciais:

- `.sdlc/commands/plane-backlog-plan.md`
- `.sdlc/commands/technical-documentation.md`
- `.sdlc/commands/business-documentation.md`

## Documentação

- [docs/sdlc/ai-native.md](../docs/sdlc/ai-native.md)
- [workflows/intent-to-deploy.md](workflows/intent-to-deploy.md)
