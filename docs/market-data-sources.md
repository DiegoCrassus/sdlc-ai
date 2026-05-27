# Market Data Sources — Research & Provider Strategy

> **Status:** Deep research completed before provider implementation.  
> **Last updated:** 2026-05-27 (v2 — Finnhub + brapi as free primaries)

---

## Executive Summary

| Asset class | Primary source | Fallback | Mock |
|-------------|----------------|----------|------|
| **Crypto** | CoinGecko Demo API | CoinGecko keyless (low volume) | `MockMarketDataProvider` |
| **US stocks / ETFs** | **Finnhub** (free, 60 req/min) | Stooq CSV → Twelve Data (optional) | Mock |
| **Indexes** | **Finnhub** (`^GSPC`, `^NDX`, `^DJI`) | Stooq CSV | Mock |
| **FX / BRL** | Banco Central (PTAX/SGS) — open data | — | Mock |
| **Brazilian equities** | **brapi.dev** (free, 15k req/mo) | Stooq CSV | Mock |
| **Company metadata** | Finnhub `/profile2` · brapi `summaryProfile` | Twelve Data (optional) | Mock |
| **Search** | Finnhub `/search` + CoinGecko + brapi | Cached composite | Mock |

**Twelve Data demoted to optional fallback** — free tier forbids displaying data to end users.

**Scraping is never the default.** It is a controlled, last-resort adapter that may break without notice.

---

## Decision Matrix (10 Research Questions)

| # | Question | Answer |
|---|----------|--------|
| 1 | **Crypto sources?** | **CoinGecko Demo API** — official REST, 10k calls/month, 100 req/min, OHLCV, 17k+ coins, no credit card. Keyless public API only for dev smoke tests (5–15 req/min, IP throttled). |
| 2 | **Stock sources?** | **Finnhub (free)** — 60 req/min, real-time US quotes, OHLC candles, company profile, search. Personal use allowed for display. Twelve Data demoted (free tier = internal non-display only). |
| 3 | **Safe for scraping?** | **Stooq** public CSV download URLs (undocumented but widely used for personal/research; strict daily hit limits). **Banco Central** — official OData/JSON APIs (not scraping). |
| 4 | **Do NOT scrape?** | **Investing.com** (ToS explicitly forbids scraping/data mining). **MarketWatch** (Dow Jones ToS; automated extraction prohibited). **Yahoo Finance** as scraping target (no official API; personal use only; high block risk). **Nasdaq** undocumented JSON endpoints (no license; fragile). |
| 5 | **APIs requiring keys?** | Finnhub, CoinGecko Demo, brapi (optional — test tickers without key), Twelve Data (optional fallback). Env: `FINNHUB_API_KEY`, `COINGECKO_API_KEY`, `BRAPI_API_KEY`. |
| 6 | **No-key sources?** | BCB PTAX/SGS (official), Stooq CSV, brapi test tickers (PETR4, VALE3, MGLU3, ITUB4), CoinGecko keyless (limited), Mock. |
| 7 | **Historical data?** | Finnhub candles (US), brapi OHLC (B3), Stooq CSV (20+ years), CoinGecko market_chart, BCB SGS (FX). |
| 8 | **Rate limits?** | See comparison table below. Application enforces stricter client-side limits + Redis cache. |
| 9 | **Fallback order?** | Cache → API (Finnhub / brapi / CoinGecko / BCB) → CSV (Stooq) → Scraping → Mock |
| 10 | **Scraping risks?** | Layout changes break parsers; IP blocks; ToS breach (Investing/MarketWatch); no SLA; delayed/stale data; legal exposure if used commercially without license. Treat as **optional adapter**. |

---

## Source Comparison

### Official APIs

