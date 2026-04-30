"""
Integration tests for src.members.service.

These tests require a live database. They are skipped in CI unless
DATABASE_URL points to a real PostgreSQL instance.

Run locally:
  cd backend
  uv run pytest tests/members/test_service.py -v
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason='requires live database — run manually with a real DATABASE_URL')


async def test_create_and_get_member(session) -> None:
    from src.members import service
    from src.members.constants import MemberRole
    from src.members.schemas import MemberCreate

    data = MemberCreate(first_name='Bob', role=MemberRole.FATHER)
    member = await service.create(session, data)

    assert member.id is not None
    assert member.first_name == 'Bob'
    assert member.role == MemberRole.FATHER

    fetched = await service.get_by_id(session, member.id)
    assert fetched is not None
    assert fetched.id == member.id


async def test_list_all_members(session) -> None:
    from src.members import service
    from src.members.constants import MemberRole
    from src.members.schemas import MemberCreate

    await service.create(session, MemberCreate(first_name='Dad', role=MemberRole.FATHER))
    await service.create(session, MemberCreate(first_name='Mom', role=MemberRole.MOTHER))

    members = await service.list_all(session)
    assert len(members) >= 2


async def test_update_member(session) -> None:
    from src.members import service
    from src.members.constants import MemberRole
    from src.members.schemas import MemberCreate, MemberUpdate

    member = await service.create(session, MemberCreate(first_name='Old', role=MemberRole.CHILD))
    updated = await service.update(session, member, MemberUpdate(first_name='New'))

    assert updated.first_name == 'New'
    assert updated.id == member.id


async def test_delete_member(session) -> None:
    from src.members import service
    from src.members.constants import MemberRole
    from src.members.schemas import MemberCreate

    member = await service.create(session, MemberCreate(first_name='Gone', role=MemberRole.CHILD))
    await service.delete(session, member)

    gone = await service.get_by_id(session, member.id)
    assert gone is None


async def test_get_by_id_returns_none_for_missing(session) -> None:
    from uuid import uuid4

    from src.members import service

    result = await service.get_by_id(session, uuid4())
    assert result is None
