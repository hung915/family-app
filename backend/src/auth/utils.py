from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import jwt

from src.auth.config import auth_settings
from src.auth.constants import JWT_ALGORITHM, JWT_EXPIRE_DAYS, MAGIC_LINK_EXPIRE_MINUTES


def create_magic_token(email: str) -> str:
    """Return a short-lived signed JWT embedding the email address."""
    exp = datetime.now(UTC) + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)
    return jwt.encode({'sub': email, 'exp': exp}, auth_settings.MAGIC_LINK_SECRET, algorithm=JWT_ALGORITHM)


def decode_magic_token(token: str) -> str:
    """Verify the magic-link token and return the email. Raises JWTError on failure."""
    payload = jwt.decode(token, auth_settings.MAGIC_LINK_SECRET, algorithms=[JWT_ALGORITHM])
    return str(payload['sub'])


def create_jwt(member_id: str, email: str) -> str:
    """Return a 30-day session JWT for the given member."""
    exp = datetime.now(UTC) + timedelta(days=JWT_EXPIRE_DAYS)
    return jwt.encode(
        {'sub': member_id, 'email': email, 'exp': exp},
        auth_settings.JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> dict:
    """Verify the session JWT and return its payload. Raises JWTError on failure."""
    return jwt.decode(token, auth_settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
