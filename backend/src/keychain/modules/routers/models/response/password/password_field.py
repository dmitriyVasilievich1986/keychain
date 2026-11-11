"""Response models for fields embedded in a password document."""

__all__ = ("PasswordFieldGet", "PasswordFieldValueGet")

from datetime import datetime

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseFromModelSchema


class PasswordFieldValueGet(BaseResponseFromModelSchema):
    """Response model for one historical value of a password field."""

    value: str = Field(..., description="The value of the field")
    created_at: datetime = Field(..., description="The creation date of the value")


class PasswordFieldGet(BaseResponseFromModelSchema):
    """Response model for a field embedded in a password."""

    name: str = Field(..., description="The name of the field")
    position: int = Field(..., description="The position of the field within the password")
    values: list[PasswordFieldValueGet] = Field(..., description="The values of the field")
    created_at: datetime = Field(..., description="The creation date of the field")
    updated_at: datetime = Field(..., description="The last update date of the field")
    deleted_at: datetime | None = Field(None, description="The deletion date of the field")
