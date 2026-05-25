# PoC 3 — Sessão real (mesa piloto local)

**Status:** ✅ Concluído  
**Objetivo:** mestre e jogador usam o produto numa sessão local sem intervenção técnica.

## Contexto

Com workspace e template publicados (PoC 1–2), fechar permissões, indicadores e UX para **piloto em localhost**.

## Marcos entregues

| # | Marco | Entregável |
|---|-------|------------|
| P3.1 | RBAC | `role_overrides` no canvas; SessionBar GM/jogador |
| P3.2 | Fluxo jogador | Editar ficha própria + validação schema |
| P3.3 | Dashboard mestre | Lista personagens, links canvas |
| P3.4 | Indicadores | Template version, último update, incompletos |
| P3.5 | Histórico básico | `sheet_revisions` |
| P3.6 | Layout responsivo | Notebook/tablet (base) |
| P3.7 | Estados UX | Loading/erro upload, publish, save |
| P3.8 | Testes | `tests/test_sheet_mvp3.py` |

## Critério de saída

✅ SessionBar alterna papéis; jogador edita; GM vê todas as fichas; 18 testes passam.

## Código

| Área | Path |
|------|------|
| Characters | `apps/backend/app/routers/characters.py` |
| Sheets | `apps/backend/app/routers/sheets.py` |
| UI GM | `apps/frontend/src/pages/WorkspacePage.tsx` |
| SessionBar | `apps/frontend/src/components/SessionBar.tsx` |

## Links

- [product/arquitetura-produto.md](../product/arquitetura-produto.md)
- [05-roadmap.md](../05-roadmap.md) — Fase 2 (convites reais)
