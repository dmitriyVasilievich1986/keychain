"""Shared pytest fixtures for the keychain backend test-suite.

Tests run against the Firestore emulator, never a real GCP project.
``FIRESTORE_EMULATOR_HOST`` defaults to ``localhost:8080``; start the emulator
with::

    gcloud emulators firestore start --host-port=localhost:8080

Every test gets a fresh :class:`FirestoreClient` (its gRPC channel is bound to
the test's event loop) and its own uniquely named collections, which are
emptied once the test finishes.

Environment variables are configured at import time (before any ``keychain``
module is imported) so the application settings resolve to the test
configuration.
"""

import os
import socket
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_PROJECT_ID = "keychain-test"

# These must be set before importing any ``keychain`` module, because
# configuration singletons read them on first access. The emulator host is
# always set so the Firestore client can never reach a real project.
os.environ["CONFIG_FILE_PATH"] = str(BACKEND_DIR / "configurations" / "test.yaml")
os.environ["ENVIRONMENT"] = "test"
os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
os.environ.setdefault("CRYPTOGRAPHY__SECRET_KEY", "WcrmZ43_lZNqollPA7g_Bt8pKZq2YBr69OFSjQ0V710=")
os.environ.setdefault("AUTH__JWT_SECRET_KEY", "test-secret")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402

from keychain.config import AppConfig  # noqa: E402
from keychain.config.models.db.firestore import FirestoreConfig  # noqa: E402
from keychain.config.models.google import GoogleConfig  # noqa: E402
from keychain.services.daos.firestore import PasswordDAO, UserDAO  # noqa: E402
from keychain.services.db_client.firestore import FirestoreClient  # noqa: E402
from keychain.utils.singleton import Singleton  # noqa: E402


def _reset_singletons() -> None:
    """Clear every cached singleton (settings, Firestore client, crypto client)."""
    Singleton._instances.clear()  # noqa: SLF001


@pytest.fixture(scope="session")
def app_config() -> Generator[AppConfig, None, None]:
    """Load the session-wide application config from ``test.yaml``.

    Yields:
        AppConfig: The test application config.

    """
    _reset_singletons()
    yield AppConfig.get_or_create(reload=True)
    _reset_singletons()


@pytest.fixture(scope="session")
def firestore_emulator() -> str:
    """Ensure the Firestore emulator is reachable.

    Returns:
        str: The emulator ``host:port``.

    """
    emulator_host = os.environ["FIRESTORE_EMULATOR_HOST"]
    host, _, port = emulator_host.rpartition(":")
    try:
        socket.create_connection((host, int(port)), timeout=2).close()
    except OSError:
        pytest.fail(
            f"Firestore emulator is not reachable at {emulator_host}. Start it with "
            f"`gcloud emulators firestore start --host-port={emulator_host}`.",
        )
    return emulator_host


@pytest_asyncio.fixture(loop_scope="function")
async def firestore_client(
    app_config: AppConfig,
    firestore_emulator: str,  # noqa: ARG001
) -> AsyncGenerator[FirestoreClient, None]:
    """Provide a :class:`FirestoreClient` connected to the emulator.

    Scoped per test so the async gRPC channel is created and closed on the
    event loop that uses it. Collections are uniquely named per test.

    Yields:
        FirestoreClient: Client bound to the test project.

    """
    Singleton._instances.pop(FirestoreClient, None)  # noqa: SLF001
    client = FirestoreClient(
        FirestoreConfig(
            db_name=app_config.db.firestore.db_name,
            collection_name=f"{app_config.db.firestore.collection_name}-{uuid4().hex}",
        ),
        GoogleConfig(project_id=TEST_PROJECT_ID),
    )
    yield client
    await client.close()
    Singleton._instances.pop(FirestoreClient, None)  # noqa: SLF001


async def _clear_collection(dao: UserDAO | PasswordDAO) -> None:
    """Delete every document in the DAO's collection.

    Args:
        dao (UserDAO | PasswordDAO): DAO whose collection to empty.

    """
    async for snapshot in dao.collection.stream():
        await snapshot.reference.delete()


@pytest_asyncio.fixture(loop_scope="function")
async def user_dao(app_config: AppConfig, firestore_client: FirestoreClient) -> AsyncGenerator[UserDAO, None]:
    """Provide a :class:`UserDAO` on a test-scoped users collection.

    Yields:
        UserDAO: DAO whose collection is emptied after the test.

    """
    dao = UserDAO(firestore_client, collection_name=f"{app_config.db.users.collection_name}-{uuid4().hex}")
    yield dao
    await _clear_collection(dao)


@pytest_asyncio.fixture(loop_scope="function")
async def password_dao(firestore_client: FirestoreClient) -> AsyncGenerator[PasswordDAO, None]:
    """Provide a :class:`PasswordDAO` on the client's test-scoped collection.

    Yields:
        PasswordDAO: DAO whose collection is emptied after the test.

    """
    dao = PasswordDAO(firestore_client)
    yield dao
    await _clear_collection(dao)
