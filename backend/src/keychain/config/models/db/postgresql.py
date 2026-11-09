"""PostgreSQL database configuration settings."""

__all__ = ("PostgresqlConfig",)

from typing import Literal
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class PostgresqlConfig(BaseModel):
    """PostgreSQL database configuration model.

    This model stores the database configuration settings including the database
    URI and connection pool settings.

    Attributes:
        provider: The database provider.
        host: The database host.
        port: The database port.
        name: The database name.
        user: The database user.
        password: The database password.
        backup_folder_path: The path to the backup folder.
        backup_count: The number of backups to keep.

    """

    provider: Literal["postgresql+asyncpg"] = Field("postgresql+asyncpg", description="The database provider")
    port: int = Field(5432, description="The port of the database")
    host: str = Field(..., description="The database URI")
    name: str = Field(..., description="The name of the database")
    user: SecretStr = Field(..., description="The user of the database")
    password: SecretStr = Field(..., description="The password of the database")

    @property
    def sqlalchemy_uri(self) -> str:
        """The SQLAlchemy database URL."""
        return URL.create(
            "postgresql+asyncpg",
            username=quote_plus(self.user.get_secret_value()),
            password=quote_plus(self.password.get_secret_value()),
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)
