from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

_MIGRATION_COLUMNS = (
    ("source_mime", "VARCHAR(100)"),
    ("analysis_json", "TEXT"),
    ("template_status", "VARCHAR(20) DEFAULT 'published'"),
    ("template_version", "INTEGER DEFAULT 1"),
    ("published_at", "DATETIME"),
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_workspaces)

    async with SessionLocal() as session:
        from app.fixtures.seed import ensure_example_workspace

        await ensure_example_workspace(session)


def _migrate_workspaces(connection) -> None:
    rows = connection.execute(text("PRAGMA table_info(workspaces)")).fetchall()
    if not rows:
        return
    existing = {row[1] for row in rows}
    for name, col_type in _MIGRATION_COLUMNS:
        if name not in existing:
            connection.execute(text(f"ALTER TABLE workspaces ADD COLUMN {name} {col_type}"))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def dumps_json(data: object) -> str:
    import json

    return json.dumps(data, ensure_ascii=False)


def loads_json(raw: str) -> object:
    import json

    return json.loads(raw)
