"""Async Firestore client management for the application."""

__all__ = ("FirestoreClient", "PasswordsFirestoreClient", "UsersFirestoreClient")

import asyncio

import structlog
from google.cloud.firestore import AsyncClient, AsyncCollectionReference

from keychain.config.models.db.firestore import FirestoreConfig
from keychain.config.models.google import GoogleConfig
from keychain.utils.singleton import Singleton

logger = structlog.stdlib.get_logger(__name__)


class FirestoreClient(metaclass=Singleton):
    """Singleton that owns the async Firestore client for one database.

    The singleton is cached per class, so each subclass bound to a different
    database (see :class:`UsersFirestoreClient` and
    :class:`PasswordsFirestoreClient`) gets its own instance.
    """

    _client: AsyncClient
    _collection_name: str
    _project_id: str
    _db_name: str
    _healthcheck_timeout_seconds: float = 5.0

    def __init__(
        self,
        firestore_config: FirestoreConfig | None = None,
        google_config: GoogleConfig | None = None,
    ) -> None:
        """Build the async Firestore client from app configuration.

        Construction is synchronous: the gRPC channel is opened lazily on the
        first request, so this is safe to call from inside or outside an
        event loop.

        Args:
            firestore_config (FirestoreConfig | None): Firestore database and
                collection names. Defaults to None.
            google_config (GoogleConfig | None): Google project ID and
                service-account credentials. Defaults to None.

        Returns:
            None

        Raises:
            RuntimeError: If ``firestore_config`` or ``google_config`` is None.

        """
        if firestore_config is None or google_config is None:
            raise RuntimeError("Firestore and Google configs are required")

        logger.info(
            "Initializing Firestore client",
            project_id=google_config.project_id,
            database=firestore_config.db_name,
        )

        self._client = AsyncClient(
            project=google_config.project_id,
            credentials=google_config.credentials,
            database=firestore_config.db_name,
        )
        self._collection_name = firestore_config.collection_name
        self._project_id = google_config.project_id
        self._db_name = firestore_config.db_name
        logger.info("Firestore client initialized successfully.")

    @property
    def client(self) -> AsyncClient:
        """Return the shared async Firestore client.

        Returns:
            AsyncClient: The configured client instance.

        """
        return self._client

    @property
    def collection(self) -> AsyncCollectionReference:
        """Return a reference to the configured collection.

        Returns:
            AsyncCollectionReference: Reference to ``collection_name``.

        """
        return self._client.collection(self._collection_name)

    @property
    def database_path(self) -> str:
        """Return the resource path of the database this client talks to.

        Returns:
            str: ``projects/<project_id>/databases/<db_name>``.

        """
        return f"projects/{self._project_id}/databases/{self._db_name}"

    def is_same_database(self, other: "FirestoreClient") -> bool:
        """Check whether another client talks to the same Firestore database.

        Writes to several collections can only share one batch or transaction
        when the collections live in the same database.

        Args:
            other (FirestoreClient): The client to compare with.

        Returns:
            bool: True if both clients use the same project and database.

        """
        return self.database_path == other.database_path

    async def close(self) -> None:
        """Close the gRPC channel and release client resources.

        ``AsyncClient.close()`` only closes the HTTP session, so the async
        gRPC transport is closed explicitly as well.

        Returns:
            None

        """
        await self._client._firestore_api.transport.close()  # noqa: SLF001
        self._client.close()
        logger.info("Firestore client closed successfully.")

    async def healthcheck(self) -> bool:
        """Read at most one document to verify Firestore is reachable.

        The read is bounded by ``HEALTHCHECK_TIMEOUT_SECONDS`` so an unreachable
        backend fails fast instead of waiting on gRPC retries.

        Returns:
            bool: True if the read succeeds, False on any error.

        """
        try:
            async with asyncio.timeout(self._healthcheck_timeout_seconds):
                await self.collection.limit(1).get()
        except TimeoutError:
            logger.error("Firestore health check timed out", timeout_seconds=self._healthcheck_timeout_seconds)
            return False
        except Exception as e:
            logger.error("Firestore health check failed", error=str(e))
            return False

        return True


class UsersFirestoreClient(FirestoreClient):
    """Singleton Firestore client for the database holding user documents."""


class PasswordsFirestoreClient(FirestoreClient):
    """Singleton Firestore client for the database holding password documents."""
