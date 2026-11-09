"""User password change request model."""

__all__ = ("UserPasswordChangeRequestModel",)

from pydantic import Field

from keychain.modules.routers.models.base.request import BaseRequestModel


class UserPasswordChangeRequestModel(BaseRequestModel):
    """Request model for changing the current user's password."""

    old_password: str = Field(..., description="The current password of the user", min_length=1)
    new_password: str = Field(..., description="The new password of the user", min_length=1)
