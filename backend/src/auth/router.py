from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service
from src.auth.constants import COOKIE_NAME, JWT_EXPIRE_DAYS
from src.auth.dependencies import get_current_user
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import LoginIn
from src.auth.utils import create_jwt, verify_password
from src.config import settings
from src.database import get_session
from src.members.models import Member
from src.members.schemas import MemberResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/login',
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary='Log in with email and password',
    description='Verifies credentials, sets an HttpOnly JWT cookie, and returns the member profile.',
)
async def login(
    data: LoginIn,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Member:
    member = await service.get_member_by_email(session, str(data.email))
    if member is None or member.password_hash is None or not verify_password(data.password, member.password_hash):
        raise InvalidCredentials()

    jwt_token = create_jwt(str(member.id), str(data.email))
    response.set_cookie(
        key=COOKIE_NAME,
        value=jwt_token,
        httponly=True,
        secure=settings.ENV != 'local',
        samesite='lax',
        max_age=JWT_EXPIRE_DAYS * 24 * 3600,
    )
    return member


@router.get(
    '/me',
    response_model=MemberResponse,
    summary='Return the currently authenticated user',
    description='Reads the session cookie and returns the matching member profile.',
)
async def me(current_user: Member = Depends(get_current_user)) -> Member:
    return current_user


@router.post(
    '/logout',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Clear the session cookie',
    description='Deletes the access_token cookie. No auth required.',
)
async def logout(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, httponly=True, samesite='lax')
