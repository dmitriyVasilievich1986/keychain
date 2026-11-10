"""Helpers for resolving a user's data encryption key in CLI commands."""

__all__ = ("build_user_dao", "load_user_dek")

import asyncclick as click

from keychain.config import AppConfig
from keychain.services.daos import UserDAO
from keychain.services.db_client.firestore import FirestoreClient


def build_user_dao(config: AppConfig) -> UserDAO:
    """Build a user DAO for the configured users collection.

    Args:
        config (AppConfig): The application config.

    Returns:
        UserDAO: The user DAO.

    """
    return UserDAO(FirestoreClient(config.db.firestore, config.google), collection_name=config.db.users.collection_name)


async def load_user_dek(user_dao: UserDAO, user_id: str, password: str) -> bytes:
    """Verify a user's password and return their data encryption key.

    Args:
        user_dao (UserDAO): The DAO used to look up the user.
        user_id (str): The unique identifier of the user.
        password (str): The user's plaintext password.

    Returns:
        bytes: The user's plaintext data encryption key.

    Raises:
        click.BadParameter: If the password is incorrect.
        click.UsageError: If the user has not been migrated to per-user
            encryption yet.

    """
    user = await user_dao.get_by_id(user_id)
    if not user.verify_password(password):
        raise click.BadParameter("Invalid user password", param_hint="--user-password")

    if not user.has_encryption_keys:
        raise click.UsageError(
            f"User {user_id} has no encryption keys. Run `keychain db migrate-fields-encryption --user-id {user_id}`."
        )

    return user.unwrap_dek(password)
