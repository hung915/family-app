from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.members.models import Member
from src.members.schemas import MemberCreate, MemberUpdate


async def get_by_id(session: AsyncSession, member_id: UUID) -> Member | None:
    result = await session.execute(select(Member).where(Member.id == member_id))
    return result.scalar_one_or_none()


async def list_all(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[Member]:
    result = await session.execute(select(Member).order_by(Member.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: MemberCreate) -> Member:
    member = Member(**data.model_dump())
    session.add(member)
    await session.flush()
    await session.refresh(member)
    return member


async def update(session: AsyncSession, member: Member, data: MemberUpdate) -> Member:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    await session.flush()
    await session.refresh(member)
    return member


async def delete(session: AsyncSession, member: Member) -> None:
    await session.delete(member)
    await session.flush()
