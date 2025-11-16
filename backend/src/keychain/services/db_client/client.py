"""Base database client for async database operations."""

__all__ = ["DBClient"]

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Self

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine

from keychain.config import AppConfig
from keychain.utils import Singleton


class DBClient(metaclass=Singleton):
    """Base database client for async database operations."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize the database client.

        Args:
            config: The application configuration. If None, the default configuration will be used.

        """
        self.config = config or AppConfig.get_or_create()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create the async database engine.

        Returns:
            The async SQLAlchemy engine instance.

        Raises:
            RuntimeError: If the engine has been closed.

        """
        if self._engine is None:
            raise RuntimeError("Database engine has not been initialized. Call initialize() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create the session factory.

        Returns:
            The async session factory instance.

        Raises:
            RuntimeError: If the session factory has not been initialized.

        """
        if self._session_factory is None:
            raise RuntimeError("Session factory has not been initialized. Call initialize() first.")
        return self._session_factory

    async def initialize(self) -> None:
        """Initialize the database engine and session factory.

        This method should be called before using the database client.
        It creates the async engine and session factory based on the configuration.

        """
        if self._engine is not None:
            return

        connect_args = {}

        # SQLite-specific async configuration
        if self.config.db.db_provider == "sqlite":
            connect_args = {"check_same_thread": False}

        self._engine = create_async_engine(
            self.config.db.sqlalchemy_url,
            echo=False,  # Set to True for SQL query logging
            connect_args=connect_args,
            pool_pre_ping=True,  # Verify connections before using them
        )
        self._session_factory = async_sessionmaker[AsyncSession](
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create an async database session context manager.

        Yields:
            An async database session that will be automatically committed
            on successful completion or rolled back on exception.

        Example:
            ```python
            async with db_client.session() as session:
                result = await session.execute(select(User))
                users = result.scalars().all()
            ```

        """
        if self._session_factory is None:
            await self.initialize()

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close the database engine and cleanup resources.

        This method should be called when the database client is no longer needed,
        typically during application shutdown.

        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Returns:
            The database client instance.

        """
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        """
        await self.close()
