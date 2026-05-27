# Current State — Handoff

> **Updated:** 2026-05-27  
> **Branch:** `develop` @ `287a8a0`

## What Works

- **SDLC operating system** — `.sdlc/`, `.cursor/`, Doctor DSL, observability tool
- **Market data layer** — composite providers (Finnhub, brapi, CoinGecko, BCB, Stooq CSV, mock)
- **FastAPI backend** — REST API at `/api/v1/market/*` with OpenAPI docs
- **22 tests passing** — unit + integration (mock mode)
- **Docker Compose** — backend + Redis

## Quick Start

```bash
make backend-test          # run tests
make backend-dev           # http://localhost:8000/docs
make backend-docker        # docker compose up
```

## API Keys Needed (free)

Register and add to `.env`:

| Key | Provider | URL |
|-----|----------|-----|
| `FINNHUB_API_KEY` | US stocks | https://finnhub.io |
| `COINGECKO_API_KEY` | Crypto | https://www.coingecko.com/en/api |
| `BRAPI_API_KEY` | B3 (optional) | https://brapi.dev/dashboard |

PETR4, VALE3, MGLU3, ITUB4 work on brapi without token.

## Next Steps

- [ ] Add frontend pages consuming market API
- [ ] Wire CI to run `make backend-test`
- [ ] Portfolio / watchlist domain models
- [ ] Auth layer

## Research

See [docs/market-data-sources.md](../market-data-sources.md) for provider decision matrix.
