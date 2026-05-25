# Pendências SDLC AI-native — RPG-OP

**Data da validação:** 2026-05-25  
**Maturidade atual:** **L1** (meta **L2** — evals smoke LangSmith)  
**Validação:** `rpg validate specs/` OK · `make test` 18 passed · `validate.sh` OK

---

## Visão geral do estado

```
Camada               Status
─────────────────────────────────────────────────────
.sdlc/ harness       ✅ Ativo (agentes em .sdlc/agents/, phases.yaml)
.cursor/ IDE         ✅ Hooks, rules, MCP config, skills
specs/               ✅ 6 ficheiros (canvas, sheet, 2 subagents, api, analysis)
generated/           ✅ Pydantic, JSON Schema, OpenAPI, TS, manifest, skills, registry
packages/rpg_dsl     ✅ validate/compile via python -m rpg_dsl._cli
apps/backend         ✅ FastAPI, workspaces, template, characters, sheets, extend
apps/frontend        ✅ React/Vite, SessionBar, SheetCanvas editável, dashboard GM
Plane                ✅ PoC work items RPG-47–78; Fase 1+ a criar
GitHub / gh CLI      ✅ gh instalado; PAT no .env (via ./launch.sh)
LangSmith            ⚠️  LANGSMITH_* no .env; confirmar traces no dashboard
Evals smoke          ❌ specs/evals/ e generated/evals/ pendentes (RPG-64, RPG-32)
docs/status          ✅ Atualizado 2026-05-25
```

---

## PoC de produto (estado)

| Fase | Escopo | Código | Plane |
|------|--------|--------|-------|
| **0** | DSL, specs, compile, CI | ✅ | evidências wiki |
| **1** | Dashboard, workspace, D&D 5e seed | ✅ | RPG-47–55 Done |
| **2** | DPA stub, upload, analyze, publish | ✅ | RPG-56–63 Done |
| **3** | RBAC, fichas, dashboard mestre | ✅ | RPG-65–72 Done |
| **4** | template/extend, migração fichas | ✅ | RPG-73–78 Done |
| **2.9** | Evals smoke + LangSmith | ❌ → Fase 1 | RPG-64 Todo |

Wiki: [docs/poc/00-indice-poc.md](../poc/00-indice-poc.md) · Roadmap: [docs/05-roadmap.md](../05-roadmap.md)

---

## 1. DSL `rpg_dsl`

| # | Item | Status |
|---|------|--------|
| 1.1 | `@Field`, `@Canvas`, `@Sheet` | ✅ |
| 1.2 | `python -m rpg_dsl._cli validate specs/` | ✅ |
| 1.3 | `rpg` no PATH (`pip install -e packages/rpg_dsl`) | ⚠️ Opcional; module funciona |
| 1.4–1.8 | compile pydantic, openapi, typescript, agent_manifest, skills | ✅ |
| 1.9 | compile `--target evals` | ❌ Aguarda specs/evals/ |
| 1.10 | compile `--target all` completo | ⚠️ Parcial (sem evals/cursor_rules) |

---

## 2. Specs `specs/`

| # | Item | Arquivo | Status |
|---|------|---------|--------|
| 2.1 | Canvas D&D 5e | `specs/templates/dnd5e_canvas.py` | ✅ |
| 2.2 | Schema D&D 5e | `specs/templates/dnd5e_sheet.py` | ✅ |
| 2.3 | Orchestrator | `specs/agents/orchestrator.py` | ✅ |
| 2.4 | sheet-template-analyst | `specs/agents/sheet_template_analyst.py` | ✅ |
| 2.5 | BFF v1 | `specs/api/bff_v1.py` | ⚠️ Revisar drift vs routers actuais |
| 2.6 | TemplateAnalysisResult | `specs/templates/analysis_result.py` | ✅ |
| 2.7 | Evals smoke (2 fixtures) | `specs/evals/` | ❌ |

---

## 3. Ambiente local (dev)

| # | Item | Status |
|---|------|--------|
| 3.1 | venv `apps/backend/.venv` | ✅ (`make setup`, `./dev.sh`) |
| 3.2 | Frontend `apps/frontend/node_modules` | ✅ |
| 3.3 | `make` + `uv` | ✅ bash / WSL / Linux |
| 3.4 | Atalho dev | ✅ `./dev.sh` |
| 3.5 | `make test` | ✅ 18 passed |
| 3.6 | `make dev` / `./dev.sh` | ✅ |
| 3.7 | Smoke API | ✅ `apps/backend/scripts/smoke_test.py` |

---

## 4. Integrações

| Integração | Config | Status |
|------------|--------|--------|
| GitHub MCP | `.cursor/mcp.json` + `.env` | ⚠️ Abrir Cursor via `./launch.sh` |
| Plane MCP | `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG` | ✅ Scripts sync wiki OK |
| LangSmith | `LANGSMITH_*` no `.env` | ⚠️ Confirmar traces |
| Supabase MCP | read-only | ✅ Token no .env |

Scripts Plane: `plane-sync-wiki-doc.sh`, `plane-mcp-check.sh`

---

## 5. Gates e CI

| Gate | Local | CI (`.github/workflows/sdlc.yml`) |
|------|-------|-----------------------------------|
| rpg validate | ✅ | ✅ |
| pytest | ✅ 18 tests | ⚠️ continue-on-error |
| smoke | ✅ | import check only |
| evals LangSmith | ❌ | ❌ |

---

## 6. Drift conhecido (documentação ↔ código)

| Área | Nota |
|------|------|
| Roadmap MVP1 fala em `campaigns` | Implementação usa **workspaces** (PoC 1 entregue) |
| `specs/api/bff_v1.py` | Endpoints evoluíram (template/extend, characters, sheets) |
| LLM multimodal DPA | PoC 2 usa stub; integração LLM → Fase 1.3 |
| `backend/` legado | READMEs de redirecionamento; runtime em `apps/backend/` |

---

## Ordem de execução recomendada (próximo ciclo)

```
Passo  O que fazer                          Desbloqueia
──────────────────────────────────────────────────────────
  1    Evals smoke (specs/evals + RPG-64)   L2 + gate eval
  2    Revisar specs/api vs routers         Contrato BFF alinhado
  3    rpg compile --target all              generated/ completo
  4    Endurecer pytest no CI                Gate required
  5    Integração LLM no DPA Agent           Fase 1.3 (pós-L2)
```

---

## Métricas de maturidade

| Nível | Critério | Estado |
|-------|----------|--------|
| **L0** | Harness scaffolded | ✅ |
| **L1** | compile + manifest + PoC 0–4 | ✅ **Atual** |
| **L2** | evals smoke em CI (LangSmith) | ❌ RPG-64 |
| L3 | Deep Agent runtime wired | backlog |
| L4 | Migrações sheet geradas; RAG na DSL | backlog |

---

## Referências

| Doc | Conteúdo |
|-----|----------|
| `docs/sdlc/ai-native.md` | Modelo AI-native |
| `docs/05-roadmap.md` | Roadmap pós-PoC (Fases 1–4) |
| `docs/poc/00-indice-poc.md` | Índice PoC + status |
| `docs/status/pendencias-humanas.md` | Ações só humanas |
| `.sdlc/AGENTS.md` | Memória do orchestrator |
