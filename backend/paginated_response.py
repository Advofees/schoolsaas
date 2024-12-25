import typing
from pydantic import BaseModel

T = typing.TypeVar("T")


class PaginatedResponse(BaseModel, typing.Generic[T]):
    total: int
    page: int
    limit: int
    data: list[T]
