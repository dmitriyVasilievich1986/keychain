"""Initial database migration.

This migration creates the initial database schema for the keychain application,
including tables for users, passwords, and password fields.

Revision ID: 85a3c034b32b
Revises:
Create Date: 2024-11-09 20:01:01.577671

"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import relationship

# revision identifiers, used by Alembic.
revision: str = "85a3c034b32b"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade the database schema.

    Creates the initial database tables:
    - password: Stores password entries with name, creation date, and image URL
    - field: Stores encrypted field values associated with passwords
    - user: Stores user accounts with name and password hash
    """
    op.create_table(
        "password",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now),
        sa.Column("image_url", sa.String(256), nullable=True, default="/static/i/no-photo.png"),
        relationship("fields", cascade="all, delete-orphan", backref="password"),
    )
    op.create_table(
        "field",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("value", sa.BINARY, nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("password_id", sa.Integer, sa.ForeignKey("password.id")),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    """Downgrade the database schema.

    Removes all tables created in the upgrade function:
    - Drops the password table
    - Drops the field table
    - Note: user table is not dropped (may be intentional or oversight)
    """
    op.drop_table("password")
    op.drop_table("field")
