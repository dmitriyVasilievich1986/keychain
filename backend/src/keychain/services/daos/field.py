"""Field DAO (Data Access Object) for database operations on Field entities."""

__all__ = ["FieldDAO"]

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from keychain.services.db_client.models.field import Field

from .base import BaseDAO


class FieldDAO(BaseDAO[Field]):
    """DAO implementation for Field entity database operations.

    This class provides concrete implementations of database operations for Field
    entities, including CRUD operations and field-specific queries. It uses the
    DBClient to manage database sessions and transactions.
    """

    async def get_all(self) -> list[Field]:
        """Retrieve all fields from the database.

        Returns:
            A list of all fields in the database.

        """
        async with self.db_client.session() as session:
            fields = await session.execute(select(Field.id, Field.name, Field.is_deleted))
            return fields.all()

    async def _get_by_id_with_session(self, session: AsyncSession, pk: int) -> Field:
        """Internal method to retrieve a field by ID using the provided session.

        Args:
            session: An active AsyncSession for the database.
            pk: The primary key (ID) of the field to retrieve.

        Returns:
            The Field object with associated password loaded, if found.

        Raises:
            ValueError: If no field with the given ID exists.

        """
        field = await session.execute(select(Field).where(Field.id == pk).options(selectinload(Field.password)))
        field = field.scalar_one_or_none()
        if field is None:
            logger.error(f"Field with id '{pk}' not found")
            raise ValueError(f"Field with id '{pk}' not found")

        return field

    async def create(self, name: str, value: str, password_id: int) -> Field:
        """Create a new field in the database.

        Creates a new field with the provided name, value, and password_id.
        After creation, the field is refreshed from the database to ensure all
        generated fields (e.g., ID, timestamps) are populated.

        Args:
            name: The name of the field to create.
            value: The value of the field to create.
            password_id: The unique identifier of the password that owns the field.

        Returns:
            The created Field object with all fields populated.

        """
        async with self.db_client.session() as session:
            field = Field(
                name=name,
                value=value,
                password_id=password_id,
            )
            session.add(field)
            await session.commit()
            await session.refresh(field)
            return field

    async def update(self, pk: int, value: str) -> Field:
        """Update an existing field in the database.

        Updates the field's name and/or value if provided. Only the fields
        that are not None will be updated. After updating, the field is refreshed
        from the database to ensure the returned object reflects the current state.

        Args:
            pk: The unique identifier of the field to update.
            name: The new name for the field.
            value: The new value for the field.

        Returns:
            The updated Field object.

        Raises:
            ValueError: If no field with the given ID exists.

        """
        async with self.db_client.session() as session:
            field = await self._get_by_id_with_session(session, pk)
            field.is_deleted = True
            new_field = Field(value=value, password_id=field.password_id, name=field.name)
            session.add(new_field)

            await session.commit()
            await session.refresh(new_field)
            return new_field

    async def delete(self, pk: int) -> None:
        """Delete a field from the database by its PK.

        Args:
            pk: The unique identifier of the field to delete.

        Raises:
            ValueError: If no field with the given PK exists.

        """
        async with self.db_client.session() as session:
            obj = await self._get_by_id_with_session(session, pk)
            obj.is_deleted = True
            await session.commit()
