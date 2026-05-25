# RPG-OP Backend

FastAPI BFF for workspaces, sheet provisioning and invites.

## Run

```bash
cd apps/backend
../.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

Or from repo root: `make dev-backend`

## API (PoC 1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/workspaces` | List workspaces (example first) |
| POST | `/v1/workspaces` | Create workspace + auto-provision schema |
| GET | `/v1/workspaces/{id}` | Workspace detail |
| GET | `/v1/workspaces/{id}/example-sheet` | Canvas payload |
| POST | `/v1/workspaces/{id}/invites` | Invite member |

Create accepts `sheet_source`: `file` | `json` | `text`.

Data: `apps/backend/data/rpg_op.db` (SQLite dev).
