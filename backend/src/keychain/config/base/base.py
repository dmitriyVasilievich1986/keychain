"""Base configuration class for application settings."""

__all__ = ("BaseConfig",)

from os import getenv
from pathlib import Path

import structlog
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

logger = structlog.stdlib.get_logger(__name__)


class BaseConfig(BaseSettings):
    """Base configuration class that extends Pydantic's BaseSettings.

    This class provides a foundation for application configuration with support for:
    - Environment variables (with nested delimiter support)
    - YAML configuration files

    The configuration sources are prioritized in the following order:
    1. Initialization parameters
    2. Environment variables
    3. .env file
    4. YAML configuration file (specified via CONFIG_FILE_PATH env var)

    The YAML file path defaults to `configurations/production.yaml` if not specified.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize the settings sources for configuration loading.

        This method extends the default Pydantic settings sources by adding a YAML
        configuration file source. The YAML file path is determined by the
        `CONFIG_FILE_PATH` environment variable, defaulting to
        `configurations/production.yaml` if not set.

        Args:
            settings_cls: The settings class type.
            init_settings: Settings source for initialization parameters.
            env_settings: Settings source for environment variables.
            dotenv_settings: Settings source for .env file.
            file_secret_settings: Settings source for file-based secrets.

        Returns:
            A tuple of settings sources in priority order, with YAML file source
            added after the default sources.

        Raises:
            FileNotFoundError: If the specified YAML configuration file does not exist.

        """
        environment = getenv("ENVIRONMENT", "production")
        file_path = Path(p) if (p := getenv("CONFIG_FILE_PATH")) else Path(f"configurations/{environment}.yaml")
        if not file_path.exists():
            logger.error("Config file not found", config_file_path=str(file_path))
            raise FileNotFoundError(f"Config file path {file_path} does not exist.")

        return (
            *super().settings_customise_sources(
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ),
            YamlConfigSettingsSource(
                settings_cls=settings_cls,
                yaml_file=file_path,
            ),
        )
