"""Database configuration settings."""

__all__ = ["DBConfig"]

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class DBConfig(BaseModel):
    """Application information model.

    This model stores the database configuration settings including the database
    URI and connection pool settings.

    Attributes:
        alembic_ini_path: The path to the Alembic configuration file.
        provider: The database provider.
        host: The database host.
        port: The database port.
        name: The database name.
        user: The database user.
        password: The database password.

    """  # noqa: E501

    alembic_ini_path: Path = Field(..., description="Path to the Alembic configuration file")
    provider: Literal["sqlite", "postgresql"] = Field(..., description="The database provider")
    host: str = Field(..., description="The database URI")

    port: int | None = Field(None, description="The port of the database")
    name: str | None = Field(None, description="The name of the database")
    user: SecretStr | None = Field(None, description="The user of the database")
    password: SecretStr | None = Field(None, description="The password of the database")

    @property
    def sqlalchemy_uri(self) -> str:
        """The SQLAlchemy database URL."""
        match self.provider:
            case "sqlite":
                return URL.create("sqlite+aiosqlite", database=self.host)
            case "postgresql":
                if not all((self.user, self.password, self.name)):
                    raise ValueError("User, password and name are required for PostgreSQL")
                return URL.create(
                    "postgresql+asyncpg",
                    username=self.user.get_secret_value(),  # type: ignore[union-attr]
                    password=self.password.get_secret_value(),  # type: ignore[union-attr]
                    host=self.host,
                    port=self.port,
                    database=self.name,
                )
            case _:
                raise ValueError(f"Invalid database provider: {self.provider}")
