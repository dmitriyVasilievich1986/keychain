"""API configuration model."""

__all__ = ("API",)

from pydantic import BaseModel, Field


class API(BaseModel):
    """API configuration model.

    This model stores the configuration for the API including the allow credentials,
    allow origins, allow methods, and allow headers.

    Attributes:
        allow_credentials: Allow credentials.
        allow_origins: Allow origins.
        allow_methods: Allow methods.
        allow_headers: Allow headers.

    """

    allow_credentials: bool = Field(..., description="Allow credentials")
    allow_origins: list[str] = Field(..., description="Allow origins")
    allow_methods: list[str] = Field(..., description="Allow methods")
    allow_headers: list[str] = Field(..., description="Allow headers")
