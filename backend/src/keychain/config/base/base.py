"""Base configuration class for application settings."""

__all__ = ["BaseConfig"]

from os import getenv
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from .settings_storage import SettingsStorage


class BaseConfig(BaseSettings):
    """Base configuration class that extends Pydantic's BaseSettings.

    This class provides a foundation for application configuration with support for:
    - Environment variables (with nested delimiter support)
    - YAML configuration files
    - Singleton pattern for settings storage

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
        file_path = Path(getenv("CONFIG_FILE_PATH", "configurations/production.yaml"))
        if not file_path.exists():
            logger.error(f"Config file path {file_path} does not exist. Using default path.")
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

    @classmethod
    def get_or_create(cls, reload: bool = False) -> Self:
        """Get the existing settings instance or create a new one.

        This method implements a singleton pattern for configuration settings.
        It retrieves the settings from the SettingsStorage singleton, or creates
        a new instance if one doesn't exist or if reload is requested.

        Args:
            reload: If True, forces creation of a new settings instance even if
                one already exists. Defaults to False.

        Returns:
            The settings instance, either retrieved from storage or newly created.

        """
        storage = SettingsStorage[Self]()

        if not reload and storage.settings:
            return storage.settings

        settings = cls()
        storage.settings = settings
        return settings
