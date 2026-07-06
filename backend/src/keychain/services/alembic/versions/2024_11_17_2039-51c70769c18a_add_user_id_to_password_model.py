"""Add user_id to 'Password' model.

This migration adds a user_id foreign key column to the 'password' table,
establishing a relationship between passwords and users. All existing passwords
are assigned to the first user in the database.

Revision ID: 51c70769c18a
Revises: 56fda1ef4adc
Create Date: 2024-11-17 20:39:38.678721

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51c70769c18a"
down_revision: str | None = "56fda1ef4adc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a ``user_id`` foreign key to the ``password`` table.

    Ensures at least one user exists (creating a dummy user if needed), adds a
    ``user_id`` column with a CASCADE foreign key to ``user.id``, assigns all
    existing passwords to the first user, and makes the column non-nullable.

    Returns:
        None

    """
    op.add_column("password", sa.Column("user_id", sa.Integer, nullable=False))
    op.create_foreign_key("fk_password_user_id_user", "password", "user", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    """Remove the ``user_id`` column from the ``password`` table.

    Drops the foreign key constraint and the ``user_id`` column, reverting the
    ``password`` table to its previous state without user association.

    Returns:
        None

    """
    op.drop_constraint("fk_password_user_id_user", "password", type_="foreignkey")
    op.drop_column("password", "user_id")
