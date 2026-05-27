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
1. Plane     → card INVES-N (Todo após plano; In Progress no start-change)
2. start-change → plane_state.py in-progress ANTES de branch/código
3. Branch    → feature/INVES-N-<slug> a partir de develop
4. Implement → Task(Implementer) · commits no feature branch
5. Validate  → Task(QA) · testes reais + make sdlc-doctor
6. Review    → Task(Reviewer) · auto-merge-policy
7. PR        → push + gh/API · CI verde
8. Merge     → auto_merge_pr.py (autônomo — sem clique humano)
9. Plane     → Done (--plane-comment) + link PR
10. Observer → post_task.py
```

### Plane — estados obrigatórios

| Estado | Quando |
|--------|--------|
| **Todo** | Após Planner criar card |
| **In Progress** | **Obrigatório** ao iniciar implementação (`start-change`) |
| **Done** | Após merge autônomo + CI verde |

Script: `python3 .sdlc/scripts/plane_state.py in-progress --card INVES-N`

### GitHub Issues

Plane é tracker primário. Issues abertas → **Issue Analyst** (Task) tria/fecha duplicatas.
Script: `python3 .sdlc/scripts/github_issue_triage.py --close-superseded`

### Merge autônomo

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card INVES-N --plane-comment
```

Ver `.cursor/skills/finish-change/SKILL.md` e `auto-merge-policy.md`.

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
