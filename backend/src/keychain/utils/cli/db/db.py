"""Database CLI commands."""

__all__ = ("db",)

import asyncclick as click

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


db.add_command(user)
db.add_command(password)
