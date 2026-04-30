from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import Field

from src.models import CustomModel

T = TypeVar('T')


class PaginationParams(CustomModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class Page(CustomModel, Generic[T]):  # noqa: UP046
    items: Sequence[T]
    total: int
    offset: int
    limit: int


def pagination_params(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(offset=offset, limit=limit)
