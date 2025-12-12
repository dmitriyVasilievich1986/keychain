"""Cryptography configuration settings."""

__all__ = ["AuthConfig"]

from pydantic import BaseModel, Field, SecretStr


class AuthConfig(BaseModel):
    """Authentication configuration model.

    This model stores the authentication configuration settings including the JWT secret key.
    """

    jwt_secret_key: SecretStr = Field(..., description="The secret key for the application")
    algorithm: str = Field(..., description="The algorithm to use for the authentication")
    access_token_expire_minutes: int = Field(..., description="The number of minutes to expire the access token")
