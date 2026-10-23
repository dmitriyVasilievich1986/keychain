"""Tests for :class:`PasswordDAO` against the Firestore emulator."""

import pytest
from google.api_core.exceptions import NotFound

from keychain.services.daos import PasswordDAO
from keychain.services.daos.firestore.models import Field, FieldValue
from keychain.utils.filter import Filter

pytestmark = pytest.mark.integration


async def test_create_password_with_fields(password_dao: PasswordDAO) -> None:
    """A password is stored together with its embedded fields and values."""
    password = await password_dao.create(
        name="github",
        user_id="owner",
        fields=[
            Field(name="login", position=0, values=[FieldValue(value="me")]),
            Field(name="password", position=1, values=[FieldValue(value="old"), FieldValue(value="new")]),
        ],
    )

    stored = await password_dao.get_by_id(password.id)
    assert stored.name == "github"
    assert stored.user_id == "owner"
    assert [field.name for field in stored.fields] == ["login", "password"]
    assert [value.value for value in stored.fields[1].values] == ["old", "new"]


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


async def test_get_missing_password(password_dao: PasswordDAO) -> None:
    """Loading an unknown password raises ``NotFound``."""
    with pytest.raises(NotFound):
        await password_dao.get_by_id("missing")
