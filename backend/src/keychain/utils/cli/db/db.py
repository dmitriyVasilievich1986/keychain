"""Database CLI commands."""

__all__ = ("db",)

import asyncclick as click

from keychain.commands import BackupDBCommand, MigrateFieldsEncryptionCommand, RestoreDBCommand
from keychain.config import AppConfig
from keychain.services.daos import InvalidPasswordError
from keychain.services.db_client.client import DBClient

from .field import field
from .password import password
from .user import user


@click.group(help="CLI for managing the database of the Keychain Application.")
def db() -> None:
    """Initialize the database CLI group for the Keychain Application.

    This function serves as the root command group for all database CLI
    operations. Subgroups build their own Firestore DAOs from the app config.

    Returns:
        None

    """


@db.command(help="Migrate a user's fields to a per-user encryption key.")
@click.option("--user-id", help="The ID of the user to migrate", required=True, type=int)
@click.option("--password", prompt="Enter the user password", help="The password of the user", hide_input=True)
@click.pass_context
async def migrate_fields_encryption(ctx: click.Context, user_id: int, password: str) -> None:
    """Migrate a legacy user's fields to their own encryption key.

    Users created before per-user encryption keys were introduced have their
    fields encrypted with the application-wide key and cannot log in until
    they are migrated. Validates and runs ``MigrateFieldsEncryptionCommand``.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        user_id (int): The unique identifier of the user to migrate.
        password (str): The current password of the user.

    Returns:
        None

    Raises:
        click.BadParameter: If the password is incorrect.
        click.UsageError: If the user is already migrated.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    cmd = MigrateFieldsEncryptionCommand(db_client, user_id, password)
    try:
        await cmd.validate()
        user = await cmd.execute()
    except InvalidPasswordError as e:
        raise click.BadParameter("Invalid password", param_hint="--password") from e
    except ValueError as e:
        raise click.UsageError(str(e)) from e

    click.echo(f"User {user.id} migrated to per-user encryption")


db.add_command(user)
db.add_command(password)
