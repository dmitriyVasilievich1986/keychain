"""Constants for the Firestore DAOs."""

__all__ = ("DOCUMENT_ID_FIELD_PATH", "OPERATORS", "FirestoreFiltersType")

from typing import Any, Sequence

from google.cloud.firestore_v1.base_query import FieldFilter

from keychain.utils.filter import Filter

# Filters accepted by the Firestore DAOs: raw ``FieldFilter`` instances,
# ``Filter`` models, or dicts validated as ``Filter``.
FirestoreFiltersType = Sequence[FieldFilter] | Sequence[dict[str, Any]] | Sequence[Filter[str]] | None

# Firestore's reserved field path for ordering by document ID.
DOCUMENT_ID_FIELD_PATH = "__name__"

# ``Filter`` operators mapped to Firestore query operators; ``like``/``ilike``
# have no Firestore equivalent and are rejected.
OPERATORS: dict[str, str] = {
    "eq": "==",
    "ge": ">=",
    "gt": ">",
    "le": "<=",
    "lt": "<",
    "in": "in",
    "isnull": "==",
    "notnull": "!=",
}