| Source | Coverage | Free tier | Auth | Rate limits | Freshness | History | ToS / notes | Integration |
|--------|----------|-----------|------|-------------|-----------|---------|-------------|-------------|
| **Finnhub Free** | US stocks, ETFs, forex, crypto, indexes | Free | Free API key | 60 req/min | Real-time US | 30+ years OHLC | Personal use; generous free tier | Official REST JSON |
| **brapi.dev Free** | B3 equities, FIIs, crypto | 15k req/mo | Optional token | Fair use | ~30 min delay | 3 months (free) | 4 test tickers without token | Official REST JSON |
| **CoinGecko Demo** | 17k+ coins, DEX, indexes | 10k calls/mo | Free API key | 100 req/min | ~1–5 min delay | 1y daily/hourly OHLC | No resale/redistribution | Official REST JSON |
| **Twelve Data Basic** | US/global | 800 credits/day | Free API key | 8/min; 800/day | Real-time US | Time series | **Internal non-display only on free tier** — optional fallback | Official REST JSON |
| **Alpha Vantage** | 200k+ tickers, indicators | 25 req/**day** | Free API key | 5/min, 25/day | 15min delayed (premium for realtime) | 100 points/request (free) | Personal/educational; Nasdaq-licensed US data | Official REST JSON/CSV |
| **Banco Central (BCB)** | PTAX FX, SGS macro series | Unlimited (fair use) | None | ~5 req/s recommended | Daily PTAX | Decades (SGS) | Open Data (ODbL) | OData + JSON REST |
| **B3 for Developers** | Official B3 market data | None public | Institutional contract | N/A | Real-time | Full | Commercial only | FIX/ITCH/REST (paid) |

### Downloadable CSV / Structured Files

| Source | Coverage | Free tier | Auth | Rate limits | Freshness | History | ToS / notes | Integration |
|--------|----------|-----------|------|-------------|-----------|---------|-------------|-------------|
| **Stooq CSV** | Global stocks, ETFs, forex, crypto, indices | Free download | None | Undocumented daily hit limit; "Exceeded daily hits" error | End-of-day | 20+ years daily | No formal API; CSV via `stooq.com/q/d/l/?s=SYMBOL&i=d` | HTTP CSV download |
| **BCB SGS export** | Macro/FX series | Free | None | Fair use | Daily/monthly | 10+ years | Open government data | JSON/CSV via API |

### Public Pages (Scraping Assessment)

| Source | Official API | Scraping allowed? | robots.txt | Risk | Verdict |
|--------|--------------|-------------------|------------|------|---------|
| **Yahoo Finance** | No (shut down 2017) | Personal use only; blocks automation | Restrictive | High — breaks often | **Reject as scrape target**; use via unofficial libs only in dev |
| **Nasdaq.com** | Paid (Nasdaq Data Link) | Undocumented JSON endpoints exist; no license | Mixed | Medium — endpoint changes | **Reject** — use Twelve Data instead |
| **Investing.com** | No free API | **Explicitly forbidden** in ToS | Cloudflare | High legal + technical | **Reject — do not scrape** |
| **MarketWatch** | No | Dow Jones ToS prohibits automated extraction | Restrictive | High legal | **Reject — do not scrape** |
| **Stooq pages** | CSV download preferred | Gray area; prefer CSV URL | Permissive for CSV path | Medium — layout/hit limits | **Fallback only** with strict rate limits |

---

## Recommended Primary Sources

### Stocks & ETFs (US)

**Primary: Finnhub API** (free, no credit card)

- Endpoints: `/quote`, `/stock/candle`, `/search`, `/stock/profile2`
- 60 API calls/minute; real-time US quotes
- Register at [finnhub.io](https://finnhub.io/) → `FINNHUB_API_KEY`

**Fallback: Stooq CSV** → optional Twelve Data if key configured

**Rejected as primary:**

- **Twelve Data free** — cannot display data to end users
- **Alpha Vantage** — 25 requests/day
- **yfinance** (open source) — wraps unofficial Yahoo endpoints; treated as scraping risk, not integrated as API provider

### Brazilian equities (B3)

**Primary: brapi.dev** (free tier R$ 0)

- Endpoint: `GET /api/quote/{ticker}`
- 15,000 requests/month; PETR4, MGLU3, VALE3, ITUB4 work **without token**
- Full coverage requires `BRAPI_API_KEY` from [brapi.dev/dashboard](https://brapi.dev/dashboard)

**Fallback: Stooq CSV** (`petr4.sa`)

### Crypto

**Primary: CoinGecko Demo API**

- Base: `https://api.coingecko.com/api/v3`
- Header: `x-cg-demo-api-key: {key}`
- Endpoints: `/simple/price`, `/coins/{id}/market_chart`, `/search`, `/coins/{id}`
- 10,000 calls/month, 100 req/min

**Fallback: CoinGecko keyless** — development and emergency only (5–15 req/min)

### Exchange rates (especially BRL)

**Primary: Banco Central do Brasil**

- PTAX OData: `https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/`
- SGS series: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json`
- No authentication; open data license

### Market indexes

**Primary: Finnhub** — symbols `^GSPC`, `^NDX`, `^DJI`  
**Fallback: Stooq CSV** — e.g. `^spx`

### Company metadata

**Primary:** Finnhub `/stock/profile2` (US) · brapi `summaryProfile` module (B3)  
**Fallback:** Twelve Data `/profile` (optional)

### Asset search / symbol lookup

**Primary:** Finnhub `/search` (US) + CoinGecko `/search` (crypto) + brapi (B3 tickers)  
**Fallback:** Cached prior search results (1–6 h TTL)

---

## Recommended Fallback Source

**Stooq CSV** for historical OHLC when API quotas are exhausted.

- Structured, parseable, no HTML fragility
- Lower confidence than official API (`confidenceLevel: medium`)
- Must respect daily hit limits (app limit: **30 CSV downloads/day**)

**Scraping provider** only if CSV URL fails — parse Stooq symbol page HTML with saved fixtures and 30-minute minimum cache.

---

## Recommended Mock Data Strategy

`MockMarketDataProvider` is always available as the final fallback in `CompositeMarketDataProvider`.

Use cases:

1. **Local development** without API keys (`MARKET_DATA_MODE=mock`)
2. **CI/tests** — deterministic prices, no network
3. **UI development** — frontend can render asset detail with provenance badge
4. **Outage** — when all external sources fail, return mock with `confidenceLevel: low` and `warning: "Simulated data — external sources unavailable"`

Mock data includes realistic OHLC shapes, metadata, and search results for a fixed symbol set (`AAPL`, `BTC`, `PETR4.SA`, `USD/BRL`).

---

## Sources Rejected (and Why)

| Source | Reason |
|--------|--------|
| **Investing.com** | ToS §10 explicitly forbids scraping, data mining, and automated extraction |
| **MarketWatch** | Dow Jones terms prohibit automated data collection; no free API |
| **Yahoo Finance (scraping)** | No official API since 2017; blocks/rate-limits; personal use only |
| **Nasdaq undocumented JSON** | No license; endpoints change; commercial use requires Nasdaq Data Link contract |
| **Twelve Data (primary)** | Free tier forbids end-user display; demoted to optional fallback |
| **Alpha Vantage (primary)** | 25 req/day too restrictive |
| **yfinance / Yahoo** | Open source but unofficial scraping; not used as API adapter |
| **brapi / bolsai (third-party BR)** | brapi now primary; bolsai deferred |

---

## Risks Related to Scraping

1. **Technical fragility** — HTML/DOM changes break parsers overnight
2. **IP blocking** — repeated requests trigger 403/429 or CAPTCHA (never bypass)
3. **Legal / ToS** — Investing.com, MarketWatch, Yahoo explicitly restrict automation
4. **Data quality** — delayed quotes, missing fields, wrong symbol mapping
5. **No SLA** — no support channel when source changes
6. **Operational cost** — maintenance of fixtures, parsers, and incident response
7. **Compliance** — redistributing scraped data to end users may violate exchange licensing

**Mitigation:** Scraping adapter is optional, rate-limited, cached ≥30 min, logs failures, marks `confidenceLevel: low`, stores `sourceUrl` + `fetchedAt`.

---

## Rate-Limit Strategy

### Application-level limits (stricter than provider defaults)

| Provider | App limit | Notes |
|----------|-----------|-------|
| Finnhub | 50 req/min (below 60 cap) | Token bucket |
| brapi | 500 req/day budget | Free tier 15k/mo |
| CoinGecko Demo | 60 req/min (below 100 cap) | Token bucket per key |
| Twelve Data (optional) | 6 credits/min, 400/day budget | Only if key configured |
| BCB | 3 req/s | Sequential with jitter |
| Stooq CSV | 2 req/min, 30/day | Global mutex |
| Scraping | 1 req/30s per domain | Hard ceiling |

### On 429 / quota exceeded

1. Log to `provider_requests` with `status=rate_limited`
2. Serve stale cache if available (extend TTL up to 2×)
3. Fall back to next provider in composite chain
4. Never retry aggressively (exponential backoff: 1s, 2s, 4s, max 3 attempts)

---

## Cache Strategy (Redis)

| Data type | TTL | Key pattern |
|-----------|-----|-------------|
| Current crypto price | 60 s (30–120 s range) | `md:crypto:price:{symbol}` |
| Current stock price | 600 s (5–15 min) | `md:stock:price:{symbol}` |
| Historical OHLC | 43200 s (12 h, up to 24 h) | `md:hist:{assetType}:{symbol}:{range}:{interval}` |
| Asset metadata | 86400 s (24 h) | `md:meta:{assetType}:{symbol}` |
| Search results | 7200 s (2 h, up to 6 h) | `md:search:{assetType}:{query_hash}` |
| Scraped pages | 1800 s minimum (30 min) | `md:scrape:{domain}:{path_hash}` |
| BCB PTAX | 3600 s | `md:fx:ptax:{date}` |

Cache entries store full response + `cachedAt` timestamp. Composite provider checks cache before any external call.

---

## Legal / Terms-of-Use Notes

- **Finnhub:** Free tier for personal use; commercial apps may need paid plan
- **brapi.dev:** Free tier for personal/academic; attribution appreciated
- **CoinGecko:** Free tier for prototyping; commercial apps need paid plan
- **Twelve Data Basic:** Internal non-display only — use only as optional fallback
- **Alpha Vantage:** Personal/non-commercial on free tier; US market data is Nasdaq-licensed
- **BCB Open Data:** ODbL license; attribution appreciated; suitable for FX display
- **Stooq:** No explicit API license; treat as research/personal; do not hammer servers
- **Scraping generally:** Prefer official APIs; document `sourceUrl`; never bypass CAPTCHA or paywalls

> **Action item for production:** Register free API keys (Finnhub + CoinGecko + brapi). Review Finnhub/brapi commercial terms before public launch; upgrade to paid tiers if usage exceeds free limits.

---

## Final Provider Priority Order

```
CompositeMarketDataProvider.resolve(request):
  1. Redis cache (sourceType: cache)
  2. ApiMarketDataProvider
       a. CoinGecko (crypto)
       b. Finnhub (US stocks, ETFs, indexes)
       c. brapi.dev (B3 equities)
       d. BCB OData (BRL FX / PTAX)
       e. Twelve Data (optional fallback if TWELVE_DATA_API_KEY set)
  3. CsvMarketDataProvider (Stooq)
  4. ScrapingMarketDataProvider (Stooq pages — disabled by default)
  5. MockMarketDataProvider (always succeeds; confidenceLevel: low)
```

Environment flags:

- `MARKET_DATA_MODE=live|mock`
- `MARKET_DATA_SCRAPING_ENABLED=false`
- `REDIS_URL=redis://localhost:6379/0`
- **`FINNHUB_API_KEY`** — primary US stocks (free at finnhub.io)
- **`COINGECKO_API_KEY`** — crypto (free Demo at coingecko.com)
- **`BRAPI_API_KEY`** — optional; PETR4/VALE3/MGLU3/ITUB4 work without key
- `TWELVE_DATA_API_KEY` — optional fallback only

---

## References

- [Finnhub API](https://finnhub.io/docs/api)
- [brapi.dev docs](https://brapi.dev/docs/acoes)
- [CoinGecko API Pricing](https://www.coingecko.com/en/api/pricing)
- [CoinGecko Keyless Public API](https://docs.coingecko.com/docs/keyless-public-api)
- [Twelve Data Pricing & Credits](https://twelvedata.com/pricing)
- [Alpha Vantage Premium](https://www.alphavantage.co/premium/)
- [BCB PTAX OData](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/)
- [BCB SGS API](https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json)
- [Stooq data overview](https://www.quantstart.com/articles/an-introduction-to-stooq-pricing-data/)
- [Investing.com Terms (scraping prohibition)](https://cdn.investing.com/about-us/terms_and_conditions.pdf)
- [yfinance README — Yahoo ToS notice](https://github.com/ranaroussi/yfinance)
