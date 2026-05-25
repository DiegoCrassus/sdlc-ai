# Status PoC — resumo (sync Plane)

**Atualizado:** 2026-05-25 · **PoC:** concluído (fases 0–4) · **Maturidade SDLC:** L1 (meta L2)

## Fases PoC

| Fase | Status | Plane |
|------|--------|-------|
| 0 Fundação SDLC | ✅ Concluído | wiki |
| 1 Workspace/Canvas | ✅ Concluído | RPG-47–55 |
| 2 DPA Agent | ✅ Concluído (stub LLM) | RPG-56–63 |
| 2.9 Evals LangSmith | ❌ → Fase 1 | RPG-64 |
| 3 Sessão real | ✅ Concluído | RPG-65–72 |
| 4 Extensão template | ✅ Concluído | RPG-73–78 |

## Gates locais

- `rpg validate specs/` — OK (6 ficheiros)
- `make test` — 18 passed
- `make dev` / `./dev.sh` — backend :8000 + frontend :5173

## Pendências → Fase 1 (Hardening)

1. Evals smoke (RPG-64) — maturidade L2
2. LLM real no DPA Agent (substituir stub)
3. Revisar drift `specs/api/bff_v1.py` vs routers
4. Confirmar MCP GitHub via `./launch.sh`
5. Confirmar traces LangSmith no dashboard

## Docs completos

- [00-indice-poc.md](00-indice-poc.md)
- [docs/05-roadmap.md](../05-roadmap.md)
- [docs/status/pendencias-sdlc.md](../status/pendencias-sdlc.md)
