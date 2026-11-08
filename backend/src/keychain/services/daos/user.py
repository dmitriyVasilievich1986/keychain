"""Data access object for user records."""

__all__ = ("EncryptionKeysMissingError", "InvalidPasswordError", "UserDAO")

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement
from werkzeug.security import generate_password_hash

from keychain.services.cryptography.client import CryptographyClient
from keychain.services.db_client.models.field import Field
from keychain.services.db_client.models.password import Password
from keychain.services.db_client.models.user import User

from .base import BaseDAO
from .exceptions import EncryptionKeysMissingError, InvalidPasswordError


class UserDAO(BaseDAO[User]):
    """Data access object providing user-specific database operations."""

    pk_column_name: str = "id"
    database_model: type[User] = User

    get_all_columns = (User.id, User.name)
    select_in_options_single = (User.passwords,)

    async def get_by_username(self, username: str, filters: Sequence[ColumnElement[bool]] | None = None) -> User:
        """Retrieve a user by their username.

        Args:
            username (str): The username to look up (matched against the
                ``name`` column).
            filters (Sequence[ColumnElement[bool]], optional): Additional SQL
                filters to apply. Defaults to None.

        Returns:
            User: The user matching the given username.

        """
        if self.session is not None:
            return await self._get_by_pk_raw(self.session, username, "name", filters)

        async with self._session_factory() as session:
            return await self._get_by_pk_raw(session, username, "name", filters)

    async def _reset_password_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        old_password: str,
        new_password: str,
        pk_column_name: str,
        filters: Sequence[ColumnElement[bool]] | None,
    ) -> User:
        """Change a user's password and re-wrap their key on the given session.

        Args:
            session (AsyncSession): The database session to use.
            pk (int | str): The primary key value identifying the user.
            old_password (str): The user's current plaintext password.
            new_password (str): The new plaintext password.
            pk_column_name (str): The column to match ``pk`` against.
            filters (Sequence[ColumnElement[bool]] | None): Additional SQL
                filters to apply.

        Returns:
            User: The updated user record.

        Raises:
            InvalidPasswordError: If ``old_password`` is incorrect.
            EncryptionKeysMissingError: If the user has not been migrated to
                per-user encryption yet.

        """
        user = await self._get_by_pk_raw(session, pk, pk_column_name, filters)
        if not user.verify_password(old_password):
            raise InvalidPasswordError("Invalid password")

        if user.encryption_salt is None or user.wrapped_dek is None:
            raise EncryptionKeysMissingError(f"User {user.id} has no encryption keys, migrate the user first")

        keys = CryptographyClient().rewrap_dek(old_password, new_password, user.encryption_salt, user.wrapped_dek)
        user.password_hash = generate_password_hash(new_password)
        user.encryption_salt = keys.salt
        user.wrapped_dek = keys.wrapped_dek
        await session.commit()

        return await self._get_by_pk_raw(session, pk, pk_column_name, filters)

    async def reset_password(
        self,
        pk: int | str,
        old_password: str,
        new_password: str,
        pk_column_name: str | None = None,
        filters: Sequence[ColumnElement[bool]] | None = None,
    ) -> User:
        """Change a user's password while keeping their data readable.

        The user's data encryption key is unwrapped with the old password and
        wrapped again with the new one, so every field the user owns stays
        decryptable without being re-encrypted. All changes are committed
        atomically.

        Args:
            pk (int | str): The primary key value identifying the user.
            old_password (str): The user's current plaintext password.
            new_password (str): The new plaintext password to hash and store.
            pk_column_name (str, optional): The column to match ``pk`` against.
                Defaults to the DAO's ``pk_column_name``.
            filters (Sequence[ColumnElement[bool]], optional): Additional SQL
                filters to apply. Defaults to None.

        Returns:
            User: The updated user record.

        Raises:
            InvalidPasswordError: If ``old_password`` is incorrect.
            EncryptionKeysMissingError: If the user has not been migrated to
                per-user encryption yet.

        """
        col = pk_column_name or self.pk_column_name

        if self.session is not None:
            return await self._reset_password_raw(self.session, pk, old_password, new_password, col, filters)

        async with self._session_factory() as session:
            return await self._reset_password_raw(session, pk, old_password, new_password, col, filters)

    async def _force_reset_password_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        new_password: str,
        pk_column_name: str,
        filters: Sequence[ColumnElement[bool]] | None,
    ) -> User:
        """Set a new password and wipe the user's fields on the given session.

        Args:
            session (AsyncSession): The database session to use.
            pk (int | str): The primary key value identifying the user.
            new_password (str): The new plaintext password.
            pk_column_name (str): The column to match ``pk`` against.
            filters (Sequence[ColumnElement[bool]] | None): Additional SQL
                filters to apply.

        Returns:
            User: The updated user record.

        """
        user = await self._get_by_pk_raw(session, pk, pk_column_name, filters)

        user_password_ids = select(Password.id).where(Password.user_id == user.id)
        await session.execute(delete(Field).where(Field.password_id.in_(user_password_ids)))

        keys = CryptographyClient().create_user_keys(new_password)
        user.password_hash = generate_password_hash(new_password)
        user.encryption_salt = keys.salt
        user.wrapped_dek = keys.wrapped_dek
        await session.commit()

        return await self._get_by_pk_raw(session, pk, pk_column_name, filters)

    async def force_reset_password(
        self,
        pk: int | str,
        new_password: str,
        pk_column_name: str | None = None,
        filters: Sequence[ColumnElement[bool]] | None = None,
    ) -> User:
        """Reset a user's password without knowing the current one.

        Without the current password the user's data encryption key cannot be
        recovered, so all of the user's fields are permanently deleted and a
        new key is generated. Password records themselves are kept.

        Args:
            pk (int | str): The primary key value identifying the user.
            new_password (str): The new plaintext password to hash and store.
            pk_column_name (str, optional): The column to match ``pk`` against.
                Defaults to the DAO's ``pk_column_name``.
            filters (Sequence[ColumnElement[bool]], optional): Additional SQL
                filters to apply. Defaults to None.

        Returns:
            User: The updated user record.

        """
        col = pk_column_name or self.pk_column_name

        if self.session is not None:
            return await self._force_reset_password_raw(self.session, pk, new_password, col, filters)

        async with self._session_factory() as session:
            return await self._force_reset_password_raw(session, pk, new_password, col, filters)
