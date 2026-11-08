"""Exceptions for the data access objects."""

__all__ = ("EncryptionKeysMissingError", "InvalidPasswordError")


class InvalidPasswordError(ValueError):
    """Raised when the provided current password of a user is incorrect."""


class EncryptionKeysMissingError(ValueError):
    """Raised when a user has no per-user encryption keys yet.

    Such users must be migrated with ``MigrateFieldsEncryptionCommand`` first.
    """
