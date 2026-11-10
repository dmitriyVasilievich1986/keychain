"""Tests for the ``authorize_user`` dependency."""

import importlib
from types import SimpleNamespace
from typing import cast

import pytest
import structlog
from fastapi.security import HTTPAuthorizationCredentials

from keychain.config import AppConfig
from keychain.services.db_client.firestore import FirestoreClient

authorize_user_module = importlib.import_module("keychain.modules.middlewares.dependencies.authorize_user")
decode_token_module = importlib.import_module("keychain.utils.decode_token")


USER_ID = "8d6c8f43-5a39-4b49-8b2f-0b6a3b1a6e7f"


class _FakeAuthClient:
    """Auth client stub that decodes every token to user ``USER_ID``."""

    def __init__(self, config: object = None) -> None:
        """Accept and ignore the application config."""

    def decode_token(self, token: str) -> SimpleNamespace:
        """Return a decoded token for user ``USER_ID``."""
        assert token == "token"
        return SimpleNamespace(user_id=USER_ID)


class _FakeUserDAO:
    """User DAO stub returning a user with the requested document ID."""

    def __init__(self, firestore_client: object, collection_name: str | None = None) -> None:
        """Accept and ignore the Firestore client and collection name."""

    async def get_by_id(self, document_id: str) -> SimpleNamespace:
        """Return a user-like object with ``id`` set to ``document_id``."""
        return SimpleNamespace(id=document_id)


async def test_binds_user_id_to_contextvars(monkeypatch: pytest.MonkeyPatch) -> None:
    """The authenticated user's id should be bound to structlog's context vars."""
    monkeypatch.setattr(decode_token_module, "AuthClient", _FakeAuthClient)
    monkeypatch.setattr(authorize_user_module, "UserDAO", _FakeUserDAO)

    structlog.contextvars.clear_contextvars()
    try:
        user = await authorize_user_module.authorize_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            cast(FirestoreClient, None),
            cast(AppConfig, SimpleNamespace(db=SimpleNamespace(users=SimpleNamespace(collection_name="users")))),
        )
        assert structlog.contextvars.get_contextvars() == {"user_id": user.id}
        assert user.id == USER_ID
    finally:
        structlog.contextvars.clear_contextvars()
