"""Redis-backed cache for market data responses."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from app.backend.src.config import MarketDataConfig


class MarketDataCache:
    """JSON-serialize Pydantic models in Redis with TTL."""

    def __init__(self, config: MarketDataConfig, redis_client: Any | None = None) -> None:
        self._config = config
        self._redis = redis_client
        self._memory: dict[str, tuple[str, datetime]] = {}

    async def connect(self) -> None:
        if self._redis is not None:
            return
        try:
            import redis.asyncio as redis

            self._redis = redis.from_url(self._config.redis_url, decode_responses=True)
            await self._redis.ping()
        except Exception:
            self._redis = None

    def _ttl_for_key(self, key: str) -> int:
        if key.startswith("md:crypto:price:"):
            return self._config.cache_ttl_crypto_price
        if key.startswith("md:stock:price:") or key.startswith("md:index:price:"):
            return self._config.cache_ttl_stock_price
        if key.startswith("md:hist:"):
            return self._config.cache_ttl_historical
        if key.startswith("md:meta:"):
            return self._config.cache_ttl_metadata
        if key.startswith("md:search:"):
            return self._config.cache_ttl_search
        if key.startswith("md:scrape:"):
            return max(self._config.cache_ttl_scraped, 1800)
        if key.startswith("md:fx:"):
            return 3600
        return 300

    async def get(self, key: str, model: type[BaseModel]) -> BaseModel | None:
        raw = await self._get_raw(key)
        if raw is None:
            return None
        return model.model_validate_json(raw)

    async def get_list(self, key: str, model: type[BaseModel]) -> list[BaseModel] | None:
        raw = await self._get_raw(key)
        if raw is None:
            return None
        payload = json.loads(raw)
        return [model.model_validate(item) for item in payload]

    async def _get_raw(self, key: str) -> str | None:
        if self._redis is not None:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        entry = self._memory.get(key)
        if entry is None:
            return None
        raw, expires_at = entry
        if datetime.now(UTC) > expires_at:
            del self._memory[key]
            return None
        return raw

    async def set(self, key: str, value: BaseModel | list[BaseModel]) -> None:
        if isinstance(value, list):
            raw = json.dumps([item.model_dump(mode="json") for item in value])
        else:
            raw = value.model_dump_json()
        ttl = self._ttl_for_key(key)
        if self._redis is not None:
            try:
                await self._redis.setex(key, ttl, raw)
                return
            except Exception:
                pass
        from datetime import timedelta

        expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        self._memory[key] = (raw, expires_at)

    def cache_key(self, *parts: str) -> str:
        return ":".join(["md", *parts])
