# Pendências humanas — ações que requerem sua intervenção

**Última atualização:** 2026-05-25

## Já concluído

| Item | Evidência |
|------|-----------|
| `apps/backend` + `apps/frontend` | PoC 0–4 |
| venv + deps | `make setup`, `./dev.sh` |
| Testes | `make test` → 18 passed |
| Toolchain shell | `.sdlc/scripts/*.sh` |

## 1. Cursor + MCP

```bash
./launch.sh
```

No chat: *"Liste issues via GitHub MCP"*

## 2. LangSmith

Confirme `LANGSMITH_*` no `.env`, instale hooks deps, abra Cursor via `./launch.sh`.

## 3. Evals smoke (RPG-64)

Único item PoC 2.9 pendente — migrado para **Fase 1 Hardening** ([roadmap](../05-roadmap.md)).

## 4. Git commit/push

Quando satisfeito com o estado local.

## 5. Rodar o produto

```bash
chmod +x dev.sh launch.sh .sdlc/scripts/*.sh
make setup
./dev.sh
```

SessionBar: **Mestre** ou **Lyra/Thorin** no workspace D&D 5e.

## 6. Plane — wiki + Fase 1

API Plane bloqueada por Cloudflare neste ambiente (403). Executar localmente:

```bash
source .sdlc/scripts/_load-env.sh
make plane-create-phase1    # work items F1.1–F1.5
make plane-sync-roadmap
make plane-sync-poc
```

Alternativa: criar tarefas via Plane MCP no Cursor após `./launch.sh`.

## Comandos

| Comando | Uso |
|---------|-----|
| `./dev.sh` | Backend + frontend |
| `make test` | pytest |
| `./launch.sh` | Cursor + .env |
| `make validate` | Gate SDLC |
| `make plane-create-phase1` | Tarefas Fase 1 no Plane |
