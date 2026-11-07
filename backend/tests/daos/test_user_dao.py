"""Tests for :class:`UserDAO` against the test database."""

import pytest
from cryptography.fernet import InvalidToken
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import EncryptionKeysMissingError, FieldDAO, InvalidPasswordError, PasswordDAO, UserDAO
from keychain.services.db_client.models.field import Field
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

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
    """Resetting a password with the current one stores a new, verifiable hash."""
    dao = UserDAO(session=db_session, database_client=None)
    user = await dao.create(name="carol", password="old-password")

    await dao.reset_password(user.id, "old-password", "new-password")

    refreshed = await dao.get_by_pk(user.id)
    assert refreshed.verify_password("new-password") is True
    assert refreshed.verify_password("old-password") is False


async def test_delete_user(db_session: AsyncSession) -> None:
    """A deleted user no longer exists in the database."""
    dao = UserDAO(session=db_session, database_client=None)
    user = await dao.create(name="dave", password="pw")

    assert await dao.delete(user.id) is True
    assert await dao.get_total() == 0


async def _create_user_with_fields(db_session: AsyncSession, password: str, values: list[str]) -> tuple[User, bytes]:
    """Create a user owning one password with a field per value."""
    user = await UserDAO(session=db_session, database_client=None).create(name="erin", password=password)
    pwd = await PasswordDAO(session=db_session, database_client=None).create(name="github", user_id=user.id)
    dek = user.unwrap_dek(password)
    field_dao = FieldDAO(session=db_session, database_client=None)
    for i, value in enumerate(values):
        await field_dao.create(name=f"field-{i}", value=value, password_id=pwd.id, dek=dek)
    return user, dek


async def _user_field_values(db_session: AsyncSession, user_id: int) -> list[str]:
    """Return the stored (encrypted) field values of a user."""
    stmt = select(Field.value).join(Password).where(Password.user_id == user_id).order_by(Field.id)
    return list((await db_session.execute(stmt)).scalars())


async def test_new_user_has_encryption_keys(db_session: AsyncSession) -> None:
    """A created user gets a salt and a wrapped key that opens with their password."""
    user = await UserDAO(session=db_session, database_client=None).create(name="frank", password="pw")

    assert user.encryption_salt is not None
    assert user.wrapped_dek is not None
    assert user.unwrap_dek("pw")


async def test_reset_password_keeps_fields_readable(db_session: AsyncSession) -> None:
    """After a password change every field still decrypts with the key from the new password."""
    user, dek = await _create_user_with_fields(db_session, "old-password", ["a", "b", "c"])
    encrypted_before = await _user_field_values(db_session, user.id)

    updated = await UserDAO(session=db_session, database_client=None).reset_password(
        user.id, "old-password", "new-password"
    )

    new_dek = updated.unwrap_dek("new-password")
    assert new_dek == dek
    encrypted_after = await _user_field_values(db_session, user.id)
    assert encrypted_after == encrypted_before
    assert [CryptographyClient().decrypt(v, new_dek) for v in encrypted_after] == ["a", "b", "c"]
    with pytest.raises(InvalidToken):
        updated.unwrap_dek("old-password")


async def test_reset_password_with_wrong_old_password(db_session: AsyncSession) -> None:
    """A wrong current password is rejected and nothing changes."""
    user, _ = await _create_user_with_fields(db_session, "old-password", ["a"])
    dao = UserDAO(session=db_session, database_client=None)
    wrapped_before = user.wrapped_dek

    with pytest.raises(InvalidPasswordError):
        await dao.reset_password(user.id, "wrong", "new-password")

    refreshed = await dao.get_by_pk(user.id)
    assert refreshed.verify_password("old-password") is True
    assert refreshed.wrapped_dek == wrapped_before


async def test_force_reset_password_deletes_fields(db_session: AsyncSession) -> None:
    """A forced reset sets a new password and key and wipes the user's fields."""
    user, dek = await _create_user_with_fields(db_session, "lost-password", ["a", "b"])

    updated = await UserDAO(session=db_session, database_client=None).force_reset_password(user.id, "new-password")

    assert updated.verify_password("new-password") is True
    assert updated.unwrap_dek("new-password") != dek
    assert await _user_field_values(db_session, user.id) == []
    password_dao = PasswordDAO(session=db_session, database_client=None)
    assert await password_dao.get_total(filters=[Password.user_id == user.id]) == 1


async def test_reset_password_requires_migrated_user(db_session: AsyncSession) -> None:
    """A legacy user without encryption keys must be migrated before changing the password."""
    user, _ = await _create_user_with_fields(db_session, "old-password", ["a"])
    await db_session.execute(update(User).where(User.id == user.id).values(encryption_salt=None, wrapped_dek=None))
    await db_session.commit()
    dao = UserDAO(session=db_session, database_client=None)

    with pytest.raises(EncryptionKeysMissingError):
        await dao.reset_password(user.id, "old-password", "new-password")
