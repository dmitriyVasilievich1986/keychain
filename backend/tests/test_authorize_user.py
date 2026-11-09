"""Tests for the ``authorize_user`` dependency."""

import importlib
from types import SimpleNamespace
from typing import cast

import pytest
import structlog
from fastapi.security import HTTPAuthorizationCredentials

from keychain.services.db_client.client import DBClient

authorize_user_module = importlib.import_module("keychain.modules.middlewares.dependencies.authorize_user")
decode_token_module = importlib.import_module("keychain.utils.decode_token")


class _FakeAuthClient:
    """Auth client stub that decodes every token to user ``7``."""

    def __init__(self, config: object = None) -> None:
        """Accept and ignore the application config."""

    def decode_token(self, token: str) -> SimpleNamespace:
        """Return a decoded token for user ``7``."""
        assert token == "token"
        return SimpleNamespace(user_id="7")


class _FakeUserDAO:
    """User DAO stub returning a user with the requested primary key."""

    def __init__(self, db_client: object) -> None:
        """Accept and ignore the database client."""

    async def get_by_pk(self, pk: int) -> SimpleNamespace:
        """Return a user-like object with ``id`` set to ``pk``."""
        return SimpleNamespace(id=pk)


async def test_binds_user_id_to_contextvars(monkeypatch: pytest.MonkeyPatch) -> None:
    """The authenticated user's id should be bound to structlog's context vars."""
    monkeypatch.setattr(decode_token_module, "AuthClient", _FakeAuthClient)
    monkeypatch.setattr(authorize_user_module, "UserDAO", _FakeUserDAO)

    structlog.contextvars.clear_contextvars()
    try:
        user = await authorize_user_module.authorize_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            cast(DBClient, None),
        )
        assert structlog.contextvars.get_contextvars() == {"user_id": user.id}
        assert user.id == 7
    finally:
        structlog.contextvars.clear_contextvars()
