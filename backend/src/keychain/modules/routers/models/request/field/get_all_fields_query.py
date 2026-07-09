"""Get all fields query model."""

__all__ = ("GetAllFieldsQuery",)

from typing import Literal

from keychain.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllFieldsQuery(
    PaginationWithFiltersQuery[Literal["id", "name", "created_at"], Literal["id", "name", "created_at", "password_id"]]
):
    """Query parameters for getting all fields."""

    pass
