from __future__ import annotations

from pydantic import EmailStr

from src.models import CustomModel


class RequestLinkIn(CustomModel):
    email: EmailStr
