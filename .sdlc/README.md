# SDLC AI-native — RPG-OP

Este diretório é o **harness de engenharia** do projeto. O Deep Agent orquestra Plane task → branch → implementação → PR → Actions → aprovação → merge em `develop`.

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

1. **Plane task** — `RPG-N` criada e documentada.
2. **Branch** — `feature/RPG-N` ou `bugfix/RPG-N`, sempre a partir de `develop`.
3. **PR** — base `develop`, checklist e Plane linkados.
4. **Actions** — lint e testes obrigatórios.
5. **Issue resolution** — falha cria issue e aciona `issue-resolver`.
6. **Merge** — somente com checks verdes e aprovação humana explícita.

Ver [integrations/github.md](integrations/github.md) e [workflows/github-lifecycle.md](workflows/github-lifecycle.md).

## Camadas

| Camada | Onde | Papel |
|--------|------|-------|
| **Harness SDLC** | `.sdlc/` | Como o agente desenvolve o repo |
| **Agentes canônicos** | `.sdlc/agents/` | YAMLs operacionais: prompts, skills, tools, permissões e delegação |
| **IDE + MCP** | `.cursor/` | Regras, adapters, skills de atalho, hooks e MCP |
| **Adapters Cursor** | `.cursor/agents/` | Quando chamar cada agente no Cursor; não duplica configuração operacional |
| **Remote** | `.github/` | Issues, PRs, Actions |

## Comandos

Commands combinam skills, agentes e procedimentos. Alguns são scripts locais;
outros são playbooks para delegação agentic.

```bash
make test
make lint
make validate
```

Playbooks iniciais:

- `.sdlc/commands/plane-backlog-plan.md`
- `.sdlc/commands/technical-documentation.md`
- `.sdlc/commands/business-documentation.md`

## Workflows principais

- [workflows/change-lifecycle.md](workflows/change-lifecycle.md)
- [workflows/github-lifecycle.md](workflows/github-lifecycle.md)
- [workflows/lint-bug-resolution.md](workflows/lint-bug-resolution.md)
