# Roadmap — RPG-OP

Roadmap **realista pós-PoC** para evoluir de prova de conceito local até piloto com mesas reais e produto sustentável.

O norte permanece: o mestre envia uma ficha real da mesa, o sistema deriva `SheetSchema` + `CanvasSpec`, e jogadores usam um canvas visual fiel ao modelo original — com publicação sempre confirmada pelo mestre (HITL).

## Estado atual (2026-05-25)

| Área | Estado |
|------|--------|
| **PoC (fases 0–4)** | ✅ Concluído — ver [docs/poc/00-indice-poc.md](poc/00-indice-poc.md) |
| SDLC AI-native | Harness `.sdlc/` + `.cursor/` — maturidade **L1** |
| DSL | `rpg validate specs/` — 6 ficheiros; compile parcial (sem evals) |
| Runtime | `apps/backend/` (FastAPI) + `apps/frontend/` (React/Vite) |
| Testes | 18 pytest passed |
| Dev local | `make setup`, `./dev.sh` — toolchain 100% shell (`.sh`) |
| Plane | Work items RPG-47–78 (histórico PoC); wiki a sincronizar |
| LangSmith / MCP | Credenciais no `.env`; evals smoke pendente (RPG-64) |

### O que o PoC provou

1. **Workspace agnóstico** — cada mesa com schema/canvas próprios.
2. **Sheet Canvas editável** — mestre e jogador no mesmo layout visual.
3. **DPA Agent (stub)** — upload → análise → draft → publish com HITL.
4. **Sessão de mesa** — RBAC, dashboard GM, revisões básicas.
5. **Extensão de template** — novos campos sem reupload, migração de fichas.
6. **SDLC AI-native** — specs DSL → artefatos gerados sem drift manual.

Detalhe por fase: [docs/poc/](poc/00-indice-poc.md).

## Estado atual

## Premissas do roadmap pós-PoC

- Não expandir para chat de regras, plugins globais ou mobile antes de **piloto estável**.
- LLM multimodal entra **depois** de evals smoke e contrato BFF alinhado.
- PostgreSQL e auth real são pré-requisitos de alpha fechado, não do PoC.
- Plane continua como backlog de produto; GitHub como SDLC de código.

- DSL `rpg_dsl` mínima instalada e executável via `rpg`.
- Specs em `specs/templates/` para ficha e canvas D&D 5e de referência.
- Spec do subagente `sheet-template-analyst`.
- `rpg validate specs/` e `rpg compile` funcionando localmente.
- Targets gerados prioritários: Pydantic, JSON Schema, TypeScript, OpenAPI e agent manifest.
- CI local via `.sdlc/scripts/validate.ps1`.

## Fase 1 — Hardening (4–6 semanas)

**Objetivo:** fechar lacunas técnicas do PoC e atingir maturidade SDLC **L2**.

| # | Entrega | Critério |
|---|---------|----------|
| 1.1 | Evals smoke LangSmith | 2 fixtures em `specs/evals/`; gate verde; RPG-64 Done |
| 1.2 | Contrato BFF alinhado | `specs/api/bff_v1.py` ↔ routers actuais; recompile OpenAPI/TS |
| 1.3 | DPA Agent com LLM real | Substituir stub determinístico; traces LangSmith por análise |
| 1.4 | CI obrigatório | pytest + validate required no workflow SDLC |
| 1.5 | Auth mínima | Sessão ou JWT local; remover mock SessionBar como default |

**Saída:** demo repetível para investidor/mesa interna; L2 no SDLC Doctor.

- Modelo de dados inicial: `campaigns`, `campaign_members`, `sheet_templates`, `characters`, `sheets`, `sheet_revisions`, `attachments`.
- BFF `/v1` com rotas de campanha, template publicado e fichas.
- Payload agregado para UI: `sheet` + `schema_json` + `canvas_spec_json` + `template_version`.
- Validação de dados da ficha contra JSON Schema do template.
- `SheetCanvas` React com apresentações mínimas: `field_grid`, `stat_row`, `rich_text`.
- Fluxo jogador: abrir a própria ficha, editar campos permitidos e salvar.
- Fluxo mestre: ver fichas da campanha em dashboard simples.
- Seed/fixture de campanha piloto para testar ponta a ponta.

## Fase 2 — Alpha fechado (6–8 semanas)

**Objetivo:** 2–3 mesas piloto com dados persistentes e deploy staging.

| # | Entrega | Critério |
|---|---------|----------|
| 2.1 | PostgreSQL | Migrar de SQLite dev; migrations versionadas em `infra/migrations/` |
| 2.2 | Convites reais | GM convida jogador por email/link; RBAC por membro |
| 2.3 | Object storage | Anexos de ficha (PDF/PNG) em S3/Supabase Storage |
| 2.4 | Deploy staging | API + frontend acessíveis na internet (HTTPS) |
| 2.5 | Observabilidade | LangSmith + health checks + logs estruturados |
| 2.6 | Piloto documentado | Runbook para mesa; feedback capturado no Plane |

