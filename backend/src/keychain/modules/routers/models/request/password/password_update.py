"""Password update request model."""

__all__ = ["PasswordUpdateRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class PasswordUpdateRequestModel(BaseRequestModel):
    """Password update request model."""

    name: str = Field(..., description="The name of the password", min_length=1)
    image_url: str | None = Field(..., description="The URL of the image associated with the password")
