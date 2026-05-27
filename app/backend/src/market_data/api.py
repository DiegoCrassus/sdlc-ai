"""Official API market data provider (Finnhub, brapi, CoinGecko, BCB)."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpx

from app.backend.src.config import MarketDataConfig
from app.backend.src.market_data.adapters.brapi import BrapiAdapter, is_brazilian_symbol
from app.backend.src.market_data.adapters.finnhub import FinnhubAdapter
from app.backend.src.market_data.base import MarketDataProvider
from app.backend.src.market_data.provenance import make_provenance
from app.backend.src.market_data.tracker import ProviderRequestTracker
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    ConfidenceLevel,
    CurrentPrice,
    HistoricalPrices,
    MarketIndexSummary,
    MarketSummary,
    PriceInterval,
    PricePoint,
    PriceRange,
    ProviderHealth,
    SourceType,
)

_TWELVE_DATA_BASE = "https://api.twelvedata.com"
_COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_BCB_PTAX_BASE = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"


class ApiMarketDataProvider(MarketDataProvider):
    """Routes to free-tier APIs: Finnhub (US), brapi (B3), CoinGecko (crypto), BCB (FX)."""

    def __init__(self, config: MarketDataConfig, tracker: ProviderRequestTracker | None = None) -> None:
        self._config = config
        self._tracker = tracker
        self._client = httpx.AsyncClient(timeout=20.0, headers={"User-Agent": config.user_agent})
        self._finnhub = FinnhubAdapter(config.finnhub_api_key, self._request)
        self._brapi = BrapiAdapter(config.brapi_api_key, self._request)

    @property
    def provider_name(self) -> str:
        return "api"

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        *,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        symbol: str | None = None,
        asset_type: AssetType | None = None,
        sub_provider: str = "api",
    ) -> tuple[int, Any | None]:
        start = time.perf_counter()
        status = "success"
        http_status: int | None = None
        error_message: str | None = None
        payload: Any | None = None
        try:
            response = await self._client.get(url, params=params, headers=headers)
            http_status = response.status_code
            if response.status_code == 429:
                status = "rate_limited"
                return http_status, None
            response.raise_for_status()
            payload = response.json()
            return http_status, payload
        except httpx.HTTPStatusError as exc:
            status = "http_error"
            http_status = exc.response.status_code
            error_message = str(exc)
            return http_status, None
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            return http_status, None
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if self._tracker:
                await self._tracker.log(
                    provider_name=f"api:{sub_provider}",
                    source_type=SourceType.API,
                    endpoint_or_url=url,
                    symbol=symbol,
                    asset_type=asset_type,
                    status=status,
                    http_status=http_status,
                    response_time_ms=elapsed_ms,
                    error_message=error_message,
                )

    def _cg_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._config.coingecko_api_key:
            headers["x-cg-demo-api-key"] = self._config.coingecko_api_key
        return headers

    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        results: list[AssetSearchResult] = []

        if asset_type in (None, AssetType.CRYPTO):
            _, data = await self._request(
                url=f"{_COINGECKO_BASE}/search",
                params={"query": query},
                headers=self._cg_headers(),
                asset_type=AssetType.CRYPTO,
                sub_provider="coingecko",
            )
            if data:
                for coin in data.get("coins", [])[:10]:
                    results.append(
                        AssetSearchResult(
                            symbol=coin.get("symbol", "").upper(),
                            name=coin.get("name", ""),
                            asset_type=AssetType.CRYPTO,
                            provenance=make_provenance(
                                provider_name="coingecko",
                                source_type=SourceType.API,
                                source_url=f"{_COINGECKO_BASE}/search",
                                confidence_level=ConfidenceLevel.HIGH,
                            ),
                        )
                    )

        if asset_type in (None, AssetType.STOCK, AssetType.ETF) and (
            is_brazilian_symbol(query) or query.upper().endswith(".SA")
        ):
            results.extend(await self._brapi.search(query))

        if asset_type in (None, AssetType.STOCK, AssetType.ETF, AssetType.INDEX):
            results.extend(await self._finnhub.search(query))

        if not results and self._config.twelve_data_api_key:
            results.extend(await self._twelve_data_search(query, asset_type))

        return results

    async def _twelve_data_search(
        self, query: str, asset_type: AssetType | None
    ) -> list[AssetSearchResult]:
        _, data = await self._request(
            url=f"{_TWELVE_DATA_BASE}/symbol_search",
            params={"symbol": query, "apikey": self._config.twelve_data_api_key},
            asset_type=asset_type or AssetType.STOCK,
            sub_provider="twelve_data",
        )
        if not data or not data.get("data"):
            return []
        out: list[AssetSearchResult] = []
        for item in data["data"][:10]:
            at = AssetType.STOCK
            if item.get("instrument_type") == "ETF":
                at = AssetType.ETF
            elif item.get("instrument_type") == "INDEX":
                at = AssetType.INDEX
            out.append(
                AssetSearchResult(
                    symbol=item.get("symbol", ""),
                    name=item.get("instrument_name", ""),
                    asset_type=at,
                    exchange=item.get("exchange"),
                    currency=item.get("currency"),
                    provenance=make_provenance(
                        provider_name="twelve_data",
                        source_type=SourceType.API,
                        source_url=f"{_TWELVE_DATA_BASE}/symbol_search",
                        is_delayed=True,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        warning="Twelve Data free tier — internal use only",
                    ),
                )
            )
        return out

    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        if asset_type == AssetType.CRYPTO:
            return await self._crypto_price(symbol)
        if asset_type == AssetType.FX and symbol.upper().startswith("USD/BRL"):
            return await self._ptax_price()
        if asset_type in (AssetType.STOCK, AssetType.ETF) and is_brazilian_symbol(symbol):
            price = await self._brapi.quote(symbol, asset_type)
            if price:
                return price
        if asset_type in (AssetType.STOCK, AssetType.ETF, AssetType.INDEX):
            price = await self._finnhub.quote(symbol, asset_type)
            if price:
                return price
            return await self._twelve_data_quote(symbol, asset_type)
        return None

    async def _crypto_price(self, symbol: str) -> CurrentPrice | None:
        coin_id = symbol.lower()
        _, data = await self._request(
            url=f"{_COINGECKO_BASE}/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            headers=self._cg_headers(),
            symbol=symbol,
            asset_type=AssetType.CRYPTO,
            sub_provider="coingecko",
        )
        if not data or coin_id not in data:
            _, search = await self._request(
                url=f"{_COINGECKO_BASE}/search",
                params={"query": symbol},
                headers=self._cg_headers(),
                symbol=symbol,
                asset_type=AssetType.CRYPTO,
                sub_provider="coingecko",
            )
            if not search or not search.get("coins"):
                return None
            coin_id = search["coins"][0]["id"]
            _, data = await self._request(
                url=f"{_COINGECKO_BASE}/simple/price",
                params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
                headers=self._cg_headers(),
                symbol=symbol,
                asset_type=AssetType.CRYPTO,
                sub_provider="coingecko",
            )
            if not data:
                return None
        price_data = data[coin_id]
        return CurrentPrice(
            symbol=symbol.upper(),
            asset_type=AssetType.CRYPTO,
            price=float(price_data["usd"]),
            currency="USD",
            change_percent=float(price_data.get("usd_24h_change") or 0),
            provenance=make_provenance(
                provider_name="coingecko",
                source_type=SourceType.API,
                source_url=f"{_COINGECKO_BASE}/simple/price",
                is_delayed=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def _ptax_price(self) -> CurrentPrice | None:
        today = datetime.now(UTC).strftime("%m-%d-%Y")
        url = (
            f"{_BCB_PTAX_BASE}/CotacaoDolarDia(dataCotacao=@dataCotacao)"
            f"?@dataCotacao='{today}'&$format=json"
        )
        _, data = await self._request(
            url=url,
            symbol="USD/BRL",
            asset_type=AssetType.FX,
            sub_provider="bcb",
        )
        if not data or not data.get("value"):
            return None
        latest = data["value"][-1]
        return CurrentPrice(
            symbol="USD/BRL",
            asset_type=AssetType.FX,
            price=float(latest["cotacaoVenda"]),
            currency="BRL",
            provenance=make_provenance(
                provider_name="bcb_ptax",
                source_type=SourceType.API,
                source_url=url,
                is_delayed=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def _twelve_data_quote(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        if not self._config.twelve_data_api_key:
            return None
        _, data = await self._request(
            url=f"{_TWELVE_DATA_BASE}/quote",
            params={"symbol": symbol, "apikey": self._config.twelve_data_api_key},
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="twelve_data",
        )
        if not data or "close" not in data:
            return None
        return CurrentPrice(
            symbol=symbol.upper(),
            asset_type=asset_type,
            price=float(data["close"]),
            currency=data.get("currency", "USD"),
            change=float(data["change"]) if data.get("change") else None,
            change_percent=float(data["percent_change"]) if data.get("percent_change") else None,
            provenance=make_provenance(
                provider_name="twelve_data",
                source_type=SourceType.API,
                source_url=f"{_TWELVE_DATA_BASE}/quote",
                is_realtime=True,
                confidence_level=ConfidenceLevel.MEDIUM,
                warning="Twelve Data free tier — internal use only",
            ),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        if asset_type == AssetType.CRYPTO:
            return await self._crypto_history(symbol, range, interval)
        if asset_type in (AssetType.STOCK, AssetType.ETF) and is_brazilian_symbol(symbol):
            hist = await self._brapi.history(symbol, asset_type, range, interval)
            if hist:
                return hist
        if asset_type in (AssetType.STOCK, AssetType.ETF, AssetType.INDEX):
            hist = await self._finnhub.history(symbol, asset_type, range, interval)
            if hist:
                return hist
            return await self._twelve_data_history(symbol, asset_type, range, interval)
        return None

    async def _crypto_history(
        self, symbol: str, range: PriceRange, interval: PriceInterval
    ) -> HistoricalPrices | None:
        days_map = {
            PriceRange.DAY: 1,
            PriceRange.WEEK: 7,
            PriceRange.MONTH: 30,
            PriceRange.THREE_MONTHS: 90,
            PriceRange.SIX_MONTHS: 180,
            PriceRange.YEAR: 365,
            PriceRange.FIVE_YEARS: 365 * 5,
            PriceRange.MAX: 365 * 10,
        }
        days = days_map[range]
        coin_id = symbol.lower()
        _, data = await self._request(
            url=f"{_COINGECKO_BASE}/coins/{quote(coin_id)}/market_chart",
            params={"vs_currency": "usd", "days": str(days)},
            headers=self._cg_headers(),
            symbol=symbol,
            asset_type=AssetType.CRYPTO,
            sub_provider="coingecko",
        )
        if not data or not data.get("prices"):
            return None
        points = [
            PricePoint(timestamp=datetime.fromtimestamp(ts / 1000, tz=UTC), close=float(price))
            for ts, price in data["prices"]
        ]
        return HistoricalPrices(
            symbol=symbol.upper(),
            asset_type=AssetType.CRYPTO,
            range=range,
            interval=interval,
            points=points,
            provenance=make_provenance(
                provider_name="coingecko",
                source_type=SourceType.API,
                source_url=f"{_COINGECKO_BASE}/coins/{{id}}/market_chart",
                is_delayed=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def _twelve_data_history(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        if not self._config.twelve_data_api_key:
            return None
        outputsize_map = {
            PriceRange.DAY: 1,
            PriceRange.WEEK: 7,
            PriceRange.MONTH: 30,
            PriceRange.THREE_MONTHS: 90,
            PriceRange.SIX_MONTHS: 180,
            PriceRange.YEAR: 365,
            PriceRange.FIVE_YEARS: 5000,
            PriceRange.MAX: 5000,
        }
        td_interval = "1day" if interval == PriceInterval.DAY else "1h"
        _, data = await self._request(
            url=f"{_TWELVE_DATA_BASE}/time_series",
            params={
                "symbol": symbol,
                "interval": td_interval,
                "outputsize": outputsize_map[range],
                "apikey": self._config.twelve_data_api_key,
            },
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="twelve_data",
        )
        if not data or not data.get("values"):
            return None
        points: list[PricePoint] = []
        for row in reversed(data["values"]):
            points.append(
                PricePoint(
                    timestamp=datetime.fromisoformat(row["datetime"]).replace(tzinfo=UTC),
                    open=float(row["open"]) if row.get("open") else None,
                    high=float(row["high"]) if row.get("high") else None,
                    low=float(row["low"]) if row.get("low") else None,
                    close=float(row["close"]),
                    volume=float(row["volume"]) if row.get("volume") else None,
                )
            )
        return HistoricalPrices(
            symbol=symbol.upper(),
            asset_type=asset_type,
            range=range,
            interval=interval,
            points=points,
            provenance=make_provenance(
                provider_name="twelve_data",
                source_type=SourceType.API,
                source_url=f"{_TWELVE_DATA_BASE}/time_series",
                is_delayed=True,
                confidence_level=ConfidenceLevel.MEDIUM,
            ),
        )

    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        if asset_type == AssetType.CRYPTO:
            _, data = await self._request(
                url=f"{_COINGECKO_BASE}/coins/{quote(symbol.lower())}",
                params={"localization": "false", "tickers": "false", "community_data": "false"},
                headers=self._cg_headers(),
                symbol=symbol,
                asset_type=asset_type,
                sub_provider="coingecko",
            )
            if not data:
                return None
            return AssetMetadata(
                symbol=symbol.upper(),
                asset_type=asset_type,
                name=data.get("name", symbol),
                description=(data.get("description") or {}).get("en"),
                market_cap=(data.get("market_data") or {}).get("market_cap", {}).get("usd"),
                currency="USD",
                website=(data.get("links") or {}).get("homepage", [None])[0],
                extra={"coingecko_id": data.get("id")},
                provenance=make_provenance(
                    provider_name="coingecko",
                    source_type=SourceType.API,
                    source_url=f"{_COINGECKO_BASE}/coins/{{id}}",
                    confidence_level=ConfidenceLevel.HIGH,
                ),
            )

        if asset_type in (AssetType.STOCK, AssetType.ETF) and is_brazilian_symbol(symbol):
            meta = await self._brapi.profile(symbol, asset_type)
            if meta:
                return meta

        meta = await self._finnhub.profile(symbol, asset_type)
        if meta:
            return meta

        if not self._config.twelve_data_api_key:
            return None
        _, data = await self._request(
            url=f"{_TWELVE_DATA_BASE}/profile",
            params={"symbol": symbol, "apikey": self._config.twelve_data_api_key},
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="twelve_data",
        )
        if not data:
            return None
        return AssetMetadata(
            symbol=symbol.upper(),
            asset_type=asset_type,
            name=data.get("name", symbol),
            description=data.get("description"),
            sector=data.get("sector"),
            industry=data.get("industry"),
            market_cap=float(data["market_capitalization"]) if data.get("market_capitalization") else None,
            currency=data.get("currency"),
            exchange=data.get("exchange"),
            website=data.get("website"),
            provenance=make_provenance(
                provider_name="twelve_data",
                source_type=SourceType.API,
                source_url=f"{_TWELVE_DATA_BASE}/profile",
                confidence_level=ConfidenceLevel.MEDIUM,
            ),
        )

    async def get_market_summary(self) -> MarketSummary | None:
        indexes = [("SPX", "^GSPC"), ("NDX", "^NDX"), ("DJI", "^DJI")]
        summaries: list[MarketIndexSummary] = []
        for label, fh_symbol in indexes:
            price = await self._finnhub.quote(fh_symbol, AssetType.INDEX)
            if price:
                summaries.append(
                    MarketIndexSummary(
                        symbol=label,
                        name=label,
                        price=price.price,
                        change_percent=price.change_percent,
                    )
                )
        if not summaries:
            return None
        return MarketSummary(
            indexes=summaries,
            updated_at=datetime.now(UTC),
            provenance=make_provenance(
                provider_name="finnhub",
                source_type=SourceType.API,
                source_url="https://finnhub.io/api/v1/quote",
                is_realtime=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def get_provider_health(self) -> ProviderHealth:
        start = time.perf_counter()
        healthy = False
        messages: list[str] = []

        status, _ = await self._request(
            url=f"{_COINGECKO_BASE}/ping",
            headers=self._cg_headers(),
            sub_provider="coingecko",
        )
        if status == 200:
            healthy = True
            messages.append("CoinGecko OK")

        if self._config.finnhub_api_key:
            _, data = await self._request(
                url="https://finnhub.io/api/v1/quote",
                params={"symbol": "AAPL", "token": self._config.finnhub_api_key},
                sub_provider="finnhub",
            )
            if data and data.get("c"):
                healthy = True
                messages.append("Finnhub OK")

        if self._config.brapi_api_key:
            status_b, _ = await self._request(
                url="https://brapi.dev/api/quote/PETR4",
                params={"token": self._config.brapi_api_key},
                sub_provider="brapi",
            )
            if status_b == 200:
                messages.append("brapi OK")
        else:
            status_b, _ = await self._request(
                url="https://brapi.dev/api/quote/PETR4",
                sub_provider="brapi",
            )
            if status_b == 200:
                messages.append("brapi OK (test tickers without token)")

        return ProviderHealth(
            provider_name=self.provider_name,
            healthy=healthy,
            latency_ms=(time.perf_counter() - start) * 1000,
            message="; ".join(messages) if messages else "Configure FINNHUB_API_KEY for US stocks",
            checked_at=datetime.now(UTC),
        )
