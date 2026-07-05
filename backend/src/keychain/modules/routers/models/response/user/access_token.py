"""Access token response model."""

__all__ = ("AccessTokenResponseModel",)

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseModel


class AccessTokenResponseModel(BaseResponseModel):
    """Access token response model."""

    access_token: str = Field(..., description="The access token")
