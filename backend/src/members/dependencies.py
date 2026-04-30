from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.members import service
from src.members.exceptions import MemberNotFound
from src.members.models import Member


async def valid_member_id(
    member_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Member:
    member = await service.get_by_id(session, member_id)
    if member is None:
        raise MemberNotFound()
    return member
