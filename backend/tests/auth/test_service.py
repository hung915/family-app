"""
Integration tests for src.auth.service.

Require a live database + a real Resend API key.
Skipped automatically in CI.

Run locally:
    cd backend
    uv run pytest tests/auth/test_service.py -v
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason='requires live database and Resend API key — run manually')


async def test_get_member_by_email_found(session) -> None:
    from src.auth import service
    from src.members import service as member_service
    from src.members.constants import MemberRole
    from src.members.schemas import MemberCreate

    member = await member_service.create(
        session, MemberCreate(first_name='Test', role=MemberRole.FATHER, email='test@family.example')
    )
    await session.flush()

    found = await service.get_member_by_email(session, 'test@family.example')
    assert found is not None
    assert found.id == member.id


async def test_get_member_by_email_not_found(session) -> None:
    from src.auth import service

    result = await service.get_member_by_email(session, 'nobody@family.example')
    assert result is None
