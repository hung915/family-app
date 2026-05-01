from __future__ import annotations

from datetime import date, datetime

from pydantic import EmailStr, Field

from src.members.constants import MemberRole
from src.models import CustomModel


class MemberBase(CustomModel):
    first_name: str = Field(min_length=1, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)
    role: MemberRole
    birth_date: date | None = None
    due_date: date | None = None
    avatar_url: str | None = Field(default=None, max_length=512)
    email: EmailStr | None = None


class MemberCreate(MemberBase):
    password: str | None = Field(default=None, min_length=8)


class MemberUpdate(CustomModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)
    role: MemberRole | None = None
    birth_date: date | None = None
    due_date: date | None = None
    avatar_url: str | None = Field(default=None, max_length=512)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class MemberResponse(MemberBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
