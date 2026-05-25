# Stack e infraestrutura

Stack **actual** (PoC) vs **alvo** (Fases 2–3). Decisões técnicas de monorepo: [project-architecture.md](project-architecture.md).

## Stack actual (PoC — localhost)

| Camada | Tecnologia | Notas |
|--------|------------|-------|
| Backend | Python 3.12 + FastAPI | `apps/backend/` |
| Frontend | React 18 + Vite + TypeScript | `apps/frontend/` |
| DB dev | SQLite | `apps/backend/data/rpg_op.db` |
| Agent (PoC) | Stub Python | LLM → Fase 1.3 |
| DSL | `packages/rpg_dsl` | `rpg validate` / compile |
| Dev toolchain | bash + `uv` + `make` | `.sdlc/scripts/*.sh` |
| Observabilidade dev | LangSmith (hooks Cursor) | `.cursor/hooks/` |

## Stack alvo (Fase 2 — Alpha)

| Camada | Tecnologia | Motivo |
|--------|------------|--------|
| Banco | PostgreSQL 16 | JSONB, ACID, revisões |
| Cache | Redis 7 | Sessão, rate limit, jobs |
| Object storage | Supabase Storage / S3 | PDFs e imagens de ficha |
| Auth | JWT ou Clerk/Auth0 | Substituir SessionBar mock |
| Deploy | Docker Compose → Railway/Fly | Staging HTTPS |
| CI | GitHub Actions | Gates required (Fase 1.4) |

## Ambientes

| Ambiente | Propósito | Fase |
|----------|-----------|------|
| `local` | PoC / dev | ✅ |
| `staging` | Piloto 2–3 mesas | Fase 2 |
| `production` | Beta+ | Fase 3 |

## Docker Compose (backlog)

Esboço para Fase 2 — ver `infra/docker-compose.yml` quando implementado:

```yaml
services:
  postgres:
    image: postgres:16-alpine
  redis:
    image: redis:7-alpine
  api:
    build: apps/backend
  web:
    build: apps/frontend
```

## LLM (produto)

| Uso | PoC | Fase 1+ |
|-----|-----|---------|
| DPA analyze | Stub determinístico | Multimodal + LangSmith trace |
| Dev orchestrator | Cursor + MCP | Deep Agent runtime (L3) |

Variável sugerida: `AGENT_MODEL` por ambiente.

## Links

- [project-architecture.md](project-architecture.md)
- [../05-roadmap.md](../05-roadmap.md)
- [../product/arquitetura-produto.md](../product/arquitetura-produto.md)
