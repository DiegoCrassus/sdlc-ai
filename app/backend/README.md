# app/backend

## Purpose

Python backend service for the sdlc-ai project. Contains business logic, API layer, and data access.

## Status

**Not yet implemented.** This boundary is reserved for the Python service.

## What Belongs Here

- API endpoints (REST or GraphQL)
- Business logic and domain models
- Database models and migrations
- Background tasks and jobs
- Authentication and authorization logic
- Backend-specific configuration

## What Does NOT Belong Here

- UI rendering — goes in `app/frontend/`
- Infrastructure definitions — goes in `app/infra/`
- Shared types used by both frontend and backend — goes in `app/shared/`
- SDLC configuration — goes in `.sdlc/`

## Expected Future Structure

```
app/backend/
├── src/
│   ├── api/            ← API routes and handlers
│   ├── core/           ← Business logic and domain models
│   ├── db/             ← Database models, sessions, migrations
│   ├── services/       ← External service integrations
│   └── config.py       ← Configuration from env vars
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/         ← Database migration files (Alembic)
└── README.md           ← (this file, extended with setup instructions)
```

## Technology

- **Language:** Python 3.11+
- **Database:** SQLite (local), Supabase/PostgreSQL (production)
- **ORM:** TBD (likely SQLAlchemy with async)
- **Framework:** TBD (FastAPI is a likely candidate)
- **Tests:** pytest

## API Server

```bash
make backend-dev
# http://localhost:8000/docs
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/api/v1/market/search?q=` | Asset search |
| GET | `/api/v1/market/price/{symbol}?asset_type=` | Current price |
| GET | `/api/v1/market/history/{symbol}?asset_type=&range=&interval=` | OHLC history |
| GET | `/api/v1/market/metadata/{symbol}?asset_type=` | Company metadata |
| GET | `/api/v1/market/summary` | Market indexes summary |
| GET | `/api/v1/market/providers/health` | Provider chain health |

### Docker

```bash
make backend-docker
```

## Market Data Provider Layer

Implemented in `src/market_data/` — see [docs/market-data-sources.md](../../../docs/market-data-sources.md).

### Providers

| Provider | Class | Role |
|----------|-------|------|
| Composite | `CompositeMarketDataProvider` | Cache → API → CSV → Scraping → Mock |
| API | `ApiMarketDataProvider` | Finnhub, brapi, CoinGecko, BCB PTAX |
| CSV | `CsvMarketDataProvider` | Stooq downloadable CSV |
| Scraping | `ScrapingMarketDataProvider` | Stooq pages (disabled by default) |
| Mock | `MockMarketDataProvider` | Dev/CI/outage fallback |

### Environment

```bash
MARKET_DATA_MODE=live          # or mock
MARKET_DATA_SCRAPING_ENABLED=false
REDIS_URL=redis://localhost:6379/0
FINNHUB_API_KEY=...            # free at https://finnhub.io
COINGECKO_API_KEY=...          # free Demo at https://www.coingecko.com/en/api
BRAPI_API_KEY=...              # optional; PETR4/VALE3/MGLU3/ITUB4 work without key
TWELVE_DATA_API_KEY=...        # optional fallback only
```

### Usage

```python
from app.backend.src.market_data.factory import build_market_data_provider

provider = await build_market_data_provider()
price = await provider.get_current_price("AAPL", AssetType.STOCK)
```

### Tests

```bash
PYTHONPATH=. pytest app/backend/tests/ -v
```

