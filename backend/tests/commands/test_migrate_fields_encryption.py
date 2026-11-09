"""Tests for :class:`MigrateFieldsEncryptionCommand` against the test database."""

import pytest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from keychain.commands import MigrateFieldsEncryptionCommand
from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import FieldDAO, InvalidPasswordError, PasswordDAO, UserDAO
from keychain.services.db_client import DBClient
from keychain.services.db_client.models.field import Field
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

pytestmark = pytest.mark.integration


async def _create_legacy_user(db_session: AsyncSession, password: str, values: list[str]) -> User:
    """Create a user whose fields are encrypted with the application-wide key and who has no keys."""
    client = CryptographyClient()
    user = await UserDAO(session=db_session, database_client=None).create(name="legacy", password=password)
    pwd = await PasswordDAO(session=db_session, database_client=None).create(name="github", user_id=user.id)
    field_dao = FieldDAO(session=db_session, database_client=None)
    for i, value in enumerate(values):
        field = await field_dao.create(
            name=f"field-{i}", value="placeholder", password_id=pwd.id, dek=user.unwrap_dek(password)
        )
        field.value = client.fernet.encrypt(value.encode()).decode()

    await db_session.execute(update(User).where(User.id == user.id).values(encryption_salt=None, wrapped_dek=None))
    await db_session.commit()
    return user


async def _user_field_values(db_session: AsyncSession, user_id: int) -> list[str]:
    """Return the stored (encrypted) field values of a user."""
    db_session.expire_all()
    stmt = select(Field.value).join(Password).where(Password.user_id == user_id).order_by(Field.id)
    return list((await db_session.execute(stmt)).scalars())


async def test_migrates_legacy_fields(db_session: AsyncSession, db_client: DBClient) -> None:
    """Legacy fields are re-encrypted with a new per-user key protected by the password."""
    user_id = (await _create_legacy_user(db_session, "pw", ["a", "b"])).id
    cmd = MigrateFieldsEncryptionCommand(db_client, user_id, "pw")

    await cmd.validate()
    migrated = await cmd.execute()

    dek = migrated.unwrap_dek("pw")
    client = CryptographyClient()
    assert [client.decrypt(v, dek) for v in await _user_field_values(db_session, user_id)] == ["a", "b"]


async def test_rejects_wrong_password(db_session: AsyncSession, db_client: DBClient) -> None:
    """A wrong password fails validation and leaves the user untouched."""
    user_id = (await _create_legacy_user(db_session, "pw", ["a"])).id
    encrypted_before = await _user_field_values(db_session, user_id)

    with pytest.raises(InvalidPasswordError):
        await MigrateFieldsEncryptionCommand(db_client, user_id, "wrong").validate()

    assert await _user_field_values(db_session, user_id) == encrypted_before


async def test_rejects_already_migrated_user(db_session: AsyncSession, db_client: DBClient) -> None:
    """A user that already has per-user keys cannot be migrated again."""
    user = await UserDAO(session=db_session, database_client=None).create(name="modern", password="pw")
    cmd = MigrateFieldsEncryptionCommand(db_client, user.id, "pw")

    with pytest.raises(ValueError, match="already uses per-user encryption"):
        await cmd.validate()
    with pytest.raises(ValueError, match="already uses per-user encryption"):
        await cmd.execute()
