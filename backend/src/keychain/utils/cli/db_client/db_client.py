"""CLI for managing the database of the Keychain Application."""

__all__ = ["db_client"]


import click

from keychain.config import AppConfig
from keychain.services.db_client.client import DBClient

from .field import field
from .password import password
from .user import user


@click.group(help="CLI for managing the database of the Keychain Application.")
@click.pass_context
def db_client(ctx: click.Context) -> None:
    """Initialize the database CLI group for the Keychain Application.

    This function serves as the root command group for all database CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.
    """
    ctx.ensure_object(dict)
    config = AppConfig.get_or_create()
    ctx.obj["db_client_instance"] = DBClient(config)


db_client.add_command(user)
db_client.add_command(password)
db_client.add_command(field)
