"""Query model combining pagination parameters with JSON-encoded filters."""

__all__ = ("PaginationWithFiltersQuery",)

from pydantic import Field, Json

from keychain.utils.filter import Filter

from .pagination_query import PaginationQuery


class PaginationWithFiltersQuery[SortByType: str, FilterColumnsType: str](PaginationQuery[SortByType]):
    """Paginated list query with optional resource-scoped filters.

    Extends :class:`PaginationQuery` with a ``filters`` field parsed from JSON
    in the query string. ``FilterColumnsType`` constrains allowed column names
    per endpoint.
    """

    filters: Json[list[Filter[FilterColumnsType]]] | None = Field(
        None, description="The filters to apply to the parameters"
    )
