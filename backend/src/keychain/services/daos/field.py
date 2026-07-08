"""Data access object for the ``Field`` model."""

__all__ = ("FieldDAO",)

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from keychain.services.db_client.models.field import Field
from keychain.services.db_client.models.password import Password

from .base import BaseDAO


class FieldDAO(BaseDAO[Field]):
    """Data access object providing CRUD operations for ``Field`` records."""

    pk_column_name: str = "id"
    database_model: type[Field] = Field

    join_options_all = (Password,)
    join_options_single = (Password,)

    async def _update_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        filters: list[ColumnElement[bool]] | None,
        **kwargs: Any,
    ) -> Field:
        """Update a field by creating a new record and soft-deleting the old one.

        The existing field is marked as deleted and a new field is created with
        the updated value while preserving the password association and name.

        Args:
            session (AsyncSession): The database session to use.
            pk (int | str): The primary key of the field to update.
            pk_column_name (str): The name of the primary key column.
            filters (list[ColumnElement[bool]] | None, optional): Additional
                filters to apply when locating the field. Defaults to None.
            **kwargs (Any): Field attributes to update; must include ``value``.

        Returns:
            Field: The newly created field reflecting the updated value.

        Raises:
            ValueError: If ``value`` is not provided in ``kwargs``.

        """
        if (value := kwargs.get("value")) is None:
            raise ValueError("Value is required")

        current_field = await self._get_by_pk_raw(session, pk, pk_column_name, filters)
        current_field.is_deleted = True
        new_field = Field(value=value, password_id=current_field.password_id, name=current_field.name)
        session.add(new_field)
        await session.commit()

        return await self._get_by_pk_raw(session, new_field.id, pk_column_name, filters)

    async def _create_raw(
        self, session: AsyncSession, filters: list[ColumnElement[bool]] | None, **kwargs: Any
    ) -> Field:
        """Create a new field associated with an existing password.

        Args:
            session (AsyncSession): The database session to use.
            filters (list[ColumnElement[bool]] | None, optional): Additional
                filters to apply when validating the parent password. Defaults
                to None.
            **kwargs (Any): Field attributes; must include ``password_id``.

        Returns:
            Field: The newly created field.

        Raises:
            ValueError: If ``password_id`` is not provided in ``kwargs``.

        """
        if (password_id := kwargs.get("password_id")) is None:
            raise ValueError("Password ID is required")

        stmt = select(Password).where(Password.id == password_id)
        if c_filters := self.concat_filters(self.base_filters, filters):
            stmt = stmt.where(*c_filters)

        session.execute(stmt)

        obj = self.database_model(**kwargs)
        session.add(obj)
        await session.commit()
        return await self._get_by_pk_raw(session, getattr(obj, self.pk_column_name), self.pk_column_name, filters)

    async def create(self, filters: list[ColumnElement[bool]] | None = None, **kwargs: Any) -> Field:
        """Create a new field, using an existing session or a new one.

        Args:
            filters (list[ColumnElement[bool]] | None, optional): Additional
                filters to apply during creation. Defaults to None.
            **kwargs (Any): Field attributes; must include ``password_id``.

        Returns:
            Field: The newly created field.

        """
        if self.session is not None:
            return await self._create_raw(self.session, **kwargs, filters=filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **kwargs, filters=filters)

    async def _delete_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        instance: Field | None,
        filters: list[ColumnElement[bool]] | None,
    ) -> bool:
        """Soft-delete a field by marking it as deleted.

        Args:
            session (AsyncSession): The database session to use.
            pk (int | str): The primary key of the field to delete.
            pk_column_name (str): The name of the primary key column.
            instance (Field | None): An already-loaded field instance to delete;
                if None, the field is looked up by primary key.
            filters (list[ColumnElement[bool]] | None): Additional filters to
                apply when locating the field.

        Returns:
            bool: True once the field has been marked as deleted.

        """
        c_filters = self.concat_filters(self.base_filters, filters)
        instance = instance or await self._get_by_pk_raw(session, pk, pk_column_name, c_filters)
        instance.is_deleted = True
        await session.commit()
        return True
