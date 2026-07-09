"""Types for the base DAO."""

__all__ = ("AcceptableFiltersType",)

from typing import Any, Sequence

from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.elements import BinaryExpression

from keychain.utils.filter import Filter

AcceptableFiltersType = (
    Sequence[ColumnElement[bool]]
    | Sequence[BinaryExpression[bool]]
    | Sequence[dict[str, Any]]
    | Sequence[Filter[str]]
    | None
)
