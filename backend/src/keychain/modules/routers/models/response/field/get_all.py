"""Get all fields response model."""

__all__ = ("GetAllFieldsResponse", "SimpleFieldGet")

from pydantic import Field

from keychain.modules.routers.models.base.metadata import PaginationMetadata
from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema


class SimpleFieldGet(BaseResponseFromModelSchema):
    """Response model for getting a simple field in list view."""

    id: int = Field(..., description="The unique identifier for the field")
    name: str = Field(..., description="The name of the field")
    is_deleted: bool = Field(..., description="Whether the field is deleted")
    password_id: int = Field(..., description="The ID of the password that owns the field")
    value_decrypted: str = Field(..., description="The decrypted value of the field")


class GetAllFieldsResponse(BaseResponseFromModelSchema):
    """Response model for getting all fields."""

    data: list[SimpleFieldGet] = Field(..., description="The list of fields")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
