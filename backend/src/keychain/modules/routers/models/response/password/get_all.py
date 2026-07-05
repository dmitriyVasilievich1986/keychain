"""Get all passwords response model."""

__all__ = ("GetAllPasswordsResponse", "SimplePasswordGet")

from pydantic import Field

from keychain.modules.routers.models.base.metadata import PaginationMetadata
from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema


class SimplePasswordGet(BaseResponseFromModelSchema):
    """Response model for getting a simple password in list view."""

    id: int = Field(..., description="The unique identifier for the password")
    name: str = Field(..., description="The name of the password")
    image_url: str | None = Field(..., description="The URL of the image associated with the password")


class GetAllPasswordsResponse(BaseResponseFromModelSchema):
    """Response model for getting all passwords."""

    data: list[SimplePasswordGet] = Field(..., description="The list of passwords")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
