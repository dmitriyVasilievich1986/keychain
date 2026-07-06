"""Password create request model."""

__all__ = ("PasswordCreateRequestModel",)

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class PasswordCreateRequestModel(BaseRequestModel):
    """Password create request model."""

    name: str = Field(..., description="The name of the password", min_length=1)
    image_url: str | None = Field(None, description="The URL of the image associated with the password")
