"""Tests for application configuration loading in the test environment."""

from keychain.config import AppConfig


def test_config_targets_test_database(app_config: AppConfig) -> None:
    """The active configuration must point at the throw-away ``test_db``."""
    assert app_config.db.provider == "postgresql"
    assert app_config.db.name == "test_db"


def test_sqlalchemy_uri_uses_asyncpg(app_config: AppConfig) -> None:
    """The SQLAlchemy URL should use asyncpg and target ``test_db``."""
    uri = str(app_config.db.sqlalchemy_uri)
    assert uri.startswith("postgresql+asyncpg://")
    assert uri.endswith("/test_db")
