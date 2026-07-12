from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envelope for paginated list responses."""

    items: list[T]
    total: int
    page: int
    size: int


class Problem(BaseModel):
    """RFC 7807 problem document — declared so it shows up in the OpenAPI schema
    for error responses."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
