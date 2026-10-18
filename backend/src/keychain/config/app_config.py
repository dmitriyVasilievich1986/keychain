"""Application configuration settings."""

__all__ = ("AppConfig",)

from typing import Literal

from pydantic import Field

from .base import BaseConfig
from .models import AppInfo, AuthConfig, CryptographyConfig, DBConfig


class AppConfig(BaseConfig):
    """Application configuration class.

    This class extends BaseConfig and defines the main application settings,
    including the environment name and application information. It supports
    configuration from environment variables, .env files, and YAML configuration
    files as defined in the base class.

    Attributes:
        environment: The environment name (e.g., "local", "production").
            Can be set via the ENVIRONMENT environment variable shortcut.
        info: Application information including name and version.
        db: Database configuration.
        cryptography: Cryptography configuration.
        auth: Authentication configuration.

    """

    environment: Literal["local", "production", "test"] = Field(
        "local",
        description="Environment name",
    )

    info: AppInfo = Field(..., description="Application information")
    db: DBConfig = Field(..., description="Database configuration")
    cryptography: CryptographyConfig = Field(..., description="Cryptography configuration")
    auth: AuthConfig = Field(..., description="Authentication configuration")

    @property
    def is_local(self) -> bool:
        """Check if the application is running in local mode."""
        return self.environment == "local"

    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return self.environment == "production"

    @property
    def is_test(self) -> bool:
        """Check if the application is running in test mode."""
        return self.environment == "test"
