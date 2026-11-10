"""Tests for :class:`UserDAO` against the Firestore emulator."""

import pytest
from cryptography.fernet import InvalidToken
from google.api_core.exceptions import NotFound

from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import EncryptionKeysMissingError, InvalidPasswordError, PasswordDAO, UserDAO
from keychain.services.daos.firestore.models import Field, FieldValue, User

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


async def test_delete_user(user_dao: UserDAO) -> None:
    """A deleted user no longer exists in the database."""
    user = await user_dao.create(name="dave", password="pw")

    assert await user_dao.delete(user.id) is True
    assert await user_dao.get_total() == 0


async def test_new_user_has_encryption_keys(user_dao: UserDAO) -> None:
    """A created user gets a salt and a wrapped key that opens with their password."""
    user = await user_dao.create(name="frank", password="pw")

    stored = await user_dao.get_by_id(user.id)
    assert stored.encryption_salt is not None
    assert stored.wrapped_dek is not None
    assert stored.unwrap_dek("pw") == user.unwrap_dek("pw")


async def _create_user_with_fields(
    user_dao: UserDAO, password_dao: PasswordDAO, password: str, values: list[str]
) -> tuple[User, bytes, str]:
    """Create a user owning one password with a field per value.

    Returns:
        tuple[User, bytes, str]: The user, their data encryption key and the
            ID of their password.

    """
    user = await user_dao.create(name="erin", password=password)
    dek = user.unwrap_dek(password)
    fields = [Field(name=f"field-{i}", position=i, values=[FieldValue(value=v)]) for i, v in enumerate(values)]
    keyed_dao = PasswordDAO(password_dao.firestore_client, password_dao.collection_name, dek=dek)
    pwd = await keyed_dao.create(name="github", user_id=user.id, fields=fields)
    return user, dek, pwd.id


async def _stored_values(password_dao: PasswordDAO, password_id: str) -> list[str]:
    """Return the stored (encrypted) field values of a password."""
    password = await password_dao.get_by_id(password_id)
    return [value.value for field in password.fields for value in field.values]


async def test_reset_password(user_dao: UserDAO) -> None:
    """Resetting a password with the current one stores a new, verifiable hash."""
    user = await user_dao.create(name="carol", password="old-password")

    await user_dao.reset_password(user.id, "old-password", "new-password")

    refreshed = await user_dao.get_by_id(user.id)
    assert refreshed.verify_password("new-password") is True
    assert refreshed.verify_password("old-password") is False


async def test_reset_password_keeps_fields_readable(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """After a password change every field still decrypts with the key from the new password."""
    user, dek, password_id = await _create_user_with_fields(user_dao, password_dao, "old-password", ["a", "b", "c"])
    encrypted_before = await _stored_values(password_dao, password_id)

    updated = await user_dao.reset_password(user.id, "old-password", "new-password")

    new_dek = updated.unwrap_dek("new-password")
    assert new_dek == dek
    encrypted_after = await _stored_values(password_dao, password_id)
    assert encrypted_after == encrypted_before
    assert [CryptographyClient().decrypt(v, new_dek) for v in encrypted_after] == ["a", "b", "c"]
    with pytest.raises(InvalidToken):
        updated.unwrap_dek("old-password")


async def test_reset_password_with_wrong_old_password(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """A wrong current password is rejected and nothing changes."""
    user, _, _ = await _create_user_with_fields(user_dao, password_dao, "old-password", ["a"])

    with pytest.raises(InvalidPasswordError):
        await user_dao.reset_password(user.id, "wrong", "new-password")

    refreshed = await user_dao.get_by_id(user.id)
    assert refreshed.verify_password("old-password") is True
    assert refreshed.wrapped_dek == user.wrapped_dek


async def test_force_reset_password_deletes_fields(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """A forced reset sets a new password and key and wipes the user's fields."""
    user, dek, password_id = await _create_user_with_fields(user_dao, password_dao, "lost-password", ["a", "b"])
    other = await password_dao.create(name="other", user_id="someone-else", fields=[])

    updated = await user_dao.force_reset_password(user.id, "new-password", password_dao)

    assert updated.verify_password("new-password") is True
    assert updated.unwrap_dek("new-password") != dek
    assert await _stored_values(password_dao, password_id) == []
    assert (await password_dao.get_by_id(password_id)).name == "github"
    assert (await password_dao.get_by_id(other.id)).name == "other"


async def test_reset_password_requires_migrated_user(user_dao: UserDAO) -> None:
    """A legacy user without encryption keys must be migrated before changing the password."""
    user = await user_dao.create(name="legacy", password="old-password")
    await user_dao.update(user.id, encryption_salt=None, wrapped_dek=None)

    with pytest.raises(EncryptionKeysMissingError):
        await user_dao.reset_password(user.id, "old-password", "new-password")
