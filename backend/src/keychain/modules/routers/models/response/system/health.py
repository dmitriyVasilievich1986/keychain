"""Health check response models."""

__all__ = ["HealthResponse"]

from typing import Literal

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseModel


class HealthResponse(BaseResponseModel):
    """Response model for service health."""

    status: Literal["ok"] = Field(
        "ok",
        description="Overall health status of the service.",
    )
