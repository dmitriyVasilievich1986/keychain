"""Tests for :class:`UserDAO` against the Firestore emulator."""

import pytest
from google.api_core.exceptions import NotFound

from keychain.services.daos import UserDAO

pytestmark = pytest.mark.integration


async def test_create_user(user_dao: UserDAO) -> None:
    """A created user is persisted with a hashed, verifiable password."""
    user = await user_dao.create(name="alice", password="secret123")

    stored = await user_dao.get_by_id(user.id)
    assert stored.name == "alice"
    assert stored.verify_password("secret123") is True
    assert stored.verify_password("wrong") is False


async def test_create_user_requires_password(user_dao: UserDAO) -> None:
    """Creating a user without a password is rejected."""
    with pytest.raises(ValueError, match="Password is required"):
        await user_dao.create(name="alice")


async def test_get_by_username(user_dao: UserDAO) -> None:
    """A user can be fetched by its username."""
    user = await user_dao.create(name="bob", password="pw")

    fetched = await user_dao.get_by_username("bob")

    assert fetched.id == user.id


async def test_get_by_username_not_found(user_dao: UserDAO) -> None:
    """Looking up an unknown username raises ``NotFound``."""
    with pytest.raises(NotFound):
        await user_dao.get_by_username("nobody")


async def test_get_all_returns_all_users(user_dao: UserDAO) -> None:
    """``get_all`` returns every user and an accurate total count."""
    await user_dao.create(name="user-1", password="pw")
    await user_dao.create(name="user-2", password="pw")

    rows, total = await user_dao.get_all()

    assert total == 2
    assert {row.name for row in rows} == {"user-1", "user-2"}


async def test_reset_password(user_dao: UserDAO) -> None:
    """Resetting a password stores a new, verifiable hash."""
    user = await user_dao.create(name="carol", password="old-password")

    await user_dao.reset_password(user.id, "new-password")

    refreshed = await user_dao.get_by_id(user.id)
    assert refreshed.verify_password("new-password") is True
    assert refreshed.verify_password("old-password") is False


async def test_delete_user(user_dao: UserDAO) -> None:
    """A deleted user no longer exists in the database."""
    user = await user_dao.create(name="dave", password="pw")

    assert await user_dao.delete(user.id) is True
    assert await user_dao.get_total() == 0
    with pytest.raises(NotFound):
        await user_dao.delete(user.id)
