from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_session
from src.members import service
from src.members.dependencies import valid_member_id
from src.members.models import Member
from src.members.schemas import MemberCreate, MemberResponse, MemberUpdate

router = APIRouter(prefix='/members', tags=['members'])


@router.get(
    '',
    response_model=list[MemberResponse],
    summary='List all family members',
    description='Returns every member of the family household.',
)
async def list_members(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    _current_user: Member = Depends(get_current_user),
) -> list[Member]:
    return await service.list_all(session, limit=limit, offset=offset)


@router.post(
    '',
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Add a family member',
    description='Creates a new member profile in the household.',
)
async def create_member(
    data: MemberCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: Member = Depends(get_current_user),
) -> Member:
    member = await service.create(session, data)
    await session.commit()
    return member


@router.get(
    '/{member_id}',
    response_model=MemberResponse,
    summary='Get a family member',
    description='Returns a single member by UUID.',
)
async def get_member(
    member: Member = Depends(valid_member_id),
    _current_user: Member = Depends(get_current_user),
) -> Member:
    return member


@router.patch(
    '/{member_id}',
    response_model=MemberResponse,
    summary='Update a family member',
    description='Partially updates a member profile. Only supplied fields are changed.',
)
async def update_member(
    data: MemberUpdate,
    member: Member = Depends(valid_member_id),
    session: AsyncSession = Depends(get_session),
    _current_user: Member = Depends(get_current_user),
) -> Member:
    updated = await service.update(session, member, data)
    await session.commit()
    return updated


@router.delete(
    '/{member_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Remove a family member',
    description='Permanently deletes a member profile.',
)
async def delete_member(
    member: Member = Depends(valid_member_id),
    session: AsyncSession = Depends(get_session),
    _current_user: Member = Depends(get_current_user),
) -> None:
    await service.delete(session, member)
    await session.commit()
