from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import RedirectResponse
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service
from src.auth.config import auth_settings
from src.auth.constants import COOKIE_NAME, JWT_EXPIRE_DAYS
from src.auth.dependencies import get_current_user
from src.auth.exceptions import EmailNotAllowed, InvalidToken, TokenExpired
from src.auth.schemas import RequestLinkIn
from src.auth.utils import create_jwt, decode_magic_token
from src.config import settings
from src.database import get_session
from src.members.models import Member
from src.members.schemas import MemberResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/request-link',
    status_code=status.HTTP_200_OK,
    summary='Request a magic login link',
    description='Sends a one-time login link to the supplied email if it belongs to a family member.',
)
async def request_link(
    data: RequestLinkIn,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    member = await service.get_member_by_email(session, str(data.email))
    if member is None:
        raise EmailNotAllowed()
    await service.send_magic_link(str(data.email))
    return {'detail': 'Magic link sent — check your email.'}


@router.get(
    '/callback',
    summary='Verify magic link and issue session cookie',
    description='Validates the token from the magic link, sets an HttpOnly JWT cookie, and redirects to the frontend.',
)
async def callback(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    try:
        email = decode_magic_token(token)
    except ExpiredSignatureError:
        raise TokenExpired() from None
    except JWTError:
        raise InvalidToken() from None

    member = await service.get_member_by_email(session, email)
    if member is None:
        raise InvalidToken()

    jwt_token = create_jwt(str(member.id), email)
    redirect = RedirectResponse(url=auth_settings.FRONTEND_URL, status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key=COOKIE_NAME,
        value=jwt_token,
        httponly=True,
        secure=settings.ENV != 'local',
        samesite='lax',
        max_age=JWT_EXPIRE_DAYS * 24 * 3600,
    )
    return redirect


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
