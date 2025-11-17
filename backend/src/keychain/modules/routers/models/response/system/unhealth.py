"""Unhealth response models."""

__all__ = ["ErrorResponse"]

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseModel


class ErrorResponse(BaseResponseModel):
    """Response model for error messages."""

    detail: str = Field(
        ...,
        description="Error detail message.",
    )
