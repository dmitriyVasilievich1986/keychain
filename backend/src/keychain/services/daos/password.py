"""Password DAO (Data Access Object) for database operations on Password entities."""

__all__ = ["PasswordDAO"]

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from keychain.services.db_client.models.password import Password

from .base import BaseDAO


class PasswordDAO(BaseDAO[Password]):
    """DAO implementation for Password entity database operations.

    This class provides concrete implementations of database operations for Password
    entities, including CRUD operations and password-specific queries. It uses the
    DBClient to manage database sessions and transactions.
    """

    async def get_all(self) -> list[Password]:
        """Retrieve all passwords from the database.

        Returns:
            A list of all passwords in the database.

        """
        async with self.db_client.session() as session:
            passwords = await session.execute(select(Password.id, Password.name))
            return passwords.all()

    async def _get_by_id_with_session(self, session: AsyncSession, pk: int) -> Password:
        """Internal method to retrieve a password by ID using the provided session.

        Args:
            session: An active AsyncSession for the database.
            pk: The primary key (ID) of the password to retrieve.

        Returns:
            The Password object with associated fields loaded, if found.

        Raises:
            ValueError: If no password with the given ID exists.

        """
        password = await session.execute(
            select(Password).where(Password.id == pk).options(selectinload(Password.fields))
        )
        password = password.scalar_one_or_none()
        if password is None:
            logger.error(f"Password with id '{pk}' not found")
            raise ValueError(f"Password with id '{pk}' not found")

        return password

    async def create(self, name: str, user_id: int, image_url: str | None = None) -> Password:
        """Create a new password in the database.

        Creates a new password with the provided name and user_id. The image_url
        is optional and will default to "/static/i/no-photo.png" if not provided.
        After creation, the password is refreshed from the database to ensure all
        generated fields (e.g., ID, timestamps) are populated.

        Args:
            name: The name of the password to create.
            user_id: The unique identifier of the user who owns the password.
            image_url: The URL of the image associated with the password.

        Returns:
            The created Password object with all fields populated.

        """
        async with self.db_client.session() as session:
            password = Password(
                name=name,
                user_id=user_id,
                image_url=image_url,
            )
            session.add(password)
            await session.commit()
            return await self._get_by_id_with_session(session, password.id)

    async def update(self, pk: int, name: str, image_url: str | None = None) -> Password:
        """Update an existing password in the database.

        Updates the password's name and/or image_url if provided. Only the fields
        that are not None will be updated. After updating, the password is refreshed
        from the database to ensure the returned object reflects the current state.

        Args:
            pk: The unique identifier of the password to update.
            name: The new name for the password.
            image_url: The new image URL for the password.

        Returns:
            The updated Password object.

        Raises:
            ValueError: If no password with the given ID exists.

        """
        async with self.db_client.session() as session:
            password = await self._get_by_id_with_session(session, pk)
            password.name = name
            password.image_url = image_url

            await session.commit()
            return await self._get_by_id_with_session(session, password.id)
