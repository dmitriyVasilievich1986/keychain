"""Query model combining pagination parameters with JSON-encoded filters."""

__all__ = ("PaginationWithFiltersQuery",)


from typing import Any, cast

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

    @property
    def filters_dict(self) -> list[dict[str, Any]]:
        """Expose parsed filters as plain dicts for DAO layers.

        Returns:
            list[dict[str, Any]]: Serialized filter objects; empty when
                ``filters`` is None.

        """
        if self.filters is None:
            return []

        return cast(list[dict[str, Any]], self.filters)
