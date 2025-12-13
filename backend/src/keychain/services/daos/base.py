"""Base DAO (Data Access Object) abstract class for database operations."""

__all__ = ["BaseDAO"]

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from keychain.services.db_client.client import DBClient

T = TypeVar("T")


class BaseDAO(ABC, Generic[T]):
    """Abstract base class for Data Access Objects (DAOs).

    This class defines the standard interface for database operations that all
    DAO implementations must follow. It provides a generic type parameter T
    that represents the entity type being managed.

    Subclasses must implement all abstract methods to provide concrete database
    operations for their specific entity types.
    """

    def __init__(self, db_client: DBClient, **_: Any):
        """Initialize the BaseDAO with a database client.

        Args:
            db_client: The database client instance used to create sessions.

        """
        self.db_client = db_client

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Retrieve all entities from the database.

        Returns:
            A list of all entities in the database.

        """
        pass

    @abstractmethod
    async def _get_by_id_with_session(self, session: AsyncSession, pk: int) -> T:
        """Internal method to retrieve an entity by ID using the provided session.

        Args:
            session: An active AsyncSession for the database.
            pk: The primary key (ID) of the entity to retrieve.

        Returns:
            The entity object if found.

        """
        pass

    async def get_by_id(self, pk: int) -> T:
        """Retrieve an entity from the database by its PK.

        Args:
            pk: The unique identifier of the entity to retrieve.

        Returns:
            The entity object if found.

        Raises:
            ValueError: If no entity with the given PK exists.

        """
        async with self.db_client.session() as session:
            return await self._get_by_id_with_session(session, pk)

    @abstractmethod
    async def create(self, **kwargs: Any) -> T:
        """Create a new entity in the database by its PK.

        Args:
            kwargs: The keyword arguments to create the entity.

        Returns:
            The created entity object, potentially with generated fields
            (e.g., ID, timestamps) populated.

        """
        pass

    @abstractmethod
    async def update(self, pk: int, **kwargs: Any) -> T:
        """Update an existing entity in the database by its PK.

        Args:
            pk: The unique identifier of the entity to update.
            kwargs: The keyword arguments to update the entity.

        Returns:
            The updated entity object.

        Raises:
            ValueError: If no entity with the given PK exists.

        """
        pass

    async def delete(self, pk: int) -> None:
        """Delete an entity from the database by its PK.

        Args:
            pk: The unique identifier of the entity to delete.

        Raises:
            ValueError: If no entity with the given PK exists.

        """
        async with self.db_client.session() as session:
            obj = await self._get_by_id_with_session(session, pk)
            await session.delete(obj)
            await session.commit()
