"""Dependency provider for application settings."""

__all__ = ["get_config"]

from keychain.config import AppConfig


def get_config() -> AppConfig:
    """Dependency function that provides a singleton instance of AppConfig."""
    return AppConfig.get_or_create()
