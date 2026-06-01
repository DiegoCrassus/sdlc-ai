# app/backend — MarketPulse API

Python FastAPI service for the **MarketPulse** financial and crypto dashboard.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2 + pydantic-settings
- SQLAlchemy 2.0 async + aiosqlite (price alerts)
- Provider pattern: `mock` (default) | `twelve_data` (stub)

## Setup

From the repository root:

```bash
pip install -e ".[dev]"
```

Optional: create `.env` in the repo root:

```bash
MARKET_DATA_PROVIDER=mock
TWELVE_DATA_API_KEY=
```

## Run API

```bash
uvicorn marketpulse.main:app --reload --host 127.0.0.1 --port 8000
```

OpenAPI docs: http://127.0.0.1:8000/docs

## Tests

```bash
python -m pytest app/backend/tests/ -v
```

## API (v1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health + active provider |
| GET | `/api/v1/markets/overview` | Market overview cards |
| GET | `/api/v1/markets/quotes?symbols=AAPL,BTC` | Batch quotes |
| GET | `/api/v1/markets/{symbol}/ohlcv` | OHLCV series |
| GET | `/api/v1/markets/search?q=bit` | Symbol search |
| GET | `/api/v1/projections/{symbol}` | Linear trend projection |
| GET | `/api/v1/watchlist` | Default watchlist |
| POST | `/api/v1/alerts` | Create price alert (watchlist symbol) |
| GET | `/api/v1/alerts` | List alerts (evaluates pending triggers) |
| DELETE | `/api/v1/alerts/{alert_id}` | Delete alert |

## Layout

```
app/backend/src/marketpulse/
  main.py
  config.py
  deps.py
  api/v1/routes/
  domain/
  providers/
  services/
app/backend/tests/
```

See also: [`docs/architecture/marketpulse-api-providers.md`](../../docs/architecture/marketpulse-api-providers.md)
