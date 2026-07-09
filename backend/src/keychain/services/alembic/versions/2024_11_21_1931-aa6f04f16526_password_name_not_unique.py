"""Password name not unique.

This migration removes the unique constraint from the 'name' column in the 'password' table,
allowing multiple passwords to have the same name. This is done by recreating the column
without the unique constraint.

Revision ID: aa6f04f16526
Revises: 51c70769c18a
Create Date: 2024-11-21 19:31:09.323648

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# revision identifiers, used by Alembic.
revision: str = "aa6f04f16526"
down_revision: str | None = "51c70769c18a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models.

    Used to define the Password model for querying during migration.
    """

    pass


class Password(Base):
    """Temporary model for the 'password' table.

    Used during migration to copy data from the 'name' column to a temporary column
    before recreating the column without the unique constraint.

    Attributes:
        id: Primary key identifier for the password
        name: The password name (without unique constraint after migration)
        name_temp: Temporary column used during migration to store name values

    """

    __tablename__ = "password"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False, unique=False)


def upgrade() -> None:
    """Drop the unique constraint on ``password.name``.

    Removes the ``uq_password_name`` constraint so multiple passwords may share
    the same name.

    Returns:
        None

    """
    op.drop_constraint("uq_password_name", "password", type_="unique")


def downgrade() -> None:
    """Restore the unique constraint on ``password.name``.

    Recreates the ``uq_password_name`` constraint. This fails if duplicate
    names already exist in the table.

    Returns:
        None

    """
    op.create_unique_constraint("uq_password_name", "password", ["name"])
