"""Database configuration settings."""

__all__ = ("DBConfig",)

from pathlib import Path

from pydantic import BaseModel, Field

from .postgresql import PostgresqlConfig


class DBConfig(BaseModel):
    """Database configuration model.

    This model stores the database configuration settings including the database
    URI and connection pool settings.

    Attributes:
        postgresql: PostgreSQL database configuration.
        alembic_ini_path: The path to the Alembic configuration file.
        backup_folder_path: The path to the backup folder.
        backup_count: The number of backups to keep.

    """

    alembic_ini_path: Path = Field(..., description="Path to the Alembic configuration file")
    backup_folder_path: Path = Field(..., description="The path to the backup folder")
    backup_count: int = Field(5, description="The number of backups to keep")

    postgresql: PostgresqlConfig = Field(..., description="PostgreSQL database configuration")
