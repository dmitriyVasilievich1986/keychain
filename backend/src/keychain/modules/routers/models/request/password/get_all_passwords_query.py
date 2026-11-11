"""Get all passwords query model."""

__all__ = ("GetAllPasswordsQuery",)

from typing import Literal

from pydantic import Field

from keychain.modules.routers.models.base.metadata import PaginationWithFiltersQuery


class GetAllPasswordsQuery(
    PaginationWithFiltersQuery[Literal["id", "name", "created_at"], Literal["id", "name", "created_at", "user_id"]]
):
    """Query parameters for getting all passwords."""

    show_deleted: bool = Field(default=False, description="Whether to include passwords marked as deleted")
