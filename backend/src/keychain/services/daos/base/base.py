"""Base async DAO for SQLAlchemy models using a session or database client."""

__all__ = ("BaseDAO",)

from abc import ABC
from typing import Any, Literal, overload, Sequence

from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from keychain.services.db_client import DBClient
from keychain.services.db_client.models.base import Base
from keychain.utils.filter import Filter

from .types import AcceptableFiltersType


class BaseDAO[DatabaseModel: Base](ABC):
    """Abstract async data-access layer for one SQLAlchemy declarative model.

    Subclasses set ``database_model`` and may override loading and scoping
    hooks used by the CRUD helpers below.

    Attributes:
        pk_column_name (str): Default primary-key attribute name. Defaults to
            ``"id"``.
        database_model (type[DatabaseModel]): ORM class this DAO operates on.
        get_all_columns (tuple[InstrumentedAttribute, ...] | None): Columns
            loaded via ``load_only`` in :meth:`get_all`; None loads all columns.
        select_in_options_single (tuple[InstrumentedAttribute, ...] | None):
            Relationships eagerly loaded in single-row reads.
        select_in_options_all (tuple[InstrumentedAttribute, ...] | None):
            Relationships eagerly loaded in list reads.
        base_filters (list[ColumnElement[bool]] | None): WHERE clauses always
            applied together with per-call filters.

    """

    pk_column_name: str = "id"
    database_model: type[DatabaseModel]

    get_all_columns: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_single: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_all: tuple[InstrumentedAttribute, ...] | None = None
    join_options_single: tuple[InstrumentedAttribute, ...] | None = None
    join_options_all: tuple[InstrumentedAttribute, ...] | None = None
    base_filters: list[ColumnElement[bool]] | None = None

    @overload
    def __init__(
        self,
        database_client: DBClient,
        session: None = None,
        **_: Any,
    ) -> None: ...

    @overload
    def __init__(
        self,
        database_client: None,
        session: AsyncSession,
        **_: Any,
    ) -> None: ...

    def __init__(
        self,
        database_client: DBClient | None = None,
        session: AsyncSession | None = None,
        **_: Any,
    ) -> None:
        """Bind the DAO to a database client or an existing async session.

        Provide exactly one of ``database_client`` or ``session``. When a
        client is used, each public method opens a short-lived session from
        ``session_factory``; when a session is injected, that session is reused.

        Args:
            database_client (DBClient | None, optional): Client used
                to create sessions per operation. Defaults to None.
            session (AsyncSession | None, optional): Injected session for
                request-scoped or transactional use. Defaults to None.

        Raises:
            ValueError: If both arguments are omitted.

        """
        if database_client is None and session is None:
            raise ValueError("Either database_client or session must be provided")

        self.database_client = database_client
        self.session = session

    @classmethod
    def parse_filters(cls, filters: AcceptableFiltersType) -> list[ColumnElement[bool]]:
        """Normalize API-style filters into SQLAlchemy WHERE clauses.

        Args:
            filters (AcceptableFiltersType): ``None``, raw ``ColumnElement``
                instances, ``Filter`` models, or dicts validated as ``Filter``.

        Returns:
            list[ColumnElement[bool]]: Clauses ready for ``.where()``.

        Raises:
            ValueError: If an entry has an unsupported type.

        """
        payload: list[ColumnElement[bool]] = []
        if filters is None:
            return payload

        for f in filters:
            match f:
                case ColumnElement():
                    payload.append(f)
                case dict():
                    filter_: Filter[str] = Filter.model_validate(f)
                    payload.append(filter_.to_sqlalchemy_filter(cls.database_model))
                case Filter():
                    payload.append(f.to_sqlalchemy_filter(cls.database_model))
                case _:
                    raise ValueError(f"Unknown filter type: {type(f)}")

        return payload

    @classmethod
    def concat_filters(cls, *filters: AcceptableFiltersType) -> list[ColumnElement[bool]]:
        """Parse and merge several filter payloads into one list.

        Args:
            *filters (AcceptableFiltersType): Zero or more filter collections
                passed to :meth:`parse_filters`.

        Returns:
            list[ColumnElement[bool]]: Combined clauses in argument order.

        """
        payload: list[ColumnElement[bool]] = []
        for f in filters:
            payload.extend(cls.parse_filters(f))

        return payload

    async def _get_by_pk_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        filters: list[ColumnElement[bool]] | None,
    ) -> DatabaseModel:
        """Load one row by primary key on the given session.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value.
            pk_column_name (str): Attribute name of the PK column on the model.
            filters (list[ColumnElement[bool]] | None): Extra WHERE clauses
                merged with ``base_filters``.

        Returns:
            DatabaseModel: The matching ORM instance.

        """
        stmt = select(self.database_model).where(getattr(self.database_model, pk_column_name) == pk)

        if c_filters := self.concat_filters(self.base_filters, filters):
            stmt = stmt.where(*c_filters)

        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        if self.join_options_single:
            for join_option in self.join_options_single:
                stmt = stmt.join(join_option)

        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_by_pk(
        self,
        pk: int | str,
        pk_column_name: str | None = None,
        filters: list[ColumnElement[bool]] | None = None,
    ) -> DatabaseModel:
        """Load one row by primary key.

        Args:
            pk (int | str): Primary key value.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to :attr:`pk_column_name`.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            DatabaseModel: The matching ORM instance.

        """
        pk_column_name = pk_column_name or self.pk_column_name

        if self.session is not None:
            return await self._get_by_pk_raw(self.session, pk, pk_column_name, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, pk, pk_column_name, filters)

    async def _get_total_raw(self, session: AsyncSession, filters: list[ColumnElement[bool]] | None = None) -> int:
        """Count rows matching filters on the given session.

        Args:
            session (AsyncSession): Active async session.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            int: Number of matching rows.

        """
        stmt = select(func.count()).select_from(self.database_model)

        if c_filters := self.concat_filters(self.base_filters, filters):
            stmt = stmt.where(*c_filters)

        if self.join_options_all:
            for join_option in self.join_options_all:
                stmt = stmt.join(join_option)

        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_total(self, filters: list[ColumnElement[bool]] | None = None) -> int:
        """Count rows matching filters.

        Args:
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            int: Number of matching rows.

        """
        if self.session is not None:
            return await self._get_total_raw(self.session, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_total_raw(session, filters)

    async def _get_all_raw(
        self,
        session: AsyncSession,
        limit: int | None,
        offset: int | None,
        sort_by: str | None,
        sort_order: Literal["asc", "desc"],
        filters: list[ColumnElement[bool]] | None,
    ) -> tuple[Sequence[DatabaseModel], int]:
        """List rows with pagination, sorting, and eager-load options.

        Args:
            session (AsyncSession): Active async session.
            limit (int | None): Maximum rows to return, or no limit if None.
            offset (int | None): Rows to skip, or no offset if None.
            sort_by (str | None): Model attribute name to sort by, or no sort.
            sort_order (Literal["asc", "desc"]): Sort direction.
            filters (list[ColumnElement[bool]] | None): Extra WHERE clauses
                merged with ``base_filters``.

        Returns:
            tuple[Sequence[DatabaseModel], int]: Matching rows and total count
                (count uses the same filters, without limit/offset).

        """
        stmt = select(self.database_model)

        if sort_by:
            order_func = asc if sort_order == "asc" else desc
            stmt = stmt.order_by(order_func(getattr(self.database_model, sort_by)))

        if self.get_all_columns:
            stmt = stmt.options(load_only(*self.get_all_columns))

        if self.join_options_all:
            for join_option in self.join_options_all:
                stmt = stmt.join(join_option)

        if self.select_in_options_all:
            stmt = stmt.options(*map(selectinload, self.select_in_options_all))

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        if c_filters := self.concat_filters(self.base_filters, filters):
            stmt = stmt.where(*c_filters)

        total = await self._get_total_raw(session, filters)
        result = await session.execute(stmt)
        return result.scalars().all(), total

    async def get_all(
        self,
        limit: int | None = 100,
        offset: int | None = 0,
        sort_by: str = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        filters: list[ColumnElement[bool]] | None = None,
    ) -> tuple[Sequence[DatabaseModel], int]:
        """List rows with pagination, sorting, and optional filters.

        Args:
            limit (int | None, optional): Maximum rows to return. Defaults to
                100.
            offset (int | None, optional): Rows to skip. Defaults to 0.
            sort_by (str, optional): Model attribute to sort by. Defaults to
                ``"id"``.
            sort_order (Literal["asc", "desc"], optional): Sort direction.
                Defaults to ``"asc"``.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            tuple[Sequence[DatabaseModel], int]: Page of rows and total count.

        """
        if self.session is not None:
            return await self._get_all_raw(self.session, limit, offset, sort_by, sort_order, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_all_raw(session, limit, offset, sort_by, sort_order, filters)

    async def _create_raw(self, session: AsyncSession, **kwargs: Any) -> DatabaseModel:
        """Insert a row and reload it on the given session.

        Args:
            session (AsyncSession): Active async session.
            **kwargs (Any): Column values for the new ORM instance.

        Returns:
            DatabaseModel: Persisted instance after commit.

        """
        obj = self.database_model(**kwargs)
        session.add(obj)
        await session.commit()
        return await self._get_by_pk_raw(session, getattr(obj, self.pk_column_name), self.pk_column_name, None)

    async def create(self, **kwargs: Any) -> DatabaseModel:
        """Insert a row and return the persisted instance.

        Args:
            **kwargs (Any): Column values for the new ORM instance.

        Returns:
            DatabaseModel: Instance loaded after commit.

        """
        if self.session is not None:
            return await self._create_raw(self.session, **kwargs)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **kwargs)

    async def _update_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        filters: list[ColumnElement[bool]] | None,
        **kwargs: Any,
    ) -> DatabaseModel:
        """Update columns for one row on the given session.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value.
            pk_column_name (str): Attribute name of the PK column.
            filters (list[ColumnElement[bool]] | None): Extra WHERE clauses
                applied to the UPDATE statement.
            **kwargs (Any): Column values to set; if empty, only loads the row.

        Returns:
            DatabaseModel: Instance after commit (or unchanged if no values).

        """
        c_filters = self.concat_filters(self.base_filters, filters)

        if not kwargs:
            return await self._get_by_pk_raw(session, pk, pk_column_name, c_filters)

        stmt = update(self.database_model).where(getattr(self.database_model, pk_column_name) == pk).values(**kwargs)
        if c_filters:
            stmt = stmt.where(*c_filters)

        await session.execute(stmt)
        await session.commit()

        return await self._get_by_pk_raw(session, pk, pk_column_name, c_filters)

    async def update(
        self,
        pk: int | str,
        pk_column_name: str | None = None,
        filters: list[ColumnElement[bool]] | None = None,
        **kwargs: Any,
    ) -> DatabaseModel:
        """Update one row by primary key.

        Args:
            pk (int | str): Primary key value.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to :attr:`pk_column_name`.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses for the UPDATE. Defaults to None.
            **kwargs (Any): Column values to set.

        Returns:
            DatabaseModel: Instance after commit.

        """
        col = pk_column_name or self.pk_column_name
        if self.session is not None:
            return await self._update_raw(self.session, pk, col, **kwargs, filters=filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._update_raw(session, pk, col, **kwargs, filters=filters)

    async def _delete_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        instance: DatabaseModel | None,
        filters: list[ColumnElement[bool]] | None,
    ) -> bool:
        """Delete one row on the given session.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value (used when ``instance`` is None).
            pk_column_name (str): Attribute name of the PK column.
            instance (DatabaseModel | None): Pre-loaded row to delete, or None
                to fetch by primary key.
            filters (list[ColumnElement[bool]] | None): Extra WHERE clauses
                when loading by primary key.

        Returns:
            bool: Always ``True`` after a successful delete and commit.

        """
        c_filters = self.concat_filters(self.base_filters, filters)
        instance = instance or await self._get_by_pk_raw(session, pk, pk_column_name, c_filters)
        await session.delete(instance)
        await session.commit()
        return True

    async def delete(
        self,
        pk: int | str,
        pk_column_name: str | None = None,
        instance: DatabaseModel | None = None,
        filters: list[ColumnElement[bool]] | None = None,
    ) -> bool:
        """Delete one row by primary key.

        Args:
            pk (int | str): Primary key value.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to :attr:`pk_column_name`.
            instance (DatabaseModel | None, optional): Pre-loaded row to
                delete instead of fetching. Defaults to None.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses when loading by primary key. Defaults to None.

        Returns:
            bool: Always ``True`` after a successful delete.

        """
        col = pk_column_name or self.pk_column_name
        if self.session is not None:
            return await self._delete_raw(self.session, pk, col, instance, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._delete_raw(session, pk, col, instance, filters)