**Saída:** mesas externas usam o produto sem suporte técnico contínuo.

- Upload de ficha exemplo (`PDF`, `PNG`, `JPG`) em `template/source`.
- Serviço de agente com orquestrador leve e subagente `sheet-template-analyst`.
- Skill `template-analysis` com passos: segmentar regiões, listar campos, inferir tipos, montar canvas e emitir warnings.
- Persistência de `analysis_json`, `schema_json` e `canvas_spec_json` como draft.
- UI de revisão com passos da análise + preview do canvas ao lado do exemplo.
- Correções manuais do mestre antes de publicar.
- Endpoint `template/publish` com confirmação humana.
- Evals smoke com 2 fixtures anonimizadas e trace LangSmith.

## Fase 3 — Beta (8–12 semanas)

**Objetivo:** robustez de produto para dezenas de mesas.

| # | Entrega | Critério |
|---|---------|----------|
| 3.1 | Análise multimodal robusta | PDFs complexos, múltiplas páginas, warnings acionáveis |
| 3.2 | Histórico completo | Diff entre revisões; restaurar versão anterior |
| 3.3 | Notificações | GM alertado quando jogador atualiza ficha |
| 3.4 | Performance | Canvas com 50+ campos sem degradação perceptível |
| 3.5 | Onboarding | Wizard de primeira mesa; docs para GM e jogador |
| 3.6 | Billing / limites (opcional) | Planos por workspace se necessário para sustentação |

**Saída:** product-market fit inicial com fichas visuais customizadas.

**Entregas principais**

## Fase 4 — Produto (12+ semanas)

Horizonte após beta estável. Priorização via Plane com base em feedback das mesas piloto.

| Fase | Conteúdo |
|------|----------|
| **F4.1 Assistente** | Chat sobre ficha, sugestões de preenchimento, ações assistidas |
| **F4.2 Registry** | Presets D&D/Tormenta como atalho opcional (não substituem ficha do GM) |
| **F4.3 Import em massa** | OCR de fichas preenchidas antigas |
| **F4.4 Mobile** | PWA ou app nativo; leitura offline parcial |
| **F4.5 Automações** | RAG de regras, subagentes por cenário, integrações VTT |

## Sequência recomendada

## Sequência recomendada

```text
PoC 0–4 ✅  →  Fase 1 Hardening  →  Fase 2 Alpha  →  Fase 3 Beta  →  Fase 4 Produto
                  ↑ estamos aqui
```

1. ~~PoC 0~~ — DSL + compile ✅
2. ~~PoC 1~~ — workspaces + SheetCanvas ✅
3. ~~PoC 2~~ — DPA stub + publish ✅ (LLM real → Fase 1.3)
4. ~~PoC 3~~ — sessão real + RBAC ✅
5. ~~PoC 4~~ — extensão de template ✅
6. **Agora:** Fase 1 — evals, contrato BFF, LLM, CI
7. **Depois:** Fase 2 — PostgreSQL, convites, staging, piloto

---

## Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| PoC vira “produto” sem hardening | Fase 1 explícita antes de alpha |
| LLM gera schema errado | Evals + HITL + preview antes de publish |
| Drift specs ↔ código | `rpg compile` obrigatório no PR; revisão BFF spec |
| Escopo para chat/mobile cedo | Roadmap por fases; Plane prioriza Fase 1–2 |
| Migração de template quebra fichas | Versionamento append-only (já provado no PoC 4) |

## Definição de sucesso do ciclo

## Definição de sucesso por marco

| Marco | Sucesso |
|-------|---------|
| **PoC** ✅ | Mesa completa no localhost: criar workspace, publicar template, jogador edita, GM estende |
| **Fase 1** | L2 SDLC; LLM real; CI verde sem `continue-on-error` |
| **Fase 2** | 3 mesas piloto em staging por 4+ semanas |
| **Fase 3** | 10+ mesas ativas; NPS interno positivo |
| **Fase 4** | Receita ou sustentação definida; roadmap F4.x priorizado |

---

## Rastreabilidade

| Documento | Conteúdo |
|-----------|----------|
| [docs/poc/00-indice-poc.md](poc/00-indice-poc.md) | PoC entregue — fases 0–4 |
| [docs/status/pendencias-sdlc.md](status/pendencias-sdlc.md) | Gates técnicos e maturidade |
| [docs/status/pendencias-humanas.md](status/pendencias-humanas.md) | Ações manuais |
| [docs/product/visao-e-escopo.md](product/visao-e-escopo.md) | Visão de produto |
| [docs/product/sheet-canvas.md](product/sheet-canvas.md) | Modelo de canvas |
| Plane projeto **RPG** | Backlog Fase 1+ (labels `phase-1`, `phase-2`, …) |
