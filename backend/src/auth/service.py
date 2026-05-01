from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.members.models import Member


async def get_member_by_email(session: AsyncSession, email: str) -> Member | None:
    result = await session.execute(select(Member).where(Member.email == email))
    return result.scalar_one_or_none()
