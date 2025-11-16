"""User update request model."""

__all__ = ["UserUpdateRequestModel"]

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class UserUpdateRequestModel(BaseRequestModel):
    """User update request model."""

    name: str = Field(..., description="The name of the user", min_length=3, max_length=50)
