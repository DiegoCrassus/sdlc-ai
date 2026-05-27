# AGENTS.md — Handbook dos Agentes SDLC AI-Native

Este arquivo é o **primeiro ponto de entrada** para qualquer agente em um novo chat.
Leia este arquivo antes de qualquer ação.

## Identidade do Projeto

- **Repositório:** `sdlc-ai`
- **Plane workspace:** `investments-sdlc` → `PLANE_WORKSPACE_SLUG`
- **Plane project:** `investiments` → `PLANE_PROJECT_NAME`
- **Repositório GitHub:** ver `.env` → `GITHUB_REPOSITORY`
- **SDLC version:** v2.0 — Autonomy Score 99%

## Fonte da verdade do workflow

**Leia primeiro:** [`docs/sdlc/change-lifecycle.md`](../docs/sdlc/change-lifecycle.md)

Este documento prevalece sobre instruções ad hoc do chat. Skills e regras referenciam-no; não o contradizem.

## Contexto Rápido

Este repositório é um **AI-Native SDLC**. Seu propósito é:
1. Ser o sistema operacional de desenvolvimento para projetos futuros
2. Demonstrar 99% de autonomia na entrega de software (da Issue ao merge)
3. Evoluir a si próprio via auditor autônomo

## Como Começar (qualquer nova tarefa)

```
1. Leia este arquivo (feito ✓)
2. Leia docs/sdlc/change-lifecycle.md     → workflow obrigatório (fonte da verdade)
3. Leia docs/sdlc/ai-native-sdlc.md       → lifecycle e estágios
4. Leia .sdlc/memory/operational-context.md → contexto de runtime
5. Identifique o estágio SDLC da tarefa (ticket/req/arch/impl/qa/review/deploy/obs)
6. Invoque o subagente correto para o estágio
7. Siga .cursor/skills/ correspondente (start-change antes de codar)
8. Emita métricas via pre_task.py e post_task.py
```

## Subagentes Disponíveis

| Agente | Arquivo | Estágio SDLC |
|--------|---------|-------------|
| Planner | `.cursor/subagents/planner.md` | ticket → requisitos |
| Architect | `.cursor/subagents/architect.md` | arquitetura |
| Implementer | `.cursor/subagents/implementer.md` | implementação |
| QA | `.cursor/subagents/qa.md` | validação |
| Reviewer | `.cursor/subagents/reviewer.md` | revisão |
| DevOps | `.cursor/subagents/devops.md` | deploy + PR lifecycle |
| Doctor | `.cursor/subagents/doctor.md` | validação estrutural |
| Observer | `.cursor/subagents/observer.md` | observabilidade |
| IssueAnalyst | `.cursor/subagents/issue-analyst.md` | triagem de issues |
| SDLCAuditor | `.cursor/subagents/sdlc-auditor.md` | auditoria autônoma |
| MigrationRunner | `.cursor/subagents/migration-runner.md` | migrations de banco |
| ContractValidator | `.cursor/subagents/contract-validator.md` | sync OpenAPI ↔ TS |
| AutoFixer | `.cursor/subagents/auto-fixer.md` | correção automática de CI |
| RollbackAgent | `.cursor/subagents/rollback-agent.md` | rollback automático |
| SecurityScanner | `.cursor/subagents/security-scanner.md` | scan de segurança |

## Skills Disponíveis

Todas em `.cursor/skills/`:
`requirements-refinement` · `architecture-analysis` · `implementation` · `qa-validation` ·
`code-review` · `observability` · `documentation` · `task-creation` · `branch-naming` ·
`container-validation` · `e2e-testing` · `secrets-management` · `performance-testing` ·
`auto-merge-policy` · `iac-generation`

## Comandos Disponíveis

| Comando | Propósito |
|---------|-----------|
| `/sdlc-plan` ou `@sdlc-plan` | Converte ideia em plano [AI][TYPE] |
| `/sdlc-implement` | Implementa uma tarefa planejada |
| `/sdlc-review` | Revisa diff de PR |
| `/sdlc-doctor` | Valida estrutura SDLC |
| `/sdlc-audit` | Auditoria completa → canvas de relatório |
| `/sdlc-handoff` | Gera handoff summary |

## Convenções Obrigatórias

- **Task names:** `[AI][TYPE] Short imperative title` — ex: `[AI][BACKEND] Add investment endpoint`
- **Branch names:** `feature/INVESTIMENTS-N-<slug>` — ver `.cursor/skills/branch-naming.md`
- **Antes de codar:** `.cursor/skills/start-change/SKILL.md` (card Plane + branch)
- **Antes de merge:** `.cursor/skills/finish-change/SKILL.md` (PR + CI verde)
- **Antes de qualquer tarefa:** métricas abertas automaticamente via `.cursor/hooks.json` (`sessionStart`); para stage/agent específicos, chamar `pre_task.py` manualmente
- **Depois de qualquer tarefa:** fechadas automaticamente via `stop`; para métricas detalhadas (tokens, tools, doctor), chamar `post_task.py` manualmente
- **Após mudança estrutural:** rodar `make sdlc-doctor`
- **Periodicamente:** rodar `make sdlc-audit` → target ≥ 90% Autonomy Score

## MCPs Ativos

- **GitHub MCP:** criar issues, PRs, gerenciar lifecycle de branches
- **Plane MCP:** criar cards, mover sprints, registrar evidências

## Makefile Targets Principais

```bash
make sdlc-doctor   # valida estrutura SDLC
make sdlc-audit    # auditoria completa → canvas
make obs-server    # dashboard de métricas em http://localhost:7700
make obs-init      # inicializa banco SQLite de observabilidade
make export-pdf    # gera PDF da simulação end-to-end
```

## Estado Atual do SDLC

- Autonomy Score: **99%** (70 PASS · 2 WARN · 0 FAIL)
- Health Score: **97%**
- Agentes implementados: 15
- Skills implementadas: 15
- CI/CD: `.github/workflows/ci.yml` (Doctor + secrets scan)
- Produto: `app/backend/` e `app/frontend/` — placeholders (sem código de app)
- IaC: `app/infra/terraform/` — placeholders

## Quando Escalar para Humano

Apenas nestes casos:
1. Mudança em `app/backend/auth/` com confidence score < 0.95
2. Decisão de cloud provider para produção (AWS/GCP/Azure)
3. Rollback cujo plano não está documentado no PR original

Em todos os outros casos: **o pipeline é 100% autônomo.**
