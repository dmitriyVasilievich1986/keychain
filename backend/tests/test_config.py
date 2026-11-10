"""Tests for application configuration loading in the test environment."""

from keychain.config import AppConfig


def test_config_uses_test_environment(app_config: AppConfig) -> None:
    """The active configuration must be loaded from ``test.yaml``."""
    assert app_config.is_test is True


def test_config_has_firestore_collections(app_config: AppConfig) -> None:
    """Passwords and users live in separate Firestore collections."""
    assert app_config.db.firestore.collection_name == "password"
    assert app_config.db.users.collection_name == "users"
