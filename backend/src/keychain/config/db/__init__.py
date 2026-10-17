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
        backup_folder_path: The path to the backup folder.
        backup_count: The number of backups to keep.

    """

    alembic_ini_path: Path = Field(..., description="Path to the Alembic configuration file")
    provider: Literal["postgresql"] = Field(..., description="The database provider")
    host: str = Field(..., description="The database URI")

    port: int | None = Field(None, description="The port of the database")
    name: str | None = Field(None, description="The name of the database")
    user: SecretStr | None = Field(None, description="The user of the database")
    password: SecretStr | None = Field(None, description="The password of the database")

    backup_folder_path: Path = Field(..., description="The path to the backup folder")
    backup_count: int = Field(5, description="The number of backups to keep")

    @property
    def sqlalchemy_uri(self) -> str:
        """The SQLAlchemy database URL."""
        match self.provider:
            case "sqlite":
                return URL.create("sqlite+aiosqlite", database=self.host).render_as_string(hide_password=False)
            case "postgresql":
                if self.user is None or self.password is None or self.name is None:
                    raise ValueError("User, password and name are required for PostgreSQL")
                return URL.create(
                    "postgresql+asyncpg",
                    username=self.user.get_secret_value(),
                    password=self.password.get_secret_value(),
                    host=self.host,
                    port=self.port,
                    database=self.name,
                ).render_as_string(hide_password=False)
            case _:
                raise ValueError(f"Invalid database provider: {self.provider}")
