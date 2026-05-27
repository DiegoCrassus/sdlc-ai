# Investment Radar — Local Runbook

> **Product:** financial monitoring demo (stocks + crypto) — **not a trading platform**.  
> **Plane epic:** [INVES-19](https://app.plane.so/investments-sdlc/browse/INVES-19/)  
> **API contract:** [investment-radar-api.md](../architecture/investment-radar-api.md)

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend API |
| Node.js | 18+ | Frontend dev server |
| Git | any | Clone repository |

Optional API keys improve live market data (see [Environment variables](#environment-variables)).

## Clone and install

```bash
git clone https://github.com/DiegoCrassus/sdlc-ai.git
cd sdlc-ai

# Backend dependencies
python3 -m pip install -e ".[dev]" --break-system-packages

# Frontend dependencies
cd app/frontend && npm install && cd ../..
```

Copy `.env.example` to `.env` at the repository root if you need custom settings. **Never commit `.env`.**

## Run locally

Use **two terminals**.

### Terminal 1 — Backend (port 8000)

From repository root:

```bash
uvicorn app.backend.main:app --reload --port 8000
```

Verify:

- Health: http://localhost:8000/api/v1/health  
- OpenAPI: http://localhost:8000/docs  

### Terminal 2 — Frontend (port 5173)

```bash
cd app/frontend
cp .env.example .env   # optional
npm run dev
```

Open **http://localhost:5173**.

## Environment variables

### Backend (`.env` at repo root)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | no | `sqlite+aiosqlite:///./data/investment_radar.db` | SQLite path for watchlist + portfolio |
| `CORS_ORIGINS` | no | `http://localhost:5173,...` | Allowed frontend origins |
| `ENABLE_LIVE_MARKET_DATA` | no | `true` | Set `false` to force fallback catalog only |
| `FINNHUB_API_KEY` | no | — | Stock quotes/search (primary live provider) |
| `ALPHA_VANTAGE_API_KEY` | no | — | Secondary stock provider |
| `MARKET_REQUEST_TIMEOUT` | no | `8.0` | HTTP timeout for providers (seconds) |

CoinGecko crypto endpoints use the public API (no key required for MVP).

### Frontend (`app/frontend/.env`)

| Variable | Required | Default |
|----------|----------|---------|
| `VITE_API_BASE_URL` | no | `http://localhost:8000/api/v1` |

## Live vs fallback data

Responses include `source: "live"` or `source: "fallback"` on quotes and history.

| Mode | When | Demo tip |
|------|------|----------|
| **Live** | Provider reachable and keys configured (stocks) / CoinGecko up (crypto) | Use symbols like `BTC`, `AAPL` |
| **Fallback** | Missing keys, rate limits, or network errors | Set `ENABLE_LIVE_MARKET_DATA=false` for offline demo |

Fallback catalog includes representative symbols (e.g. `AAPL`, `MSFT`, `BTC`, `ETH`) with plausible static prices.

## Feature walkthrough

1. **Discover** (`/`) — search assets, add to watchlist  
2. **Watchlist** (`/watchlist`) — monitor prices with source badges  
3. **Asset detail** (`/assets/stock:AAPL`) — quote + price history chart  
4. **Portfolio** (`/portfolio`) — simulated cash (seed **$100,000 USD**), buy/sell at current quote  

> Simulated portfolio only. No brokerages, payments, or real money movement.

## Tests

```bash
# Backend (from repo root)
python3 -m pytest app/backend/tests/ -v

# SDLC structure
make sdlc-doctor

# Frontend production build
cd app/frontend && npm run build
```

## Architecture overview

```
Browser (React SPA :5173)
        │  REST /api/v1
        ▼
FastAPI backend (:8000)
        ├── market_data → Finnhub / Alpha Vantage / CoinGecko + fallback
        ├── watchlist   → SQLite
        └── portfolio   → SQLite (simulated)
```

See also:

- [Architecture overview](../architecture/overview.md)  
- [System context](../architecture/system-context.md)  
- [ADRs](../architecture/decisions.md) (ADR-004..008)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Frontend CORS errors | Confirm backend `CORS_ORIGINS` includes `http://localhost:5173` |
| All quotes show `fallback` | Expected without API keys; or set `ENABLE_LIVE_MARKET_DATA=false` |
| Empty portfolio | Call `GET /api/v1/portfolio` once to seed default portfolio |
| `ModuleNotFoundError: app` | Run uvicorn from **repository root**, not `app/backend/` |
| SQLite locked | Single writer; stop duplicate backend processes |

## Continuing development

Work follows the SDLC cycle: Plane card `INVES-N` → `feature/INVES-N-*` branch → PR → merge `develop`.

Sub-task mapping:

| Card | Scope |
|------|-------|
| INVES-20 | Market data API |
| INVES-21 | Watchlist |
| INVES-22 | Simulated portfolio |
| INVES-23 | Frontend SPA |
| INVES-24 | This runbook |
