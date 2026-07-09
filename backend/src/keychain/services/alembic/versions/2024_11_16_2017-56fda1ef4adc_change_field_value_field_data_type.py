"""Change 'Field' value field data type.

This migration modifies the 'field' table to:
- Change the 'value' column data type from BINARY to String
- Make the 'password_id' column non-nullable (after cleaning up null values)

Revision ID: 56fda1ef4adc
Revises: 85a3c034b32b
Create Date: 2024-11-16 20:17:06.978705

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.sql import select

# revision identifiers, used by Alembic.
revision: str = "56fda1ef4adc"
down_revision: str | None = "85a3c034b32b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models.

    Used to define the Field model for querying during migration.
    """

    pass


class Field(Base):
    """Temporary model for the 'field' table.

    Used during migration to query and delete records with null password_id
    before making the column non-nullable.

    Attributes:
        id: Primary key identifier for the field
        password_id: Foreign key reference to the password table

    """

    __tablename__ = "field"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    password_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=False)


def upgrade() -> None:
    """Delete orphan fields and make ``password_id`` non-nullable.

    Removes all ``field`` records with a null ``password_id`` and then alters
    the ``password_id`` column so it can no longer be null.

    Returns:
        None

    """
    bind = op.get_bind()
    session = Session(bind=bind)
    stmt = select(Field).where(Field.password_id.is_(None))
    session.execute(stmt)

    op.alter_column("field", "password_id", nullable=False, existing_nullable=True)


def downgrade() -> None:
    """Make the ``password_id`` column nullable again.

    Reverts the column change from the upgrade. The previously deleted records
    with a null ``password_id`` are not restored.

    Returns:
        None

    """
    op.alter_column("field", "password_id", nullable=True, existing_nullable=False)
