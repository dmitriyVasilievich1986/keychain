"""Data access object for user records."""

__all__ = ["UserDAO"]

from sqlalchemy.sql import ColumnElement
from werkzeug.security import generate_password_hash

from keychain.services.db_client.models.user import User

from .base import BaseDAO


class UserDAO(BaseDAO[User]):
    """Data access object providing user-specific database operations."""

    pk_column_name: str = "id"
    database_model: type[User] = User

    get_all_columns = (User.id, User.name)
    select_in_options_single = (User.passwords,)

    async def get_by_username(self, username: str, filters: list[ColumnElement[bool]] | None = None) -> User:
        """Retrieve a user by their username.

        Args:
            username (str): The username to look up (matched against the
                ``name`` column).
            filters (list[ColumnElement[bool]], optional): Additional SQL
                filters to apply. Defaults to None.

        Returns:
            User: The user matching the given username.

        """
        if self.session is not None:
            return await self._get_by_pk_raw(self.session, username, "name", filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, username, "name", filters)

    async def reset_password(
        self,
        pk: int | str,
        password: str,
        pk_column_name: str | None = None,
        filters: list[ColumnElement[bool]] | None = None,
    ) -> User:
        """Reset a user's password by hashing and storing the new value.

        Args:
            pk (int | str): The primary key value identifying the user.
            password (str): The new plaintext password to hash and store.
            pk_column_name (str, optional): The column to match ``pk`` against.
                Defaults to the DAO's ``pk_column_name``.
            filters (list[ColumnElement[bool]], optional): Additional SQL
                filters to apply. Defaults to None.

        Returns:
            User: The updated user record.

        """
        col = pk_column_name or self.pk_column_name
        new_password_hash = generate_password_hash(password)

        if self.session is not None:
            return await self._update_raw(self.session, pk, col, {"password_hash": new_password_hash}, filters=filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._update_raw(session, pk, col, {"password_hash": new_password_hash}, filters=filters)
