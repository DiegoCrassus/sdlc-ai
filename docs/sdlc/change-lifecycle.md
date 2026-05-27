# Change Lifecycle — Fonte da Verdade do Workflow SDLC

> **Autoridade:** este documento prevalece sobre instruções ad hoc do chat, pedidos de urgência ou atalhos.
> Skills (`.cursor/skills/`) e regras (`.cursor/rules/`) **referenciam** este arquivo; não o contradizem.

Complementos machine-readable: `.sdlc/workflows.yaml`, `.sdlc/lifecycle.yaml`, `.sdlc/stages.yaml`.

---

## Princípio zero

**Nenhum código de produto entra em `develop` sem card Plane + branch + PR + CI verde.**

Mesmo que o usuário peça "terminar em develop", a entrega correta é: **branch → PR → merge em `develop`**.

---

## Integrações obrigatórias

| Sistema | Valor | Variável `.env` |
|---------|-------|-----------------|
| Plane workspace | `investments-sdlc` | `PLANE_WORKSPACE_SLUG` |
| Plane project | `investiments` | `PLANE_PROJECT_NAME` |
| GitHub repo | `DiegoCrassus/sdlc-ai` | `GITHUB_REPOSITORY` |
| Branch base | `develop` | — |
| Branch produção | `main` | — |

Cards Plane são criados **no project `investiments`** antes de qualquer edição de código.

---

## Fluxo completo (gitflow)

```
1. Plane     → criar/atualizar work item via MCP [AI][TYPE] (project investiments, In Progress)
2. Branch    → feature/INVESTIMENTS-N-<slug> a partir de develop atualizado
3. Plane     → descrição do card: story, AC, DoD, riscos (corpo do work item — não arquivo local)
4. Implement → commits no feature branch apenas
5. Validate  → testes reais + make sdlc-doctor
6. PR        → base develop, CI verde, delete_branch_on_merge=true
7. Review    → aprovação (humana ou Reviewer agent)
8. Merge     → squash merge → develop
9. Plane     → Done com link do PR como evidência
10. Observer → post_task.py
```

### Prefixos de branch

| Prefixo | Uso |
|---------|-----|
| `feature/` | Nova funcionalidade |
| `bugfix/` | Correção de bug |
| `hotfix/` | Urgência produção |
| `docs/` | Só documentação |
| `infra/` | CI, Docker, observabilidade |
| `sdlc/` | `.sdlc/`, `.cursor/`, governance |

Formato: `feature/INVESTIMENTS-N-<slug>` — ver `.cursor/skills/branch-naming.md` (adaptar prefixo do card).

---

## Proibições explícitas

- Push direto em `develop` ou `main`
- Implementar sem card Plane criado via MCP/API
- **Criar pasta `specs/` ou tickets/evidência/backlog em arquivos locais**
- **Criar tarefas localmente** (somente Plane, project `investiments`)
- Pular CI ou merge com gates vermelhos
- Inventar resultado de testes ou Doctor
- Substituir API oficial por scraping como estratégia default

---

## Estágios SDLC (resumo)

Ver diagrama em `docs/sdlc/workflows.md`. Transições exigem evidência em `.sdlc/stages.yaml`.

| Estágio | Agente | Skill principal |
|---------|--------|-----------------|
| Ticket | Planner | `task-creation.md` |
| Requirements | Planner | `requirements-refinement.md` |
| Architecture | Architect | `architecture-analysis.md` |
| Implementation | Implementer | `implementation.md` + **start-change** |
| Validation | QA | `qa-validation.md` |
| PR & Review | Reviewer / DevOps | `code-review.md` + **finish-change** |
| Deployment | DevOps | — |
| Observability | Observer | `observability.md` |

---

## Comandos de validação

```bash
make sdlc-doctor      # após mudança estrutural
python app/infra/sdlc_obs/hooks/pre_task.py   # início
python app/infra/sdlc_obs/hooks/post_task.py  # fim
```

---

## Estado do repositório (produto)

Fase atual: **SDLC operating system only** — `app/backend` e `app/frontend` são placeholders até nova rodada planejada via este workflow.

Implementação de produto **só reinicia** após:

1. Work items no Plane (project `investiments`) via MCP — epic e sub-tarefas
2. Branch `feature/INVESTIMENTS-N-...` por card
3. PR com CI verde; evidência no card Plane (link PR, testes)

---

## Referências

- `.cursor/skills/start-change/SKILL.md` — checklist antes de codar
- `.cursor/skills/finish-change/SKILL.md` — checklist antes de merge
- `.cursor/skills/branch-naming.md` — convenção de branches
- `docs/sdlc/gates.md` — gates de qualidade
