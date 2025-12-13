"""Dependency provider for database client."""

__all__ = ["get_db"]

from keychain.services.db_client.client import DBClient


def get_db() -> DBClient:
    """Dependency function that provides a singleton instance of DBClient."""
    return DBClient()
