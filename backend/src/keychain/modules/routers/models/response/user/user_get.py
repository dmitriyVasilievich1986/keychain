"""User get response model."""

__all__ = ("UserGetResponseModel", "UserGetResponseModelSimple")

from datetime import datetime
from uuid import UUID

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema


class UserGetResponseModelSimple(BaseResponseFromModelSchema):
    """User get response model simple."""

    id: UUID = Field(..., description="The ID of the user")
    name: str = Field(..., description="The name of the user")


class UserGetResponseModel(BaseResponseFromModelSchema):
    """User get response model."""

    id: UUID = Field(..., description="The ID of the user")
    name: str = Field(..., description="The name of the user")
    created_at: datetime = Field(..., description="The creation date of the user")
