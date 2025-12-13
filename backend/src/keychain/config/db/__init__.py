"""Database configuration settings."""

__all__ = ["DBConfig"]

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class DBConfig(BaseModel):
    """Application information model.

    This model stores the database configuration settings including the database
    URI and connection pool settings.

    Attributes:
        uri: The database URI. Can be set via the DATABASE_URI environment variable shortcut.
        pool_size: The maximum number of connections in the connection pool. Can be set via the POOL_SIZE environment variable shortcut.
        max_overflow: The maximum number of connections to allow beyond the pool size. Can be set via the MAX_OVERFLOW environment variable shortcut.
        pool_timeout: The number of seconds to wait before timing out a connection. Can be set via the POOL_TIMEOUT environment variable shortcut.
        pool_recycle: The number of seconds to recycle a connection. Can be set via the POOL_RECYCLE environment variable shortcut.

    """  # noqa: E501

    alembic_ini_path: Path = Field(
        Path("src/keychain/services/alembic/alembic.ini"), description="Path to the Alembic configuration file"
    )
    db_provider: Literal["sqlite", "postgresql"] = Field(default="sqlite", description="The database provider")
    db_uri: str = Field(default=":memory:", description="The database URI")

    @property
    def sqlalchemy_url(self) -> str:
        """The SQLAlchemy database URL."""
        if self.db_provider == "sqlite":
            return f"sqlite+aiosqlite:///{self.db_uri}"
        if self.db_provider == "postgresql":
            return f"postgresql+asyncpg://{self.db_uri}"
        raise ValueError(f"Invalid database provider: {self.db_provider}")

    @property
    def sync_sqlalchemy_url(self) -> str:
        """The synchronous SQLAlchemy database URL."""
        if self.db_provider == "sqlite":
            return f"sqlite:///{self.db_uri}"
        if self.db_provider == "postgresql":
            return f"postgresql://{self.db_uri}"
        raise ValueError(f"Invalid database provider: {self.db_provider}")
