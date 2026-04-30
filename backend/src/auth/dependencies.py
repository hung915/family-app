from __future__ import annotations

from uuid import UUID

from fastapi import Cookie, Depends
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.constants import COOKIE_NAME
from src.auth.exceptions import InvalidToken, NotAuthenticated
from src.auth.utils import decode_jwt
from src.database import get_session
from src.members import service as member_service
from src.members.models import Member


async def get_current_user(
    token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
) -> Member:
    if token is None:
        raise NotAuthenticated()
    try:
        payload = decode_jwt(token)
        member_id = UUID(payload['sub'])
    except JWTError, KeyError, ValueError:
        raise InvalidToken() from None

    member = await member_service.get_by_id(session, member_id)
    if member is None:
        raise InvalidToken()
    return member
