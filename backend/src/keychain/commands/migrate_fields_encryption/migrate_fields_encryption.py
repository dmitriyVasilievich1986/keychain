"""Migrate a user's fields from the application-wide key to a per-user key."""

__all__ = ("MigrateFieldsEncryptionCommand",)

import structlog
from sqlalchemy import select

from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos import InvalidPasswordError, UserDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.field import Field
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

from ..base import BaseCommand

logger = structlog.stdlib.get_logger(__name__)


class MigrateFieldsEncryptionCommand(BaseCommand[User]):
    """Command that moves a legacy user to per-user field encryption.

    Users created before per-user encryption keys were introduced have no
    ``encryption_salt``/``wrapped_dek`` and their fields are encrypted with the
    application-wide secret key. This command generates the user's keys from
    their password and re-encrypts every field they own (including
    soft-deleted ones) in a single transaction. The user's password is
    required because the new key is wrapped with it.
    """

    def __init__(self, db_client: DBClient, user_id: int, password: str):
        """Initialize the migration command.

        Args:
            db_client (DBClient): The database client used to access the user
                and their fields.
            user_id (int): The unique identifier of the user to migrate.
            password (str): The user's current plaintext password.

        """
        self.db_client = db_client
        self.user_id = user_id
        self.password = password

    async def initialize(self, *args, **kwargs) -> None:
        """Initialize the migration command.

        Args:
            *args (Any): Positional arguments to initialize the command.
            **kwargs (Any): Keyword arguments to initialize the command.

        """
        pass

    async def validate(self, *_, **__) -> None:
        """Check that the user exists, still needs migration and the password is correct.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            None

        Raises:
            sqlalchemy.exc.NoResultFound: If the user does not exist.
            ValueError: If the user already has per-user encryption keys.
            InvalidPasswordError: If the password is incorrect.

        """
        user = await UserDAO(self.db_client).get_by_pk(self.user_id)
        self._validate_user(user)

    def _validate_user(self, user: User) -> None:
        """Validate that the user can be migrated with the given password.

        Args:
            user (User): The user to validate.

        Raises:
            ValueError: If the user already has per-user encryption keys.
            InvalidPasswordError: If the password is incorrect.

        """
        if user.wrapped_dek is not None:
            raise ValueError(f"User {user.id} already uses per-user encryption")

        if not user.verify_password(self.password):
            raise InvalidPasswordError("Invalid password")

    async def execute(self, *_, **__) -> User:
        """Re-encrypt the user's fields with a new per-user key.

        The user is re-validated inside the transaction, so a concurrent
        migration cannot run twice.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            User: The migrated user record.

        Raises:
            ValueError: If the user already has per-user encryption keys.
            InvalidPasswordError: If the password is incorrect.

        """
        client = CryptographyClient()

        async with self.db_client.session_factory() as session:
            user_dao = UserDAO(session=session, database_client=None)
            user = (await session.execute(select(User).where(User.id == self.user_id).with_for_update())).scalar_one()
            self._validate_user(user)

            keys = client.create_user_keys(self.password)

            fields = (await session.execute(select(Field).join(Password).where(Password.user_id == user.id))).scalars()
            migrated_count = 0
            for field in fields:
                field.value = client.encrypt(client.legacy_decrypt(field.value), keys.dek)  # ty: ignore[deprecated]
                migrated_count += 1

            user.encryption_salt = keys.salt
            user.wrapped_dek = keys.wrapped_dek
            await session.commit()

            logger.info("Migrated user fields to per-user encryption", user_id=user.id, fields=migrated_count)
            return await user_dao.get_by_pk(user.id)
