"""Generic pagination schemas for API responses."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Attributes:
        items: The list of items on the current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed). None when pagination is not used.
        per_page: Number of items per page. None when pagination is not used.
        pages: Total number of pages. None when pagination is not used.
    """

    items: List[T]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None
    pages: Optional[int] = None
