"""Health check response models."""

__all__ = ["HealthResponse"]

from typing import Any, Literal

from pydantic import Field

from keychain.modules.routers.models.base.response import BaseResponseModel


class ServiceHealth(BaseResponseModel):
    """Response model for service health."""

    name: str = Field(
        description="Name of the service.",
    )
    status: Literal["UP", "DOWN"] = Field(
        "UP",
        description="Overall health status of the service.",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra information about the service health.",
    )


class HealthResponse(BaseResponseModel):
    """Response model for service health."""

    status: Literal["UP", "DOWN"] = Field(
        "UP",
        description="Overall health status of the service.",
    )
    services: list[ServiceHealth] = Field(
        description="List of service health checks.",
    )
