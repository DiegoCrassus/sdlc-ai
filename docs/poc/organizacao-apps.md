# Organização — pasta `apps/`

**Status:** ✅ Concluído (marco P1.1 do PoC 1)

**Objetivo:** consolidar runtimes num layout previsível e eliminar duplicação entre caminhos legados e alvo.

## Problema (antes do PoC)

```text
apps/
├── backend/          # placeholder
├── frontend/         # README apenas
└── web/              # React + Vite (código real)

backend/              # FastAPI — FORA de apps/
```

## Layout entregue

```text
apps/
├── backend/          # FastAPI — BFF + domínio
│   ├── app/
│   ├── requirements.txt
│   └── scripts/smoke_test.py
└── frontend/         # React + Vite
    ├── src/
    └── package.json
```

## Marcos entregues

| # | Marco | Status |
|---|-------|--------|
| A.1 | Migrar backend | ✅ `apps/backend/` |
| A.2 | Migrar frontend | ✅ `apps/frontend/` |
| A.3 | Atualizar CI/Makefile | ✅ shell `.sh` |
| A.4 | Atualizar docs | ✅ |
| A.5 | Proxy Vite `/v1` | ✅ |
| A.6 | Legado | ✅ READMEs redirecionamento |
| A.7 | Smoke test | ✅ 18 pytest |

## Critério de saída

✅ Um único caminho sob `apps/`; `make dev` / `./dev.sh` funcionam.

## Links

- [apps/README.md](../../apps/README.md)
- [infrastructure/project-architecture.md](../infrastructure/project-architecture.md)
- [poc-1-workspace-canvas.md](poc-1-workspace-canvas.md)
