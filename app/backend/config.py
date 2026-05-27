"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Investment Radar"
    app_version: str = "0.1.0"
    database_url: str = f"sqlite+aiosqlite:///{DATA_DIR / 'investment_radar.db'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    enable_live_market_data: bool = True
    market_request_timeout: float = 8.0
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    finnhub_base_url: str = "https://finnhub.io/api/v1"
    alpha_vantage_base_url: str = "https://www.alphavantage.co/query"
    finnhub_api_key: str | None = None
    alpha_vantage_api_key: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
