"""Cryptography configuration settings."""

__all__ = ["CryptographyConfig"]

from pydantic import BaseModel, Field, SecretStr


class CryptographyConfig(BaseModel):
    """Cryptography configuration model.

    This model stores the cryptography configuration settings including the secret key.
    """

    secret_key: SecretStr = Field(..., description="The secret key for the application")
