"""Application configuration settings."""

__all__ = ["AppConfig"]

from pydantic import Field

from .base import BaseConfig
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
        examples=("local", "dev", "prod"),
        json_schema_extra={"env_shortcut": "ENV"},
    )
    info: AppInfo = Field(description="Application information")
