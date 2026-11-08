"""Tests for :class:`FieldDAO` against the test database."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import FieldDAO, PasswordDAO, UserDAO
from keychain.services.db_client.models import Field, Password

pytestmark = pytest.mark.integration


async def test_create_and_update_encrypt_with_user_dek(db_session: AsyncSession) -> None:
    """Field values are stored encrypted with the owner's data encryption key."""
    user = await UserDAO(session=db_session, database_client=None).create(name="owner", password="pw")
    password = await PasswordDAO(session=db_session, database_client=None).create(name="github", user_id=user.id)
    field_dao = FieldDAO(session=db_session, database_client=None)
    dek = user.unwrap_dek("pw")
    client = CryptographyClient()

    field = await field_dao.create(name="login", value="alice", password_id=password.id, dek=dek)

    assert field.value != "alice"
    assert client.decrypt(field.value, dek) == "alice"

    updated = await field_dao.update(field.id, value="bob", dek=dek)

    assert client.decrypt(updated.value, dek) == "bob"


async def test_create_requires_value(db_session: AsyncSession) -> None:
    """Creating a field without a value is rejected."""
    user = await UserDAO(session=db_session, database_client=None).create(name="owner", password="pw")
    password = await PasswordDAO(session=db_session, database_client=None).create(name="github", user_id=user.id)
    field_dao = FieldDAO(session=db_session, database_client=None)

    with pytest.raises(ValueError, match="Value is required"):
        await field_dao.create(name="login", password_id=password.id, dek=user.unwrap_dek("pw"))


async def test_create_rejects_password_of_another_user(db_session: AsyncSession) -> None:
    """Creating a field on another user's password fails without writing anything."""
    user_dao = UserDAO(session=db_session, database_client=None)
    owner = await user_dao.create(name="owner", password="pw")
    intruder = await user_dao.create(name="intruder", password="pw2")
    password = await PasswordDAO(session=db_session, database_client=None).create(name="github", user_id=owner.id)
    field_dao = FieldDAO(session=db_session, database_client=None)

    with pytest.raises(NoResultFound):
        await field_dao.create(
            name="login",
            value="stolen",
            password_id=password.id,
            filters=[Password.user_id == intruder.id],
            dek=intruder.unwrap_dek("pw2"),
        )

    field_count = await db_session.scalar(select(func.count()).select_from(Field))
    assert field_count == 0
