"""Migrate a user's fields from the application-wide key to a per-user key."""

__all__ = ("MigrateFieldsEncryptionCommand",)

from datetime import datetime, timezone

import structlog
from google.cloud.firestore_v1.base_query import FieldFilter

from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos import InvalidPasswordError, PasswordDAO, UserDAO
from keychain.services.daos.firestore.models import Field, Password, User

from ..base import BaseCommand

logger = structlog.stdlib.get_logger(__name__)


class MigrateFieldsEncryptionCommand(BaseCommand[User]):
    """Command that moves a legacy user to per-user field encryption.

    Users created before per-user encryption keys were introduced have no
    ``encryption_salt``/``wrapped_dek`` and their field values are encrypted
    with the application-wide secret key. This command generates the user's
    keys from their password and re-encrypts every field value of every
    password they own (including soft-deleted ones and the value history) in
    a single atomic batch. The user's password is required because the new
    key is wrapped with it.
    """

    def __init__(self, user_dao: UserDAO, password_dao: PasswordDAO, user_id: str, password: str):
        """Initialize the migration command.

        Args:
            user_dao (UserDAO): DAO for the users collection.
            password_dao (PasswordDAO): DAO for the passwords collection. It
                must not hold a data encryption key, so it reads the stored
                ciphertext as is.
            user_id (str): The unique identifier of the user to migrate.
            password (str): The user's current plaintext password.

        Raises:
            ValueError: If ``password_dao`` holds a data encryption key, or if
                users and passwords live in different databases, since the
                migration must write both in one atomic batch.

        """
        if password_dao.dek is not None:
            raise ValueError("The password DAO must not hold a data encryption key")

        if not user_dao.firestore_client.is_same_database(password_dao.firestore_client):
            raise ValueError("Users and passwords must live in the same database to be migrated atomically")

        self.user_dao = user_dao
        self.password_dao = password_dao
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
            NotFound: If the user does not exist.
            ValueError: If the user already has per-user encryption keys.
            InvalidPasswordError: If the password is incorrect.

        """
        self._validate_user(await self.user_dao.get_by_id(self.user_id))

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

    @staticmethod
    def _reencrypt_field(field: Field, client: CryptographyClient, dek: bytes) -> Field:
        """Re-encrypt every value of a field from the legacy key to ``dek``.

        Args:
            field (Field): The field with values encrypted by the legacy key.
            client (CryptographyClient): Client used for the conversion.
            dek (bytes): The user's new data encryption key.

        Returns:
            Field: A copy of the field with every value encrypted by ``dek``.

        Raises:
            cryptography.fernet.InvalidToken: If a value was not encrypted with
                the application-wide key.

        """
        values = [
            value.model_copy(
                update={"value": client.encrypt(client.legacy_decrypt(value.value), dek)}  # ty: ignore[deprecated]
            )
            for value in field.values
        ]
        return field.model_copy(update={"values": values})

    async def execute(self, *_, **__) -> User:
        """Re-encrypt the user's field values with a new per-user key.

        The user is re-validated right before writing. Every value is
        converted before anything is written, so a value that cannot be
        decrypted aborts the migration without changes.

        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.

        Returns:
            User: The migrated user.

        Raises:
            NotFound: If the user does not exist.
            ValueError: If the user already has per-user encryption keys.
            InvalidPasswordError: If the password is incorrect.
            cryptography.fernet.InvalidToken: If a stored value was not
                encrypted with the application-wide key.

        """
        client = CryptographyClient()
        user = await self.user_dao.get_by_id(self.user_id)
        self._validate_user(user)

        keys = client.create_user_keys(self.password)
        now = datetime.now(timezone.utc)
        batch = self.user_dao.firestore_client.client.batch()

        snapshots = await self.password_dao.collection.where(filter=FieldFilter("user_id", "==", user.id)).get()
        migrated_count = 0
        for snapshot in snapshots:
            password: Password = self.password_dao.to_model(snapshot)
            fields = [self._reencrypt_field(field, client, keys.dek) for field in password.fields]
            migrated_count += sum(len(field.values) for field in fields)
            batch.update(snapshot.reference, {"fields": [field.model_dump() for field in fields], "updated_at": now})

        batch.update(
            self.user_dao.collection.document(user.id),
            {"encryption_salt": keys.salt, "wrapped_dek": keys.wrapped_dek, "updated_at": now},
        )
        await batch.commit()

        logger.info("Migrated user fields to per-user encryption", user_id=user.id, values=migrated_count)
        return await self.user_dao.get_by_id(user.id)
