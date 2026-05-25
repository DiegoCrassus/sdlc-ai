# Apps

Application runtimes belong under `apps/`.

Target layout:

```text
apps/
├── backend/
└── frontend/
```

Current transition:

- `backend/` still contains the FastAPI application.
- `apps/web/` still contains the React + Vite application.

Do not treat those legacy paths as the final architecture. A dedicated migration task should move them to `apps/backend/` and `apps/frontend/` with CI, docs, commands, and Cursor rules updated in the same PR.
