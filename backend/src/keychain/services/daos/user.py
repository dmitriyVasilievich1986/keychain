"""User DAO (Data Access Object) for database operations on User entities."""

__all__ = ["UserDAO"]

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from werkzeug.security import generate_password_hash

from keychain.services.db_client.models.user import User

from .base import BaseDAO


class UserDAO(BaseDAO[User]):
    """DAO implementation for User entity database operations.

    This class provides concrete implementations of database operations for User
    entities, including CRUD operations and user-specific queries. It uses the
    DBClient to manage database sessions and transactions.
    """

    async def get_all(self) -> list[User]:
        """Retrieve all users from the database.

        Returns:
            A list of all users in the database.

        """
        async with self.db_client.session() as session:
            users = await session.execute(select(User.id, User.name))
            return users.all()

    async def _get_by_id_with_session(self, session: AsyncSession, pk: int) -> User:
        """Internal method to retrieve a user by ID using the provided session.

        Args:
            session: An active AsyncSession for the database.
            pk: The primary key (ID) of the user to retrieve.

        Returns:
            The User object with associated passwords loaded, if found.

        Raises:
            ValueError: If no user with the given ID exists.

        """
        user = await session.execute(select(User).where(User.id == pk).options(selectinload(User.passwords)))
        user = user.scalar_one_or_none()
        if user is None:
            logger.error(f"User with id '{pk}' not found")
            raise ValueError(f"User with id '{pk}' not found")

        return user

    async def create(self, name: str, password: str) -> User:
        """Create a new user in the database.

        Creates a new user with the provided name and password. The password
        will be hashed automatically by the User model. After creation, the
        user is refreshed from the database to ensure all generated fields
        (e.g., ID, timestamps) are populated.

        Args:
            name: The name of the user to create.
            password: The plaintext password for the user (will be hashed).

        Returns:
            The created User object with all fields populated.

        """
        async with self.db_client.session() as session:
            user = User(name=name, password=password)
            session.add(user)
            await session.commit()
            return await self._get_by_id_with_session(session, user.id)

    async def update(self, pk: int, name: str) -> User:
        """Update an existing user in the database.

        Updates the user's name if provided. Only the fields that are not None
        will be updated. After updating, the user is refreshed from the database
        to ensure the returned object reflects the current state.

        Args:
            pk: The unique identifier of the user to update.
            name: The new name for the user.

        Returns:
            The updated User object.

        Raises:
            ValueError: If no user with the given ID exists.

        """
        async with self.db_client.session() as session:
            user = await self._get_by_id_with_session(session, pk)
            user.name = name

            await session.commit()
            return await self._get_by_id_with_session(session, user.id)

    async def verify_password(self, pk: int, password: str) -> bool:
        """Verify the password for a user.

        Args:
            pk: The unique identifier of the user to verify the password for.
            password: The password to verify.

        Returns:
            True if the password is valid, False otherwise.

        """
        user = await self.get_by_id(pk)
        return user.verify_password(password)

    async def reset_password(self, pk: int, password: str) -> User:
        """Reset the password for a user.

        Args:
            pk: The unique identifier of the user to reset the password for.
            password: The new password for the user.

        Returns:
            The updated User object.

        """
        async with self.db_client.session() as session:
            user = await self._get_by_id_with_session(session, pk)
            user.password_hash = generate_password_hash(password)
            await session.commit()
            return await self._get_by_id_with_session(session, user.id)
