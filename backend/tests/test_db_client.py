"""Tests for the database client against the migrated test database."""

import pytest
from sqlalchemy import text

from keychain.services.db_client import DBClient

pytestmark = pytest.mark.integration


async def test_healthcheck_succeeds(db_client: DBClient) -> None:
    """A healthy connection to the test database returns ``True``."""
    assert await db_client.healthcheck() is True


async def test_migrations_created_tables(db_client: DBClient) -> None:
    """Alembic migrations should have created the core application tables."""
    async with db_client.session_factory() as session:
        result = await session.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'",
            ),
        )
        tables = {row[0] for row in result.all()}

    assert {"user", "password", "field"}.issubset(tables)
