"""Add per-user encryption keys to the 'User' model.

This migration adds the ``encryption_salt`` and ``wrapped_dek`` columns to the
'user' table. Each user gets a random data encryption key (DEK) that is stored
wrapped by a key derived from the user's password. Both columns are nullable so
existing users can be migrated lazily on their next login.

Revision ID: e725d02a90a9
Revises: aa6f04f16526
Create Date: 2026-11-07 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e725d02a90a9"
down_revision: str | None = "aa6f04f16526"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the ``encryption_salt`` and ``wrapped_dek`` columns to the ``user`` table.

    Returns:
        None

    """
    op.add_column("user", sa.Column("encryption_salt", sa.LargeBinary, nullable=True))
    op.add_column("user", sa.Column("wrapped_dek", sa.String, nullable=True))


def downgrade() -> None:
    """Drop the ``encryption_salt`` and ``wrapped_dek`` columns from the ``user`` table.

    Field values of migrated users stay encrypted with their per-user keys and
    become unreadable after this downgrade.

    Returns:
        None

    """
    op.drop_column("user", "wrapped_dek")
    op.drop_column("user", "encryption_salt")
