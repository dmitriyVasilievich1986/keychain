"""Types for the base DAO."""

__all__ = ("AcceptableFiltersType",)

from typing import Any

from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.elements import BinaryExpression

from keychain.utils.filter import Filter

AcceptableFiltersType = (
    list[ColumnElement[bool]] | list[BinaryExpression[bool]] | list[dict[str, Any]] | list[Filter[str]] | None
)
