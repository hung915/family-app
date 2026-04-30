from __future__ import annotations

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import auth_settings
from src.auth.utils import create_magic_token
from src.members.models import Member


async def get_member_by_email(session: AsyncSession, email: str) -> Member | None:
    result = await session.execute(select(Member).where(Member.email == email))
    return result.scalar_one_or_none()


async def send_magic_link(email: str) -> None:
    """Send a magic-link email via Resend. Raises httpx.HTTPStatusError on failure."""
    token = create_magic_token(email)
    link = f'{auth_settings.API_BASE_URL}/auth/callback?token={token}'

    html = (
        '<p>Hi there,</p>'
        f'<p><a href="{link}">Click here to log in to the Family App</a>.</p>'
        '<p>This link expires in 15 minutes. If you did not request this, ignore it.</p>'
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {auth_settings.RESEND_API_KEY}'},
            json={
                'from': auth_settings.RESEND_FROM_EMAIL,
                'to': [email],
                'subject': 'Your Family App login link',
                'html': html,
            },
        )
        response.raise_for_status()
