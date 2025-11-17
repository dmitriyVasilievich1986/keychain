"""Password get response model."""

__all__ = ["PasswordGetResponseModel", "PasswordGetResponseModelSimple"]

from datetime import datetime

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseModel
from keychain.modules.routers.models.response.field import FieldGetResponseModelSimple


class PasswordGetResponseModelSimple(BaseResponseModel):
    """Password get response model simple."""

    id: int = Field(..., description="The ID of the password")
    name: str = Field(..., description="The name of the password")


class PasswordGetResponseModel(BaseResponseModel):
    """Password get response model."""

    id: int = Field(..., description="The ID of the password")
    name: str = Field(..., description="The name of the password")
    created_at: datetime = Field(..., description="The creation date of the password")
    image_url: str | None = Field(None, description="The URL of the image associated with the password")
    user_id: int = Field(..., description="The ID of the user who owns the password")
    fields: list[FieldGetResponseModelSimple] = Field(..., description="The fields associated with the password")
