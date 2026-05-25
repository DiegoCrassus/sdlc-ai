# Documentação — RPG-OP

Índice central. Cada pasta tem um papel único — **sem duplicar** conteúdo entre elas.

## Mapa

| Pasta | Conteúdo | Quando usar |
|-------|----------|-------------|
| **[05-roadmap.md](05-roadmap.md)** | Roadmap pós-PoC (Fases 1–4) | Planejar próximo trabalho |
| **[poc/](poc/00-indice-poc.md)** | Proof of Concept **concluído** | Ver o que já foi provado |
| **[product/](product/visao-e-escopo.md)** | Visão, arquitetura, Sheet Canvas | Contexto de produto |
| **[sdlc/](sdlc/ai-native.md)** | SDLC AI-native, DSL, harness | Engenharia e gates |
| **[status/](status/pendencias-sdlc.md)** | Pendências e maturidade | Validar L1→L2 |
| **[infrastructure/](infrastructure/project-architecture.md)** | Monorepo, stack, sync Plane | Onboarding técnico |

---

## Produto

| Documento | Descrição |
|-----------|-----------|
| [product/visao-e-escopo.md](product/visao-e-escopo.md) | Problema, objetivos, glossário |
| [product/arquitetura-produto.md](product/arquitetura-produto.md) | Camadas, BFF, domínio PoC |
| [product/sheet-canvas.md](product/sheet-canvas.md) | Canvas, DPA, fluxos GM/jogador |

---

## PoC (concluído)

| Documento | Descrição |
|-----------|-----------|
| [poc/00-indice-poc.md](poc/00-indice-poc.md) | **Índice PoC** — fases 0–4 |
| [poc/status-resumo.md](poc/status-resumo.md) | Resumo para Plane wiki |
| [poc/poc-0 … poc-4](poc/00-indice-poc.md#fases-do-poc-concluídas) | Detalhe por fase |
| [poc/organizacao-apps.md](poc/organizacao-apps.md) | Layout `apps/` |

---

## Roadmap e status

| Documento | Descrição |
|-----------|-----------|
| [05-roadmap.md](05-roadmap.md) | Fases 1–4 realistas |
| [status/pendencias-sdlc.md](status/pendencias-sdlc.md) | Gates técnicos |
| [status/pendencias-humanas.md](status/pendencias-humanas.md) | Ações manuais |

---

## SDLC e infra

| Documento | Descrição |
|-----------|-----------|
| [sdlc/ai-native.md](sdlc/ai-native.md) | DSL, compile, maturidade |
| [infrastructure/project-architecture.md](infrastructure/project-architecture.md) | Estrutura monorepo |
| [infrastructure/stack.md](infrastructure/stack.md) | Stack PoC vs alvo |

---

## Sincronizar Plane

```bash
source .sdlc/scripts/_load-env.sh
make plane-sync-roadmap
make plane-sync-poc
make plane-sync-infrastructure
```

---

## Linha do tempo

```text
PoC 0–4 ✅  →  Fase 1 Hardening  →  Fase 2 Alpha  →  Fase 3 Beta  →  Fase 4 Produto
```

Backlog Plane: projeto **RPG** · labels `phase-1`, `phase-2`, …
