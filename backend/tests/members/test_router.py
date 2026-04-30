from __future__ import annotations

from datetime import UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.main import app
from src.members.constants import MemberRole
from src.members.dependencies import valid_member_id


@pytest.fixture
def override_valid_member(mock_member: SimpleNamespace):
    """Override the valid_member_id dependency to return the mock member."""

    async def _dep() -> SimpleNamespace:
        return mock_member

    app.dependency_overrides[valid_member_id] = _dep
    yield mock_member
    app.dependency_overrides.pop(valid_member_id, None)


# ── list ──────────────────────────────────────────────────────────────────────


async def test_list_members_empty(client: AsyncClient) -> None:
    with patch('src.members.service.list_all', new_callable=AsyncMock, return_value=[]):
        response = await client.get('/members')
    assert response.status_code == 200
    assert response.json() == []


async def test_list_members_returns_items(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    with patch('src.members.service.list_all', new_callable=AsyncMock, return_value=[mock_member]):
        response = await client.get('/members')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['first_name'] == mock_member.first_name


# ── create ────────────────────────────────────────────────────────────────────


async def test_create_member_ok(client: AsyncClient, mock_member: SimpleNamespace) -> None:
    with patch('src.members.service.create', new_callable=AsyncMock, return_value=mock_member):
        response = await client.post(
            '/members',
            json={'first_name': 'Alice', 'role': 'mother'},
        )
    assert response.status_code == 201
    assert response.json()['first_name'] == 'Alice'
    assert response.json()['role'] == MemberRole.MOTHER


async def test_create_member_missing_required_fields(client: AsyncClient) -> None:
    response = await client.post('/members', json={})
    assert response.status_code == 422


async def test_create_member_first_name_too_short(client: AsyncClient) -> None:
    response = await client.post('/members', json={'first_name': '', 'role': 'father'})
    assert response.status_code == 422


async def test_create_member_invalid_role(client: AsyncClient) -> None:
    response = await client.post('/members', json={'first_name': 'Bob', 'role': 'alien'})
    assert response.status_code == 422


# ── get ───────────────────────────────────────────────────────────────────────


async def test_get_member_ok(client: AsyncClient, override_valid_member: SimpleNamespace) -> None:
    response = await client.get(f'/members/{override_valid_member.id}')
    assert response.status_code == 200
    assert response.json()['first_name'] == override_valid_member.first_name


async def test_get_member_not_found(client: AsyncClient) -> None:
    with patch('src.members.service.get_by_id', new_callable=AsyncMock, return_value=None):
        response = await client.get(f'/members/{uuid4()}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'MEMBER_NOT_FOUND'


# ── update ────────────────────────────────────────────────────────────────────


async def test_update_member_ok(
    client: AsyncClient,
    mock_member: SimpleNamespace,
    override_valid_member: SimpleNamespace,
) -> None:
    from datetime import datetime

    updated = SimpleNamespace(**vars(mock_member))
    updated.first_name = 'Updated'
    updated.updated_at = datetime.now(UTC)

    with patch('src.members.service.update', new_callable=AsyncMock, return_value=updated):
        response = await client.patch(f'/members/{mock_member.id}', json={'first_name': 'Updated'})
    assert response.status_code == 200
    assert response.json()['first_name'] == 'Updated'


async def test_update_member_not_found(client: AsyncClient) -> None:
    with patch('src.members.service.get_by_id', new_callable=AsyncMock, return_value=None):
        response = await client.patch(f'/members/{uuid4()}', json={'first_name': 'X'})
    assert response.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────


async def test_delete_member_ok(client: AsyncClient, override_valid_member: SimpleNamespace) -> None:
    with patch('src.members.service.delete', new_callable=AsyncMock):
        response = await client.delete(f'/members/{override_valid_member.id}')
    assert response.status_code == 204


async def test_delete_member_not_found(client: AsyncClient) -> None:
    with patch('src.members.service.get_by_id', new_callable=AsyncMock, return_value=None):
        response = await client.delete(f'/members/{uuid4()}')
    assert response.status_code == 404
