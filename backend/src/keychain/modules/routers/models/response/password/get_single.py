"""Password get response model."""

__all__ = ("PasswordGetResponseModel",)

from datetime import datetime
from uuid import UUID

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema

from .password_field import PasswordFieldGet


class PasswordGetResponseModel(BaseResponseFromModelSchema):
    """Password get response model."""

    id: UUID = Field(..., description="The ID of the password")
    name: str = Field(..., description="The name of the password")
    created_at: datetime = Field(..., description="The creation date of the password")
    updated_at: datetime = Field(..., description="The last update date of the password")
    image_url: str | None = Field(None, description="The URL of the image associated with the password")
    user_id: UUID = Field(..., description="The ID of the user who owns the password")
    fields: list[PasswordFieldGet] = Field(..., description="The fields associated with the password")
