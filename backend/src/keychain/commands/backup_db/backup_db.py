"""Create and rotate database dump backups."""

__all__ = ("BackupDBCommand",)

from datetime import datetime
from os import environ
from pathlib import Path
from subprocess import run
from typing import cast

from loguru import logger
from pydantic import SecretStr

from keychain.config import AppConfig

from ..base import BaseCommand
from .models import DBBackup


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

    @staticmethod
    def find_backup_files(db_backup_path: Path, provider: str, db_name: str) -> list[DBBackup]:
        """Find matching dump files, newest first.

        Args:
            db_backup_path (Path): Directory to search for ``*.dump`` files.
            provider (str): Database provider used in the dump file name.
            db_name (str): Database name used in the dump file name.

        Returns:
            list[Path]: Matching backups sorted by backup time, descending.

        """
        payload: list[DBBackup] = [
            DBBackup.factory(f)
            for f in db_backup_path.glob("*.dump")
            if DBBackup.validate_file_name(f.name, provider, db_name) and f.is_file()
        ]
        return sorted(payload, key=lambda x: x.backup_time, reverse=True)

    @staticmethod
    def get_new_backup_file_model(provider: str, db_backup_path: Path, db_name: str) -> DBBackup:
        """Build metadata for a new dump named with today's date.

        Args:
            provider (str): Database provider prefix for the file name.
            db_backup_path (Path): Directory where the dump will be written.
            db_name (str): Database name used in the dump file name.

        Returns:
            DBBackup: Model pointing at the new dump path.

        """
        backup_file_name = f"{provider}_{datetime.now().strftime('%d-%m-%Y')}_{db_name}.dump"
        return DBBackup.factory(db_backup_path / backup_file_name)

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

        self.new_backup_file_model = self.get_new_backup_file_model(
            self.app_config.db.provider, self.db_backup_path, cast(str, self.app_config.db.name)
        )
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
        run(  # noqa: ASYNC221
            command,
            check=True,
            timeout=(60 * 1),
            env=environ | env,
            shell=False,
            capture_output=False,
            text=True,
        )
        logger.info(f"Backup file created: {self.new_backup_file_model.backup_path}")
        backup_files = self.find_backup_files(
            self.db_backup_path, self.app_config.db.provider, cast(str, self.app_config.db.name)
        )
        for file in backup_files[self.app_config.db.backup_count :]:
            file.backup_path.unlink()
            logger.info(f"Deleted old backup file: {file.backup_path}")

        return self.new_backup_file_model
