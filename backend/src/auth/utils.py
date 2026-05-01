from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from src.auth.config import auth_settings
from src.auth.constants import JWT_ALGORITHM, JWT_EXPIRE_DAYS

_pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_jwt(member_id: str, email: str) -> str:
    exp = datetime.now(UTC) + timedelta(days=JWT_EXPIRE_DAYS)
    return jwt.encode(
        {'sub': member_id, 'email': email, 'exp': exp},
        auth_settings.JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, auth_settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
