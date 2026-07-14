"""Create and rotate database dump backups."""

__all__ = ("BackupDBCommand",)

import asyncio
from datetime import datetime
from os import environ
from pathlib import Path
from subprocess import CalledProcessError
from typing import cast

from loguru import logger
from pydantic import SecretStr

from keychain.config import AppConfig

from ..base import BaseCommand
from .models import DBBackup
from .utils import find_backup_files


class BackupDBCommand(BaseCommand[DBBackup]):
    """Command that dumps the configured database and prunes old backups."""

    available_db_types = ("postgresql",)

    def __init__(self, app_config: AppConfig):
        """Initialize the backup command.

        Args:
            app_config (AppConfig): Application config with database and backup settings.

        """
        self.db_backup_path = Path(app_config.db.backup_folder_path)
        self.backup_count = app_config.db.backup_count
        self.app_config = app_config

    def _get_bash_command(self, backup_file_path: Path) -> tuple[list[str], dict[str, str]]:
        """Build the dump argv and env vars for the configured provider.

        Args:
            backup_file_path (Path): Destination path for the dump file.

        Returns:
            tuple[list[str], dict[str, str]]: Command argv and process env
                overrides (for example ``PGPASSWORD``).

        Raises:
            ValueError: If the configured database provider is unsupported.

        """
        match self.app_config.db.provider:
            case "postgresql":
                return [
                    "pg_dump",
                    "-U",
                    cast(str, cast(SecretStr, self.app_config.db.user).get_secret_value()),
                    "-h",
                    self.app_config.db.host,
                    "-p",
                    str(self.app_config.db.port),
                    "-d",
                    cast(str, self.app_config.db.name),
                    "-Fc",
                    "-b",
                    "-v",
                    "-f",
                    str(backup_file_path),
                ], {"PGPASSWORD": cast(str, cast(SecretStr, self.app_config.db.password).get_secret_value())}
            case _:
                raise ValueError(f"Invalid database provider: {self.app_config.db.provider}")

    async def validate(self, *_, **__) -> None:
        """Validate config and prepare backup paths to create or delete.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            None

        Raises:
            ValueError: If the provider is unsupported or the backup directory
                is missing.

        """
        if self.app_config.db.provider not in self.available_db_types:
            raise ValueError(f"Invalid database provider: {self.app_config.db.provider}")

        if not self.db_backup_path.is_dir() or not self.db_backup_path.exists():
            raise ValueError(f"Database backup path does not exist: {self.db_backup_path}")

        db_name = cast(str, self.app_config.db.name)
        new_backup_file_name = f"{self.app_config.db.provider}_{datetime.now().strftime('%d-%m-%Y')}_{db_name}.dump"
        self.new_backup_file_model = DBBackup.factory(self.db_backup_path / new_backup_file_name)
        if self.new_backup_file_model.backup_path.exists():
            logger.warning(
                f"Backup file already exists: {self.new_backup_file_model.backup_path}, will be overwritten."
            )

    async def execute(self, *_, **__) -> DBBackup:
        """Run the dump command and remove backups beyond the retention limit.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            DBBackup: Metadata for the newly created dump.

        Raises:
            CalledProcessError: If the dump subprocess exits with a non-zero
                status.

        """
        command, env = self._get_bash_command(self.new_backup_file_model.backup_path)
        process = await asyncio.create_subprocess_shell(" ".join(command), env=environ | env, text=False)
        await process.wait()
        if process.returncode != 0:
            raise CalledProcessError(process.returncode or -1, " ".join(command))
        logger.info(f"Backup file created: {self.new_backup_file_model.backup_path}")
        backup_files = find_backup_files(
            self.db_backup_path, self.app_config.db.provider, cast(str, self.app_config.db.name)
        )
        for file in backup_files[self.app_config.db.backup_count :]:
            file.backup_path.unlink()
            logger.info(f"Deleted old backup file: {file.backup_path}")

        return self.new_backup_file_model
