"""Initial database migration.

This migration creates the initial database schema for the keychain application,
including tables for users, passwords, and password fields.

Revision ID: 85a3c034b32b
Revises:
Create Date: 2024-11-09 20:01:01.577671

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85a3c034b32b"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial database tables.

    Creates the ``password``, ``field``, and ``user`` tables that make up
    the initial schema for the keychain application.

    Returns:
        None

    """
    op.create_table(
        "password",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("image_url", sa.String(255), nullable=True, server_default="/static/i/no-photo.png"),
        sa.PrimaryKeyConstraint("id", name="pk_password"),
        sa.UniqueConstraint("name", name="uq_password_name"),
    )
    op.create_table(
        "field",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("is_deleted", sa.Boolean, server_default=sa.text("false")),
        sa.Column("password_id", sa.Integer),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_field"),
        sa.ForeignKeyConstraint(["password_id"], ["password.id"], name="fk_field_password", ondelete="CASCADE"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_user"),
        sa.UniqueConstraint("name", name="uq_user_name"),
    )


def downgrade() -> None:
    """Drop the tables created by the upgrade.

    Removes the ``password``, ``field``, and ``user`` tables, reverting the
    schema to its state before this migration.

    Returns:
        None

    """
    op.drop_table("user")
    op.drop_table("field")
    op.drop_table("password")
