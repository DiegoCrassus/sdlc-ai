"""Application configuration from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

SESSION_COOKIE_NAME = "mp_session"
SESSION_TTL_SECONDS = 604800


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MarketPulse API"
    api_prefix: str = "/api/v1"
    debug: bool = False

    market_data_provider: str = "mock"
    twelve_data_api_key: str = ""

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    mock_seed: int = 42

    database_url: str = "sqlite+aiosqlite:///./data/marketpulse.db"

    session_cookie_name: str = SESSION_COOKIE_NAME
    session_ttl_seconds: int = SESSION_TTL_SECONDS

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def session_cookie_secure(self) -> bool:
        return not self.debug


@lru_cache
def get_settings() -> Settings:
    return Settings()
