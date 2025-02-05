"""initial

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
    op.create_table(
        "password",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.now),
        sa.Column(
            "image_url", sa.String(256), nullable=True, default="/static/i/no-photo.png"
        ),
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


def downgrade() -> None:
    op.drop_table("password")
    op.drop_table("field")
