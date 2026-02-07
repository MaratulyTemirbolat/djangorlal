# Python modules
from typing import Any, Optional, Sequence
from urllib.parse import parse_qs, urlparse

# Rest Framework modules
from rest_framework.pagination import (
    CursorPagination,
    PageNumberPagination,
    LimitOffsetPagination,
)
from rest_framework.response import Response as DRFResponse
from rest_framework.utils.serializer_helpers import ReturnList


def _extract_cursor_token(link: Optional[str], param: str = "cursor") -> Optional[str]:
    """Returns just the cursor token from the link (?cursor=...) for easier frontend handling."""
    if not link:
        return None
    q: dict[str, Any] = parse_qs(urlparse(link).query)
    vals: list[str] = q.get(param)
    return vals[-1] if vals else None


class AbstractCursorPaginator(CursorPagination):
    """
    Abstract cursor paginator with a unified response format.
    - Supports page_size via query (?page_size=...)
    - Returns both full next/previous links and raw tokens
    """

    DEFAULT_PAGE_SIZE = 50
    page_size_query_param = "page_size"
    cursor_query_param = "cursor"
    max_page_size = 200

    def __init__(
        self,
        page_size: int = DEFAULT_PAGE_SIZE,
        ordering: str | Sequence[str] = "-created_at",
        extra_data_return: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize with a default page size and ordering."""

        self.page_size = min(page_size, AbstractCursorPaginator.max_page_size)
        self.ordering = ordering
        self.extra_data_return = extra_data_return or {}
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Returns a paginated response with next/previous links and cursor tokens."""

        next_link: Optional[str] = self.get_next_link()
        prev_link: Optional[str] = self.get_previous_link()
        response: DRFResponse = DRFResponse(
            {
                "pagination": {
                    "next": next_link,
                    "previous": prev_link,
                    "next_cursor": _extract_cursor_token(
                        next_link, self.cursor_query_param
                    ),
                    "previous_cursor": _extract_cursor_token(
                        prev_link, self.cursor_query_param
                    ),
                    "page_size": self.get_page_size(self.request),
                    "returned": len(data),
                    "max_page_size": self.max_page_size,
                    "ordering": self.ordering,
                },
                "data": data,
                **self.extra_data_return,
            }
        )
        return response

    def get_dict_response(self, data: ReturnList) -> dict[str, Any]:
        """Returns a paginated response as a dictionary with next/previous links and cursor tokens."""

        next_link: Optional[str] = self.get_next_link()
        prev_link: Optional[str] = self.get_previous_link()
        return {
            "pagination": {
                "next": next_link,
                "previous": prev_link,
                "next_cursor": _extract_cursor_token(
                    next_link, self.cursor_query_param
                ),
                "previous_cursor": _extract_cursor_token(
                    prev_link, self.cursor_query_param
                ),
                "page_size": self.get_page_size(self.request),
                "returned": len(data),
                "max_page_size": self.max_page_size,
                "ordering": self.ordering,
            },
            "data": data,
        }


class AbstractPageNumberPaginator(PageNumberPagination):
    """Abstract page number paginator with a unified response format."""

    page_size_query_param: str = "page_size"
    page_query_param: str = "page"

    def __init__(self, page_size: int = 6) -> None:
        self.page_size = page_size
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Overriden method to return a paginated response with next/previous links and total page count."""
        response: DRFResponse = DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.num_pages,
                },
                "data": data,
            }
        )
        return response

    def get_dict_response(self, data: ReturnList) -> dict[str, Any]:
        """Get paginated response as a Dictionary with filled data."""

        return {
            "pagination": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.num_pages,
            },
            "data": data,
        }


class AbstractLimitOffsetPaginator(LimitOffsetPagination):
    """Abstract limit-offset paginator with a unified response format."""

    limit: int = 2
    limit_query_param: str = "limit"
    offset: int = 0
    offset_query_param: str = "offset"
    max_limit: int = 5

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Overriden method to return a paginated response with next/previous links and total count."""
    
        response: DRFResponse = DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "data": data,
            }
        )
        return response

