"""Helpers for resolving a user's data encryption key in CLI commands."""

__all__ = ("load_user_dek",)

import asyncclick as click

from keychain.services.daos import UserDAO
from keychain.services.db_client.client import DBClient


async def load_user_dek(db_client: DBClient, user_id: int, password: str) -> bytes:
    """Verify a user's password and return their data encryption key.

    Args:
        db_client (DBClient): The database client used to look up the user.
        user_id (int): The unique identifier of the user.
        password (str): The user's plaintext password.

    Returns:
        bytes: The user's plaintext data encryption key.

    Raises:
        click.BadParameter: If the password is incorrect.
        click.UsageError: If the user has not been migrated to per-user
            encryption yet.

    """
    user_dao = UserDAO(db_client)
    user = await user_dao.get_by_pk(user_id)
    if not user.verify_password(password):
        raise click.BadParameter("Invalid user password", param_hint="--user-password")

    if user.wrapped_dek is None:
        raise click.UsageError(
            f"User {user_id} has no encryption keys. Run `keychain db migrate-fields-encryption --user-id {user_id}`."
        )

    return user.unwrap_dek(password)
