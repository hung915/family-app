from __future__ import annotations

from pydantic import EmailStr, Field

from src.models import CustomModel


class LoginIn(CustomModel):
    email: EmailStr
    password: str = Field(min_length=1)
