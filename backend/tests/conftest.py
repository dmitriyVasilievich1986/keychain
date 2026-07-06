"""Shared pytest fixtures for the keychain backend test-suite.

The fixtures here spin up a dedicated PostgreSQL database (``test_db``) for the
whole test session: it is created before any test runs, migrated to ``head`` with
Alembic, and dropped once the session finishes. Every test gets a clean set of
tables via truncation between test functions.

Environment variables are configured at import time (before any ``keychain``
module is imported) so the application settings resolve to the throw-away test
database rather than a real one.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DB_NAME = "test_db"
MAINTENANCE_DB_NAME = "postgres"

# Point the settings loader at the test configuration and force the test
# database name. These must be set before importing any ``keychain`` module,
# because configuration singletons read them on first access.
os.environ["CONFIG_FILE_PATH"] = str(BACKEND_DIR / "configurations" / "test.yaml")
os.environ["DB__NAME"] = TEST_DB_NAME
os.environ.setdefault("DB__HOST", "localhost")
os.environ.setdefault("DB__PORT", "5432")
os.environ.setdefault("DB__USER", "root")
os.environ.setdefault("DB__PASSWORD", "root")
os.environ.setdefault("DB__ALEMBIC_INI_PATH", str(BACKEND_DIR / "src/keychain/services/alembic/alembic.ini"))

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.engine import URL  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402

from keychain.config import AppConfig  # noqa: E402
from keychain.services.db_client import DBClient  # noqa: E402
from keychain.utils.singleton import Singleton  # noqa: E402

# All ORM table names, ordered so a CASCADE truncate is unambiguous.
_TABLE_NAMES = ('"field"', '"password"', '"user"')


def _reset_singletons() -> None:
    """Clear every cached singleton (settings, DB client, crypto client)."""
    Singleton._instances.clear()  # noqa: SLF001


def _maintenance_url(config: AppConfig) -> URL:
    """Build a connection URL to the ``postgres`` maintenance database.

    ``CREATE DATABASE`` / ``DROP DATABASE`` cannot run against the database
    being (re)created, so we connect to the default ``postgres`` database using
    the same credentials.
    """
    db = config.db
    return URL.create(
        "postgresql+asyncpg",
        username=db.user.get_secret_value(),  # type: ignore[union-attr]
        password=db.password.get_secret_value(),  # type: ignore[union-attr]
        host=db.host,
        port=db.port,
        database=MAINTENANCE_DB_NAME,
    )


async def _create_test_database(config: AppConfig) -> None:
    """Drop any leftover test database and create a fresh one."""
    engine = create_async_engine(_maintenance_url(config), isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
            await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    finally:
        await engine.dispose()


async def _drop_test_database(config: AppConfig) -> None:
    """Drop the test database, terminating any lingering connections."""
    engine = create_async_engine(_maintenance_url(config), isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_database() -> Generator[AppConfig, None, None]:
    """Create, migrate and finally drop the ``test_db`` database.

    Runs synchronously (Alembic's ``env.py`` drives its own event loop via
    ``asyncio.run``), so it must not execute inside a running loop.
    """
    _reset_singletons()
    config = AppConfig.get_or_create(reload=True)

    asyncio.run(_create_test_database(config))

    # Store the test config so Alembic's env.py picks it up, then run migrations.
    _reset_singletons()
    AppConfig.get_or_create(reload=True)
    alembic_cfg = Config(str(config.db.alembic_ini_path))
    command.upgrade(alembic_cfg, "head")

    # env.py builds and disposes its own DBClient; start clean for the tests.
    _reset_singletons()

    yield config

    asyncio.run(_drop_test_database(config))
    _reset_singletons()


@pytest.fixture(scope="session")
def app_config(test_database: AppConfig) -> AppConfig:
    """Return the session-wide application config pointed at ``test_db``."""
    return test_database


@pytest_asyncio.fixture(loop_scope="function")
async def db_client(app_config: AppConfig) -> AsyncGenerator[DBClient, None]:
    """Provide a :class:`DBClient` bound to the test database.

    Scoped per test (and per event loop) so asyncpg connections are always
    created and torn down on the loop that uses them.
    """
    _reset_singletons()
    client = DBClient(app_config=app_config)
    yield client
    await client.close()
    _reset_singletons()


@pytest_asyncio.fixture(loop_scope="function")
async def db_session(db_client: DBClient) -> AsyncGenerator[AsyncSession, None]:
    """Yield an :class:`AsyncSession` and truncate all tables afterwards."""
    async with db_client.session_factory() as session:
        yield session

    async with db_client.session_factory() as cleanup:
        await cleanup.execute(text(f"TRUNCATE TABLE {', '.join(_TABLE_NAMES)} RESTART IDENTITY CASCADE"))
        await cleanup.commit()
