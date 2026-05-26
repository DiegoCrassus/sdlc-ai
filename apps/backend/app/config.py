from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./data/rpg_op.db"
    upload_dir: Path = Path("./data/uploads")
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    api_prefix: str = "/v1"
    agent_model: str = "openai:gpt-4o-mini"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
Path("./data").mkdir(parents=True, exist_ok=True)
