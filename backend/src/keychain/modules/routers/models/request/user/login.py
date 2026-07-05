"""Login request model."""

__all__ = ("LoginRequestModel",)

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class LoginRequestModel(BaseRequestModel):
    """Request model for logging in a user."""

    username: str = Field(..., description="The username of the user")
    password: str = Field(..., description="The password of the user")
