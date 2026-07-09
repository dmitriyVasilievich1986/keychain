"""Application configuration settings."""

__all__ = ["AppConfig"]

from pydantic import Field

from .auth import AuthConfig
from .base import BaseConfig
from .cryptography import CryptographyConfig
from .db import DBConfig
from .info import AppInfo


class AppConfig(BaseConfig):
    """Application configuration class.

    This class extends BaseConfig and defines the main application settings,
    including the environment name and application information. It supports
    configuration from environment variables, .env files, and YAML configuration
    files as defined in the base class.

    Attributes:
        environment: The environment name (e.g., "local", "dev", "prod").
            Can be set via the ENV environment variable shortcut.
        info: Application information including name and version.

    """

    environment: str = Field(
        "local",
        description="Environment name",
        examples=["local", "dev", "prod"],
    )
    info: AppInfo = Field(description="Application information")
    db: DBConfig = Field(description="Database configuration")
    cryptography: CryptographyConfig = Field(description="Cryptography configuration")
    auth: AuthConfig = Field(description="Authentication configuration")
