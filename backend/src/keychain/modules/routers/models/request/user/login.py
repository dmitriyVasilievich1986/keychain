__all__ = ["LoginRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class LoginRequestModel(BaseRequestModel):
    """Login request model."""

    username: str = Field(..., description="The username of the user")
    password: str = Field(..., description="The password of the user")
