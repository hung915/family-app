import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client wired directly to the ASGI app — no real server needed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
