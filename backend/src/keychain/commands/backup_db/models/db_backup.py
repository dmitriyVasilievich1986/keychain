"""Database backup metadata model."""

__all__ = ("DBBackup",)

import re
from datetime import datetime
from pathlib import Path
from typing import cast, Literal, Self

from pydantic import BaseModel, Field


class DBBackup(BaseModel):
    """Metadata describing a created database backup.

    Attributes:
        backup_path: The path to the database backup file.
        backup_time: The time the backup was created.
        db_name: The name of the database that was backed up.
        db_type: The type of database that was backed up.

    """

    backup_path: Path = Field(..., description="The path to the database backup")
    backup_time: datetime = Field(..., description="The time the backup was created")
    db_name: str = Field(..., description="The name of the database")
    db_type: Literal["postgresql"] = Field(..., description="The type of database")

    @staticmethod
    def validate_file_name(file_name: str, provider: str | None = None, db_name: str | None = None) -> bool:
        """Check whether a backup file name matches the expected pattern.

        Expected format is ``{provider}_{DD-MM-YYYY}_{db_name}.dump``.

        Args:
            file_name (str): The backup file name to validate.
            provider (str | None, optional): Expected database provider segment.
                When omitted, any non-empty segment is accepted. Defaults to None.
            db_name (str | None, optional): Expected database name segment.
                When omitted, any non-empty segment is accepted. Defaults to None.

        Returns:
            bool: True if the file name matches the pattern, otherwise False.

        """
        provider_ = provider or r".+?"
        db_name_ = db_name or r".+?"
        return re.match(rf"^{provider_}_\d{{2}}-\d{{2}}-\d{{4}}_{db_name_}\.dump$", file_name) is not None

    @classmethod
    def factory(cls, file_path: Path) -> Self:
        """Build a ``DBBackup`` instance by parsing a backup file path.

        Args:
            file_path (Path): Path to a backup dump file whose name follows
                the expected naming convention.

        Returns:
            Self: A populated ``DBBackup`` instance.

        Raises:
            ValueError: If the file name does not match the expected pattern.

        """
        if not cls.validate_file_name(file_path.name):
            raise ValueError(f"Invalid backup file name: {file_path.name}")

        db_type, backup_date, db_name = file_path.name.split("_", maxsplit=2)

        return cls(
            backup_path=file_path,
            backup_time=datetime.strptime(backup_date, "%d-%m-%Y"),
            db_name=re.sub(r"\.dump$", "", db_name),
            db_type=cast(Literal["postgresql"], db_type),
        )
