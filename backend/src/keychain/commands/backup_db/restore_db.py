"""Restore the database from a dump backup."""

__all__ = ("RestoreDBCommand",)

import asyncio
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


class RestoreDBCommand(BaseCommand[DBBackup]):
    """Command that restores the configured database from a dump backup."""

    available_db_types = ("postgresql",)

    def __init__(self, app_config: AppConfig, dump_file_path: Path | str | None = None):
        """Initialize the restore command.

        Args:
            app_config (AppConfig): Application config with database and backup settings.
            dump_file_path (Path | str | None, optional): Explicit dump file
                to restore. Defaults to None (latest backup).

        """
        self.dump_file_path = Path(dump_file_path) if dump_file_path else None
        self.db_backup_path = Path(app_config.db.backup_folder_path)
        self.app_config = app_config

    def _get_bash_command(self, backup_file_path: Path) -> tuple[list[str], dict[str, str]]:
        """Build the restore argv and env vars for the configured provider.

        Args:
            backup_file_path (Path): Path to the dump file to restore.

        Returns:
            tuple[list[str], dict[str, str]]: Command argv and process env
                overrides (for example ``PGPASSWORD``).

        Raises:
            ValueError: If the configured database provider is unsupported.

        """
        match self.app_config.db.provider:
            case "postgresql":
                return [
                    "pg_restore",
                    "-U",
                    cast(str, cast(SecretStr, self.app_config.db.user).get_secret_value()),
                    "-h",
                    self.app_config.db.host,
                    "-p",
                    str(self.app_config.db.port),
                    "-d",
                    cast(str, self.app_config.db.name),
                    "-c",
                    "--if-exists",
                    "-v",
                    str(backup_file_path),
                ], {"PGPASSWORD": cast(str, cast(SecretStr, self.app_config.db.password).get_secret_value())}
            case _:
                raise ValueError(f"Invalid database provider: {self.app_config.db.provider}")

    async def validate(self, *_, **__) -> None:
        """Validate config and resolve the backup file to restore.

        When ``backup_file_path`` is omitted, the newest matching dump in the
        backup folder is selected.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            None

        Raises:
            ValueError: If the provider is unsupported, the backup directory is
                missing, no backups are found, or the dump file is invalid.

        """
        if self.app_config.db.provider not in self.available_db_types:
            raise ValueError(f"Invalid database provider: {self.app_config.db.provider}")

        if not self.db_backup_path.is_dir() or not self.db_backup_path.exists():
            raise ValueError(f"Database backup path does not exist: {self.db_backup_path}")

        db_name = cast(str, self.app_config.db.name)
        provider = self.app_config.db.provider

        if self.dump_file_path is None:
            backup_files = find_backup_files(self.db_backup_path, provider, db_name)
            if not backup_files:
                raise ValueError(
                    f"No backup files found for provider={provider!r}, db_name={db_name!r} in {self.db_backup_path}"
                )
            self.backup_file_model = backup_files[0]
            logger.info(f"Using latest backup file: {self.backup_file_model.backup_path}")
            return
        self.backup_file_model = DBBackup.factory(self.dump_file_path)

        if not self.dump_file_path.exists() or not self.dump_file_path.is_file():
            raise ValueError(f"Backup file does not exist: {self.dump_file_path}")

    async def execute(self, *_, **__) -> DBBackup:
        """Run the restore command against the resolved dump file.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            DBBackup: Metadata for the dump that was restored.

        Raises:
            CalledProcessError: If the restore subprocess exits with a non-zero
                status.

        """
        command, env = self._get_bash_command(self.backup_file_model.backup_path)
        process = await asyncio.create_subprocess_shell(" ".join(command), env=environ | env, text=False)
        await process.wait()
        if process.returncode != 0:
            raise CalledProcessError(process.returncode or -1, " ".join(command))
        logger.info(f"Database restored from backup file: {self.backup_file_model.backup_path}")
        return self.backup_file_model
