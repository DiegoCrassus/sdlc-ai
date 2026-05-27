import pytest
from httpx import ASGITransport, AsyncClient

from app.backend.config import settings
from app.backend.main import app


@pytest.fixture(autouse=True)
def disable_live_market_data():
    previous = settings.enable_live_market_data
    settings.enable_live_market_data = False
    yield
    settings.enable_live_market_data = previous


@pytest.fixture
async def client():
    from app.backend.database import init_db

    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
