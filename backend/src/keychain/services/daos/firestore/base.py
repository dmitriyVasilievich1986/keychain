"""Base async DAO for Pydantic models stored as Firestore documents."""

__all__ = ("BaseFirestoreDAO",)

from abc import ABC
from datetime import date, datetime, time, timezone
from typing import Any, Literal
from uuid import uuid4

from google.api_core.exceptions import NotFound
from google.cloud.firestore import AsyncCollectionReference, AsyncQuery, DocumentSnapshot
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel

from keychain.services.db_client.firestore import FirestoreClient
from keychain.utils.filter import Filter

from .constants import DOCUMENT_ID_FIELD_PATH, FirestoreFiltersType, OPERATORS


class BaseFirestoreDAO[DocumentModel: BaseModel](ABC):
    """Abstract async data-access layer for one Firestore collection.

    Each document is represented by a Pydantic model. The document ID is
    exposed on the model through :attr:`id_field` and is not stored inside
    the document body.

    Attributes:
        id_field (str): Model field that holds the document ID. Defaults to
            ``"id"``.
        document_model (type[DocumentModel]): Pydantic model for documents in
            this collection.
        collection_name (str | None): Default collection for this DAO class;
            overridden per instance by the ``collection_name`` init argument.
            None uses the client's configured collection.
        base_filters (FirestoreFiltersType): Filters always applied together
            with per-call filters in list and count queries.

    """

    id_field: str = "id"
    document_model: type[DocumentModel]
    collection_name: str | None = None
    base_filters: FirestoreFiltersType = None

    def __init__(
        self,
        firestore_client: FirestoreClient,
        collection_name: str | None = None,
        **_: Any,
    ) -> None:
        """Bind the DAO to a Firestore client and a collection.

        Args:
            firestore_client (FirestoreClient): Client that owns the
                underlying ``AsyncClient``.
            collection_name (str | None, optional): Collection this instance
                operates on; None keeps the class-level ``collection_name``.
                Defaults to None.

        """
        self.firestore_client = firestore_client
        if collection_name is not None:
            self.collection_name = collection_name

    @property
    def collection(self) -> AsyncCollectionReference:
        """Return a reference to this DAO's collection.

        Returns:
            AsyncCollectionReference: ``collection_name``, or the client's
                configured collection when it is None.

        """
        if self.collection_name is None:
            return self.firestore_client.collection
        return self.firestore_client.client.collection(self.collection_name)

    @classmethod
    def _filter_value(cls, value: Any) -> Any:
        """Convert a filter value to a type Firestore can compare.

        Firestore stores timestamps, not dates, so ``date`` values (which
        ``Filter`` produces from ISO strings) become midnight UTC.

        Args:
            value (Any): Raw filter value.

        Returns:
            Any: Value safe to pass to a Firestore query.

        """
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, time.min, tzinfo=timezone.utc)
        if isinstance(value, list):
            return [cls._filter_value(v) for v in value]
        return value

    def parse_filters(self, filters: FirestoreFiltersType) -> list[FieldFilter]:
        """Normalize API-style filters into Firestore field filters.

        Args:
            filters (FirestoreFiltersType): ``None``, raw ``FieldFilter``
                instances, ``Filter`` models, or dicts validated as ``Filter``.

        Returns:
            list[FieldFilter]: Filters ready for ``.where(filter=...)``.

        Raises:
            ValueError: If an entry has an unsupported type or operator.

        """
        payload: list[FieldFilter] = []
        if filters is None:
            return payload

        for f in filters:
            match f:
                case FieldFilter():
                    payload.append(f)
                case dict():
                    payload.append(self._to_field_filter(Filter.model_validate(f)))
                case Filter():
                    payload.append(self._to_field_filter(f))
                case _:
                    raise ValueError(f"Unknown filter type: {type(f)}")

        return payload

    def _to_field_filter(self, filter_: Filter[str]) -> FieldFilter:
        """Convert one ``Filter`` model into a Firestore field filter.

        Filters on :attr:`id_field` target the document ID, which Firestore
        compares as document references, so their values are converted.

        Args:
            filter_ (Filter[str]): Validated filter triple.

        Returns:
            FieldFilter: Equivalent Firestore filter.

        Raises:
            ValueError: If the operator is not supported by Firestore.

        """
        if (op_string := OPERATORS.get(filter_.operator)) is None:
            raise ValueError(f"Operator {filter_.operator!r} is not supported by Firestore")

        if filter_.operator in ("isnull", "notnull"):
            return FieldFilter(filter_.column, op_string, None)

        if filter_.column == self.id_field:
            values = filter_.value if isinstance(filter_.value, list) else [filter_.value]
            references = [self.collection.document(str(v)) for v in values]
            return FieldFilter(
                DOCUMENT_ID_FIELD_PATH,
                op_string,
                references if isinstance(filter_.value, list) else references[0],
            )

        return FieldFilter(filter_.column, op_string, self._filter_value(filter_.value))

    def concat_filters(self, *filters: FirestoreFiltersType) -> list[FieldFilter]:
        """Parse and merge several filter payloads into one list.

        Args:
            *filters (FirestoreFiltersType): Zero or more filter collections
                passed to :meth:`parse_filters`.

        Returns:
            list[FieldFilter]: Combined filters in argument order.

        """
        payload: list[FieldFilter] = []
        for f in filters:
            payload.extend(self.parse_filters(f))

        return payload

    def to_model(self, snapshot: DocumentSnapshot) -> DocumentModel:
        """Build a model from a document snapshot.

        Args:
            snapshot (DocumentSnapshot): An existing document.

        Returns:
            DocumentModel: Model with the document ID set on :attr:`id_field`.

        """
        return self.document_model.model_validate({**(snapshot.to_dict() or {}), self.id_field: snapshot.id})

    def to_document(self, model: DocumentModel) -> dict[str, Any]:
        """Serialize a model into a Firestore document body.

        Override to customize serialization, e.g. for ``Enum``, ``date`` or
        ``Decimal`` fields, which Firestore cannot store natively.

        Args:
            model (DocumentModel): Model to store.

        Returns:
            dict[str, Any]: Document body without :attr:`id_field`.

        """
        return model.model_dump(exclude={self.id_field})

    def _build_query(self, filters: FirestoreFiltersType) -> AsyncCollectionReference | AsyncQuery:
        """Start a query on the collection with base and per-call filters.

        Args:
            filters (FirestoreFiltersType): Extra filters merged with
                ``base_filters``.

        Returns:
            AsyncCollectionReference | AsyncQuery: The filtered query.

        """
        query: AsyncCollectionReference | AsyncQuery = self.collection
        for field_filter in self.concat_filters(self.base_filters, filters):
            query = query.where(filter=field_filter)
        return query

    async def get_by_id(self, document_id: str) -> DocumentModel:
        """Load one document by ID.

        ``base_filters`` are not applied: a direct document read cannot be
        combined with query filters.

        Args:
            document_id (str): Document ID.

        Returns:
            DocumentModel: The matching document.

        Raises:
            NotFound: If the document does not exist.

        """
        snapshot = await self.collection.document(document_id).get()
        if not snapshot.exists:
            raise NotFound(f"Document {document_id!r} not found in {self.collection.id!r}")

        return self.to_model(snapshot)

    async def get_total(self, filters: FirestoreFiltersType = None) -> int:
        """Count documents matching filters with a server-side aggregation.

        Args:
            filters (FirestoreFiltersType, optional): Extra filters merged with
                ``base_filters``. Defaults to None.

        Returns:
            int: Number of matching documents.

        """
        result = await self._build_query(filters).count().get()
        return int(result[0][0].value)

    async def get_all(
        self,
        limit: int | None = 100,
        offset: int | None = 0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] = "asc",
        filters: FirestoreFiltersType = None,
    ) -> tuple[list[DocumentModel], int]:
        """List documents with pagination, sorting, and optional filters.

        Firestore bills skipped documents as reads, so large offsets are
        costly; prefer narrowing with filters for deep pages.

        Args:
            limit (int | None, optional): Maximum documents to return.
                Defaults to 100.
            offset (int | None, optional): Documents to skip. Defaults to 0.
            sort_by (str | None, optional): Field to sort by; :attr:`id_field`
                sorts by document ID. Defaults to None (Firestore's default
                document ID order).
            sort_order (Literal["asc", "desc"], optional): Sort direction.
                Defaults to ``"asc"``.
            filters (FirestoreFiltersType, optional): Extra filters merged with
                ``base_filters``. Defaults to None.

        Returns:
            tuple[list[DocumentModel], int]: Page of documents and total count
                (count uses the same filters, without limit/offset).

        """
        query = self._build_query(filters)
        total = await self.get_total(filters)

        if sort_by:
            field_path = DOCUMENT_ID_FIELD_PATH if sort_by == self.id_field else sort_by
            direction = AsyncQuery.ASCENDING if sort_order == "asc" else AsyncQuery.DESCENDING
            query = query.order_by(field_path, direction=direction)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        snapshots = await query.get()
        return [self.to_model(snapshot) for snapshot in snapshots], total

    async def create(self, **kwargs: Any) -> DocumentModel:
        """Validate and insert a new document.

        Args:
            **kwargs (Any): Field values for the new model.

        Returns:
            DocumentModel: The stored document.

        Raises:
            Conflict: If a document with ``document_id`` already exists.

        """
        reference = self.collection.document(str(uuid4()))
        model = self.document_model.model_validate({**kwargs, self.id_field: reference.id})
        await reference.create(self.to_document(model))
        return model

    async def update(self, document_id: str, **kwargs: Any) -> DocumentModel:
        """Validate and apply a partial update to one document.

        The merged document is validated against :attr:`document_model`, but
        only the fields in ``kwargs`` are written.

        Args:
            document_id (str): Document ID.
            **kwargs (Any): Field values to set; if empty, only loads the
                document.

        Returns:
            DocumentModel: The document after the update.

        Raises:
            NotFound: If the document does not exist.
            ValueError: If ``kwargs`` tries to change :attr:`id_field`.

        """
        current = await self.get_by_id(document_id)
        if not kwargs:
            return current
        if self.id_field in kwargs:
            raise ValueError(f"{self.id_field!r} cannot be updated")

        model = self.document_model.model_validate({**current.model_dump(), **kwargs})
        document = self.to_document(model)
        await self.collection.document(document_id).update({key: document[key] for key in kwargs})
        return model

    async def delete(self, document_id: str) -> bool:
        """Delete one document by ID.

        Args:
            document_id (str): Document ID.

        Returns:
            bool: Always ``True`` after a successful delete.

        Raises:
            NotFound: If the document does not exist.

        """
        reference = self.collection.document(document_id)
        # Firestore deletes are no-ops for missing documents; require existence
        # so callers get the same NotFound as ``get_by_id`` and ``update``.
        await reference.delete(option=self.firestore_client.client.write_option(exists=True))
        return True
