"""Tests for :class:`PasswordDAO` against the Firestore emulator."""

import pytest
from google.api_core.exceptions import NotFound

from keychain.services.cryptography import CryptographyClient
from keychain.services.daos import PasswordDAO
from keychain.services.daos.firestore.models import Field, FieldValue
from keychain.utils.filter import Filter

pytestmark = pytest.mark.integration


async def test_create_password_with_fields(encrypting_password_dao: PasswordDAO) -> None:
    """A password is stored together with its embedded fields and values."""
    password = await encrypting_password_dao.create(
        name="github",
        user_id="owner",
        fields=[
            Field(name="login", position=0, values=[FieldValue(value="me")]),
            Field(name="password", position=1, values=[FieldValue(value="old"), FieldValue(value="new")]),
        ],
    )

    stored = await encrypting_password_dao.get_by_id(password.id)
    assert stored.name == "github"
    assert stored.user_id == "owner"
    assert [field.name for field in stored.fields] == ["login", "password"]
    assert [value.value for value in stored.fields[1].values] == ["old", "new"]


async def test_field_values_are_encrypted_with_dek(
    password_dao: PasswordDAO, encrypting_password_dao: PasswordDAO, dek: bytes
) -> None:
    """Field values are stored encrypted with the owner's data encryption key."""
    password = await encrypting_password_dao.create(
        name="github",
        user_id="owner",
        fields=[Field(name="login", position=0, values=[FieldValue(value="alice")])],
    )

    raw = await password_dao.get_by_id(password.id)
    stored_value = raw.fields[0].values[0].value
    assert stored_value != "alice"
    assert CryptographyClient().decrypt(stored_value, dek) == "alice"


async def test_update_keeps_other_field_values_encrypted(
    password_dao: PasswordDAO, encrypting_password_dao: PasswordDAO, dek: bytes
) -> None:
    """Updating a password through a keyed DAO re-encrypts the fields it writes."""
    password = await encrypting_password_dao.create(name="github", user_id="owner", fields=[])

    await encrypting_password_dao.update(
        password.id, fields=[Field(name="login", position=0, values=[FieldValue(value="bob")])]
    )

    raw = await password_dao.get_by_id(password.id)
    assert CryptographyClient().decrypt(raw.fields[0].values[0].value, dek) == "bob"


async def test_writing_fields_requires_dek(password_dao: PasswordDAO) -> None:
    """A DAO without a data encryption key refuses to write field values."""
    fields = [Field(name="login", position=0, values=[FieldValue(value="alice")])]

    with pytest.raises(ValueError, match="Data encryption key is required"):
        await password_dao.create(name="github", user_id="owner", fields=fields)

    password = await password_dao.create(name="github", user_id="owner", fields=[])
    with pytest.raises(ValueError, match="Data encryption key is required"):
        await password_dao.update(password.id, fields=fields)


async def test_get_all_filters_by_user(password_dao: PasswordDAO) -> None:
    """``get_all`` applies filters to both the page and the total count."""
    await password_dao.create(name="github", user_id="alice", fields=[])
    await password_dao.create(name="gitlab", user_id="alice", fields=[])
    await password_dao.create(name="bitbucket", user_id="bob", fields=[])

    rows, total = await password_dao.get_all(
        filters=[Filter[str](column="user_id", operator="eq", value="alice")],
        sort_by="name",
    )

    assert total == 2
    assert [row.name for row in rows] == ["github", "gitlab"]


async def test_update_password(password_dao: PasswordDAO) -> None:
    """Only the given fields are changed by an update."""
    password = await password_dao.create(name="github", user_id="owner", image_url="a.png", fields=[])

    updated = await password_dao.update(password.id, name="GitHub")

    stored = await password_dao.get_by_id(password.id)
    assert updated.name == stored.name == "GitHub"
    assert stored.image_url == "a.png"


async def test_mark_as_deleted_without_dek(password_dao: PasswordDAO, encrypting_password_dao: PasswordDAO) -> None:
    """A password with encrypted fields can be soft-deleted without the owner's key."""
    password = await encrypting_password_dao.create(
        name="github",
        user_id="owner",
        fields=[Field(name="login", position=0, values=[FieldValue(value="alice")])],
    )

    await password_dao.mark_as_deleted(password.id)

    stored = await encrypting_password_dao.get_by_id(password.id)
    assert stored.deleted_at is not None
    assert stored.fields[0].values[0].value == "alice"


async def test_get_missing_password(password_dao: PasswordDAO) -> None:
    """Loading an unknown password raises ``NotFound``."""
    with pytest.raises(NotFound):
        await password_dao.get_by_id("missing")
