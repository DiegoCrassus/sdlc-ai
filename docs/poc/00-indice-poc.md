# Índice — Proof of Concept (PoC)

Documentação do **PoC concluído** do RPG-OP (2026-05). Cada página descreve **objetivo**, **marcos entregues** e **critério de saída** de uma fase do PoC.

> **PoC ≠ produto.** O PoC valida a tese técnica e de UX em localhost. O [roadmap pós-PoC](../05-roadmap.md) define Fases 1–4 até piloto e beta.

## Visão da plataforma

O RPG-OP é uma **plataforma agnóstica de RPG**: cada **workspace** representa uma **mesa de RPG** independente. O mestre define como a ficha funciona; o sistema deriva schema, canvas e persistência a partir desse modelo.

| Conceito | Significado |
|----------|-------------|
| **Workspace** | Mesa de RPG — campanha, houserule ou one-shot |
| **Ficha** | Modelo de personagem (PDF, imagem, JSON ou texto) |
| **DPA Agent** | Agente que constrói schema, canvas e artefatos por modelo de RPG |
| **Sheet Canvas** | UI visual fiel ao layout da ficha original |
| **Usuários** | Base compartilhada; dados de workspace por FK |

Fonte técnica: [product/arquitetura-produto.md](../product/arquitetura-produto.md) · [product/sheet-canvas.md](../product/sheet-canvas.md)

---

## Fases do PoC (concluídas)

| Fase | Página | Foco | Status | Plane (histórico) |
|------|--------|------|--------|-------------------|
| **0** | [PoC 0 — Fundação SDLC](poc-0-fundacao-sdlc.md) | DSL, specs, compile, CI | ✅ | evidências wiki |
| **1** | [PoC 1 — Workspace e Canvas](poc-1-workspace-canvas.md) | Dashboard, workspace D&D 5e, BFF | ✅ | RPG-47–55 |
| **2** | [PoC 2 — DPA Agent](poc-2-dpa-agent.md) | Upload, análise, publish (stub LLM) | ✅ | RPG-56–63 |
| **2.9** | (evals) | Evals smoke + LangSmith | ❌ → Fase 1 | RPG-64 |
| **3** | [PoC 3 — Sessão real](poc-3-sessao-real.md) | RBAC, dashboard GM, revisões | ✅ | RPG-65–72 |
| **4** | [PoC 4 — Extensão de template](poc-4-extensao-template.md) | Evoluir ficha sem reupload | ✅ | RPG-73–78 |

### Transversal

| Página | Foco | Status |
|--------|------|--------|
| [Organização Apps](organizacao-apps.md) | `apps/backend`, `apps/frontend` | ✅ |

---

## Runtime entregue

| Camada | Path |
|--------|------|
| API BFF | `apps/backend/app/` |
| UI | `apps/frontend/src/` |
| Specs DSL | `specs/` |
| Testes | `tests/` (18 pytest) |
| Dev | `make dev` ou `./dev.sh` |

Legado `backend/` e `apps/web/` — apenas READMEs de redirecionamento.

---

## Demonstração do PoC (fluxo completo)

```mermaid
flowchart LR
    A[Dashboard] --> B[Criar workspace]
    B --> C[Upload / fixture D&D 5e]
    C --> D[DPA analisa draft]
    D --> E[GM publica template]
    E --> F[Jogador edita ficha]
    F --> G[GM vê dashboard]
    G --> H[GM estende template]
```

1. `./dev.sh` — app `:5173`, API `:8000`
2. Abrir workspace D&D 5e de exemplo ou criar novo
3. SessionBar: alternar **Mestre** / **Lyra** / **Thorin**
4. GM publica template; jogador edita; GM estende campos

---

## Rastreabilidade

| Artefato | Local |
|----------|-------|
| Roadmap pós-PoC | [docs/05-roadmap.md](../05-roadmap.md) |
| Status SDLC | [docs/status/pendencias-sdlc.md](../status/pendencias-sdlc.md) |
| Resumo operacional | [status-resumo.md](status-resumo.md) |
| Pendências humanas | [docs/status/pendencias-humanas.md](../status/pendencias-humanas.md) |
| Specs DSL | `specs/` |

---

## Próximo passo (pós-PoC)

Ver [Fase 1 — Hardening](../05-roadmap.md#fase-1--hardening-46-semanas):

1. Evals smoke LangSmith (RPG-64)
2. Alinhar `specs/api/bff_v1.py` com routers
3. Integrar LLM real no DPA Agent
4. CI obrigatório sem `continue-on-error`
