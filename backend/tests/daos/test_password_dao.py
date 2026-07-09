"""Tests for :class:`PasswordDAO` against the test database."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keychain.services.daos import PasswordDAO, UserDAO

pytestmark = pytest.mark.integration


async def test_create_password_for_user(db_session: AsyncSession) -> None:
    """A password is created and linked to its owning user."""
    user = await UserDAO(session=db_session, database_client=None).create(name="owner", password="pw")
    password_dao = PasswordDAO(session=db_session, database_client=None)

    password = await password_dao.create(name="github", user_id=user.id)

    assert password.id is not None
    assert password.name == "github"
    assert password.user_id == user.id
    assert password.image_url == "/static/i/no-photo.png"


async def test_get_all_passwords(db_session: AsyncSession) -> None:
    """``get_all`` returns the created passwords with an accurate total."""
    user = await UserDAO(session=db_session, database_client=None).create(name="owner", password="pw")
    password_dao = PasswordDAO(session=db_session, database_client=None)
    await password_dao.create(name="github", user_id=user.id)
    await password_dao.create(name="gitlab", user_id=user.id)

    rows, total = await password_dao.get_all()

    assert total == 2
    assert {row.name for row in rows} == {"github", "gitlab"}
