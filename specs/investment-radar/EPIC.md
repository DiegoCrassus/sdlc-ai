# Epic: Investment Radar

> **Card:** INVESTIMENTS-0 (planning)  
> **GitHub:** planning branch `docs/INVESTIMENTS-0-plan-investment-radar`  
> **Stage:** Requirements → Architecture  
> **Updated:** 2026-05-27

## Story

People who follow stocks and cryptocurrencies need one place to understand what is happening with assets they care about — without trading, brokerages, or moving money. Today `app/backend` and `app/frontend` are empty placeholders. This epic delivers **Investment Radar**: discover assets, maintain a watchlist, view price history, simulate a portfolio, set price alerts, and see data provenance — with graceful degradation when live APIs fail.

## Scope

- FastAPI backend with SQLite persistence (watchlist, portfolio, alerts)
- Market data: CoinGecko (crypto), yfinance (stocks), deterministic fallback catalog
- React + Vite + TypeScript frontend
- Local run via Makefile; documentation for developers
- SDLC evidence per ticket under `specs/investment-radar/evidence/`

## Non-Goals

- Real trading, brokerage integration, or money movement
- User authentication / multi-tenant accounts
- Production deployment or Kubernetes
- Mobile native apps
- Paid market data APIs requiring keys

## Assumptions

| Assumption | Confidence | Impact if wrong |
|------------|------------|-----------------|
| Single local user (no auth) | high | Add auth layer later |
| CoinGecko + yfinance free tiers sufficient | medium | Rely more on fallback |
| React + Vite acceptable for frontend ADR | high | Rewrite UI |
| SQLite adequate for demo | high | Migrate to Postgres |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| External API rate limits | medium | Stale prices | Fallback catalog + source labels |
| yfinance instability | medium | Stock quotes fail | Fallback for known symbols |
| Scope creep into trading | low | Wrong product | Non-goals in every ticket |

## Ticket Breakdown

See [TICKETS.md](./TICKETS.md).

## Acceptance Criteria (epic)

1. `make radar-dev` starts backend and frontend locally.
2. User can search stocks/crypto, add to watchlist, view history chart.
3. User can add simulated portfolio positions and see gain/loss.
4. User can create above/below price alerts.
5. UI shows data source (live vs fallback) per asset.
6. App remains usable when live APIs are disabled.
7. Each delivery ticket has evidence file and commit on its feature branch.
