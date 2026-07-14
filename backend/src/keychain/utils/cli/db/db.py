"""Database CLI commands."""

__all__ = ("db",)

import asyncio
from pathlib import Path

import asyncclick as click
from alembic import command
from alembic.config import Config

from keychain.commands import BackupDBCommand, RestoreDBCommand
from keychain.config import AppConfig
from keychain.services.db_client.client import DBClient

from .field import field
from .password import password
from .user import user


@click.group(help="CLI for managing the database of the Keychain Application.")
@click.pass_context
def db(ctx: click.Context) -> None:
    """Initialize the database CLI group for the Keychain Application.

    This function serves as the root command group for all database CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.

    Args:
        ctx: Click context object for sharing data between commands.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    alembic_cfg = Config(config.db.alembic_ini_path)
    ctx.obj["alembic_cfg"] = alembic_cfg
    ctx.obj["db_client_instance"] = DBClient(app_config=config)


@db.command()
@click.pass_context
async def current(ctx: click.Context) -> None:
    """Display the current database revision.

    Retrieves the current database revision from the Alembic configuration and displays
    it in a user-friendly format.

    Args:
        ctx: Click context object containing the Alembic configuration.

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    await asyncio.to_thread(command.current, alembic_cfg)


@db.command()
@click.option(
    "--revision",
    default="head",
    help="The target revision to upgrade to. Use 'head' to upgrade to the latest revision.",
)
@click.pass_context
async def upgrade(ctx: click.Context, revision: str) -> None:
    """Upgrade the database to a specific revision.

    Applies pending migrations to upgrade the database schema to the specified
    revision. If no revision is specified, upgrades to the latest (head) revision.

    Args:
        ctx: Click context object containing the Alembic configuration.
        revision: The target revision identifier (e.g., 'head', 'abc123', '+1').

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    await asyncio.to_thread(command.upgrade, alembic_cfg, revision)


@db.command()
@click.option(
    "--revision",
    required=True,
    help="The target revision to downgrade to. Use '-1' to downgrade one revision, or a specific revision ID.",
)
@click.pass_context
async def downgrade(ctx: click.Context, revision: str) -> None:
    """Downgrade the database to a specific revision.

    Reverts database migrations to downgrade the schema to the specified revision.
    This operation will undo the changes made by migrations.

    Args:
        ctx: Click context object containing the Alembic configuration.
        revision: The target revision identifier (e.g., '-1', 'abc123', 'base').

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    await asyncio.to_thread(command.downgrade, alembic_cfg, revision)


@db.command()
@click.option(
    "--backup-folder-path",
    required=False,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    help="The directory where the dump file will be written.",
)
@click.option(
    "--backup-count",
    required=False,
    type=int,
    default=None,
    help="The number of backups to keep. If not specified, the default backup count will be used.",
)
@click.option(
    "--db-name",
    required=False,
    default=None,
    type=str,
    help="The name of the database to backup.",
)
@click.pass_context
async def backup(
    ctx: click.Context, backup_folder_path: str | None, backup_count: int | None, db_name: str | None
) -> None:
    """Create a database dump and prune older backups.

    Overrides the app config backup settings with the provided CLI options,
    then validates and runs ``BackupDBCommand``.

    Args:
        ctx (click.Context): Click context object containing the app config.
        backup_folder_path (str): Directory where the dump file will be written.
        backup_count (int | None): Maximum number of backup files to retain.
            If not specified, the default backup count will be used.
        db_name (str | None): The name of the database to backup.

    Returns:
        None

    """
    app_config: AppConfig = ctx.obj["config"]
    if backup_folder_path is not None:
        app_config.db.backup_folder_path = Path(backup_folder_path)
    if db_name is not None:
        app_config.db.name = db_name
    if backup_count is not None:
        app_config.db.backup_count = backup_count
    cmd = BackupDBCommand(app_config)
    await cmd.validate()
    await cmd.execute()


@db.command()
@click.option(
    "--backup-folder-path",
    required=False,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="The directory that contains database dump backups.",
)
@click.option(
    "--backup-file-path",
    required=False,
    default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Specific dump file to restore. If omitted, the latest matching backup is used.",
)
@click.option(
    "--db-name",
    required=False,
    default=None,
    type=str,
    help="The name of the database to restore.",
)
@click.pass_context
async def restore(
    ctx: click.Context, backup_folder_path: str | None, backup_file_path: str | None, db_name: str | None
) -> None:
    """Restore the database from a dump backup.

    Overrides the app config backup folder with the provided CLI option,
    then validates and runs ``RestoreDBCommand``.

    Args:
        ctx (click.Context): Click context object containing the app config.
        backup_folder_path (str): Directory that contains dump backups.
        backup_file_path (str | None): Optional explicit dump file to restore.
        db_name (str | None): The name of the database to restore.

    Returns:
        None

    """
    app_config: AppConfig = ctx.obj["config"]
    if backup_folder_path is not None:
        app_config.db.backup_folder_path = Path(backup_folder_path)
    if db_name is not None:
        app_config.db.name = db_name
    cmd = RestoreDBCommand(app_config, dump_file_path=backup_file_path)
    await cmd.validate()
    await cmd.execute()


db.add_command(user)
db.add_command(password)
db.add_command(field)
