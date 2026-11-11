"""Database CLI commands."""

__all__ = ("db",)

from uuid import UUID

import asyncclick as click

from keychain.commands import MigrateFieldsEncryptionCommand
from keychain.config import AppConfig
from keychain.services.daos import InvalidPasswordError
from keychain.utils.cli.user_dek import build_password_dao, build_user_dao

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
@click.option("--user-id", help="The ID of the user to migrate", required=True, type=click.UUID)
@click.option("--password", prompt="Enter the user password", help="The password of the user", hide_input=True)
@click.pass_context
async def migrate_fields_encryption(ctx: click.Context, user_id: UUID, password: str) -> None:
    """Migrate a legacy user's fields to their own encryption key.

    Users created before per-user encryption keys were introduced have their
    fields encrypted with the application-wide key and cannot log in until
    they are migrated. Validates and runs ``MigrateFieldsEncryptionCommand``.

    Args:
        ctx (click.Context): Click context object containing the app config.
        user_id (UUID): The unique identifier of the user to migrate.
        password (str): The current password of the user.

    Returns:
        None

    Raises:
        click.BadParameter: If the password is incorrect.
        click.UsageError: If the user is already migrated.

    """
    config: AppConfig = ctx.obj["config"]
    cmd = MigrateFieldsEncryptionCommand(build_user_dao(config), build_password_dao(config), str(user_id), password)
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
