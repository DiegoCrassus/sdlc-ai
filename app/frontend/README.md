# Investment Radar — Frontend

React 18 + Vite 5 + TypeScript SPA for the Investment Radar local demo (ADR-005, INVES-23).

## Prerequisites

- Node.js 18+
- Backend API running on port **8000** (see below)

## Quick start

```bash
cd app/frontend
cp .env.example .env   # optional; defaults to http://localhost:8000/api/v1
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server is allowed in backend `CORS_ORIGINS`.

### Backend (separate terminal)

From the repository root:

```bash
uvicorn app.backend.main:app --reload --port 8000
```

## Scripts

| Script    | Description                          |
|-----------|--------------------------------------|
| `npm run dev`     | Vite dev server (port 5173)   |
| `npm run build`   | Typecheck + production build  |
| `npm run preview` | Serve `dist/` locally         |

## Environment

| Variable              | Default                              |
|-----------------------|--------------------------------------|
| `VITE_API_BASE_URL`   | `http://localhost:8000/api/v1`       |

## Routes

| Path                 | Page                                      |
|----------------------|-------------------------------------------|
| `/`                  | Discover — search assets, add watchlist   |
| `/watchlist`         | Watchlist with quotes and source badges   |
| `/assets/:assetId`   | Asset detail, quote, history chart/table  |
| `/portfolio`         | Cash, holdings, buy/sell, transactions    |

Asset IDs in URLs are URL-encoded (e.g. `stock%3AAAPL` for `stock:AAPL`).

## Manual test checklist

1. Start backend and frontend; confirm Discover loads without console errors.
2. Search `apple` or `BTC` — results show with **live** or **fallback** badge when applicable.
3. Add an asset to watchlist from Discover; open **Watchlist** and confirm price + badge.
4. Open asset detail — quote, line chart, and OHLCV table render.
5. **Portfolio** — note cash balance; buy `stock:AAPL` qty `1`; holdings and transactions update.
6. Sell partial quantity; confirm cash increases and holding quantity decreases.
7. Stop backend — pages show error states instead of hanging.

## Structure

```
src/
├── api/          # client.ts, types.ts
├── components/   # Layout, SourceBadge, AsyncState
├── pages/        # Discover, Watchlist, AssetDetail, Portfolio
└── utils/        # formatting helpers
```

## Status

**Implemented** (INVES-23). Production deploy and full local runbook: INVES-24 (not in scope here).

## What does NOT belong here

- Backend business logic — `app/backend/`
- Auth — deferred (ADR-008)
- Local task tickets — Plane MCP only
