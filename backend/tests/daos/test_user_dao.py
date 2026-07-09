"""Tests for :class:`UserDAO` against the test database."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keychain.services.daos import UserDAO

pytestmark = pytest.mark.integration


async def test_create_user(db_session: AsyncSession) -> None:
    """A created user is persisted with a hashed, verifiable password."""
    dao = UserDAO(session=db_session, database_client=None)

    user = await dao.create(name="alice", password="secret123")

    assert user.id is not None
    assert user.name == "alice"
    assert user.verify_password("secret123") is True
    assert user.verify_password("wrong") is False


async def test_get_by_username(db_session: AsyncSession) -> None:
    """A user can be fetched by its username."""
    dao = UserDAO(session=db_session, database_client=None)
    await dao.create(name="bob", password="pw")

    fetched = await dao.get_by_username("bob")

    assert fetched.name == "bob"


async def test_get_all_returns_all_users(db_session: AsyncSession) -> None:
    """``get_all`` returns every user and an accurate total count."""
    dao = UserDAO(session=db_session, database_client=None)
    await dao.create(name="user-1", password="pw")
    await dao.create(name="user-2", password="pw")

    rows, total = await dao.get_all()

    assert total == 2
    assert {row.name for row in rows} == {"user-1", "user-2"}


async def test_reset_password(db_session: AsyncSession) -> None:
    """Resetting a password stores a new, verifiable hash."""
    dao = UserDAO(session=db_session, database_client=None)
    user = await dao.create(name="carol", password="old-password")

    await dao.reset_password(user.id, "new-password")

    refreshed = await dao.get_by_pk(user.id)
    assert refreshed.verify_password("new-password") is True
    assert refreshed.verify_password("old-password") is False


async def test_delete_user(db_session: AsyncSession) -> None:
    """A deleted user no longer exists in the database."""
    dao = UserDAO(session=db_session, database_client=None)
    user = await dao.create(name="dave", password="pw")

    assert await dao.delete(user.id) is True
    assert await dao.get_total() == 0
