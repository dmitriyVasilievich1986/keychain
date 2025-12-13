"""User create request model."""

__all__ = ["UserCreateRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class UserCreateRequestModel(BaseRequestModel):
    """User create request model."""

    name: str = Field(..., description="The name of the user", min_length=3, max_length=50)
    password: str = Field(..., description="The password of the user", min_length=1)
