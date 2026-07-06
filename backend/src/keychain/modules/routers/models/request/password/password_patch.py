"""Password patch request model."""

__all__ = ("PasswordPatchRequestModel",)

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class PasswordPatchRequestModel(BaseRequestModel):
    """Password patch request model."""

    name: str | None = Field(None, description="The name of the password", min_length=1)
    image_url: str | None = Field(None, description="The URL of the image associated with the password")
