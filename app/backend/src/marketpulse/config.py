"""Application configuration from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MarketPulse API"
    api_prefix: str = "/api/v1"
    debug: bool = False

    market_data_provider: str = "mock"
    twelve_data_api_key: str = ""

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    mock_seed: int = 42

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
