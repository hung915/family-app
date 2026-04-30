from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.auth.dependencies import get_current_user
from src.database import get_session
from src.main import app
from src.members.constants import MemberRole


@pytest.fixture
def mock_member() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        first_name='Alice',
        nickname='Al',
        role=MemberRole.MOTHER,
        email='alice@family.example',
        birth_date=None,
        due_date=None,
        avatar_url=None,
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture(autouse=True)
def override_session() -> AsyncMock:
    """Replace the real DB session with a mock for all members tests."""
    mock_sess = AsyncMock()

    async def _get_session():
        yield mock_sess

    app.dependency_overrides[get_session] = _get_session
    yield mock_sess
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture(autouse=True)
def override_current_user(mock_member: SimpleNamespace) -> None:
    """Bypass auth for all members tests — any request is treated as authenticated."""

    async def _get_user() -> SimpleNamespace:
        return mock_member

    app.dependency_overrides[get_current_user] = _get_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
