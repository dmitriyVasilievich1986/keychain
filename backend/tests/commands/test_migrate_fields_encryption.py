"""Tests for :class:`MigrateFieldsEncryptionCommand` against the Firestore emulator."""

import pytest

from keychain.commands import MigrateFieldsEncryptionCommand
from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import InvalidPasswordError, PasswordDAO, UserDAO
from keychain.services.daos.firestore.models import Field, FieldValue, User

pytestmark = pytest.mark.integration


async def _create_legacy_user(
    user_dao: UserDAO, password_dao: PasswordDAO, password: str, values: list[str]
) -> tuple[User, str]:
    """Create a user without keys whose field values use the application-wide key.

    Returns:
        tuple[User, str]: The legacy user and the ID of their password.

    """
    client = CryptographyClient()
    user = await user_dao.create(name="legacy", password=password)
    user = await user_dao.update(user.id, encryption_salt=None, wrapped_dek=None)

    pwd = await password_dao.create(name="github", user_id=user.id, fields=[])
    fields = [
        Field(
            name=f"field-{i}",
            position=i,
            values=[FieldValue(value=client.fernet.encrypt(value.encode()).decode())],
        ).model_dump()
        for i, value in enumerate(values)
    ]
    # Legacy ciphertext cannot be written through the DAO, which requires a key for field values.
    await password_dao.collection.document(pwd.id).update({"fields": fields})
    return user, pwd.id


async def _stored_values(password_dao: PasswordDAO, password_id: str) -> list[str]:
    """Return the stored (encrypted) field values of a password."""
    password = await password_dao.get_by_id(password_id)
    return [value.value for field in password.fields for value in field.values]


async def test_migrates_legacy_fields(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """Legacy fields are re-encrypted with a new per-user key protected by the password."""
    user, password_id = await _create_legacy_user(user_dao, password_dao, "pw", ["a", "b"])
    cmd = MigrateFieldsEncryptionCommand(user_dao, password_dao, user.id, "pw")

    await cmd.validate()
    migrated = await cmd.execute()

    dek = migrated.unwrap_dek("pw")
    client = CryptographyClient()
    assert [client.decrypt(v, dek) for v in await _stored_values(password_dao, password_id)] == ["a", "b"]


async def test_rejects_wrong_password(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """A wrong password fails validation and leaves the user untouched."""
    user, password_id = await _create_legacy_user(user_dao, password_dao, "pw", ["a"])
    encrypted_before = await _stored_values(password_dao, password_id)

    with pytest.raises(InvalidPasswordError):
        await MigrateFieldsEncryptionCommand(user_dao, password_dao, user.id, "wrong").validate()

    assert await _stored_values(password_dao, password_id) == encrypted_before


async def test_rejects_already_migrated_user(user_dao: UserDAO, password_dao: PasswordDAO) -> None:
    """A user that already has per-user keys cannot be migrated again."""
    user = await user_dao.create(name="modern", password="pw")
    cmd = MigrateFieldsEncryptionCommand(user_dao, password_dao, user.id, "pw")

    with pytest.raises(ValueError, match="already uses per-user encryption"):
        await cmd.validate()
    with pytest.raises(ValueError, match="already uses per-user encryption"):
        await cmd.execute()


async def test_rejects_password_dao_with_dek(user_dao: UserDAO, encrypting_password_dao: PasswordDAO) -> None:
    """The command needs raw access to the stored ciphertext."""
    with pytest.raises(ValueError, match="must not hold a data encryption key"):
        MigrateFieldsEncryptionCommand(user_dao, encrypting_password_dao, "user", "pw")
