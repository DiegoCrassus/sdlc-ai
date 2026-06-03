# app/studio-frontend — Studio Service UI

React + Vite SPA for the **SDLC Studio control plane**: dashboard, workflow canvas (React Flow), builders, and live observability.

**Not MarketPulse.** Isolated from `app/frontend/` (`marketpulse-frontend`).

## Stack

- React 19 + TypeScript
- Vite 5
- React Router 7
- Tailwind CSS (align with MarketPulse styling patterns)
- React Flow (S2+ canvas)
- TanStack Query (recommended for `/studio` API)

## Architecture

Screen catalog, React Flow boundaries, and API contract:

[`docs/architecture/studio-service-platform.md`](../../docs/architecture/studio-service-platform.md)

## Target layout

```text
app/studio-frontend/
├── README.md
├── package.json              # name: studio-frontend
├── vite.config.ts            # port 5174; proxy /studio → :8100
└── src/
    ├── components/shell/     # TopBar, Sidebar (S1)
    ├── components/canvas/    # React Flow mapper (S2)
    ├── pages/                # Dashboard, Workflows, Observability, …
    └── api/client.ts
```

## Run (after INVES-79 scaffold)

```bash
cd app/studio-frontend && npm install && npm run dev
```

UI: http://127.0.0.1:5174  
API proxy: `/studio` → http://127.0.0.1:8100

Combined dev (root Makefile, INVES-78/79):

```bash
make studio-dev
```

## Routes (information architecture)

| Path | Screen | Phase |
|------|--------|-------|
| `/` | Dashboard | S1 |
| `/workflows` | Read-only canvas | S2 |
| `/builder` | Workflow builder (propose-only) | S4 |
| `/observability` | Live timeline + SSE | S3 |
| `/agents`, `/rules`, `/registry`, … | Builders & explorers | S4–S5 |

## React Flow boundaries

- **API owns semantics** — nodes, edges, overlays from `GET /studio/engine/canvas`.
- **UI owns layout** — `position`, zoom, pan, filters; stored locally only (non-authoritative).
- **No silent writes** — builder exports via `POST /studio/proposals`; apply happens in git/Plane workflow outside Studio.

See §6 in the architecture doc for the `mapViewModel.ts` contract.

## Boundaries

| Owns | Must not |
|------|----------|
| Layout, routing, canvas rendering, forms | Execute shell/git/merge |
| SSE client for observability | Embed Cursor chat |
| Patch preview display | Persist workflow IR as repo truth |

## Related

- API: [`app/studio-backend/README.md`](../studio-backend/README.md)
- Engine contracts: [`studio/visual-orchestration-prototype.md`](../../studio/visual-orchestration-prototype.md)
- Roadmap: [`docs/roadmap/sdlc-studio-service-roadmap.md`](../../docs/roadmap/sdlc-studio-service-roadmap.md)
