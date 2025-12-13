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
from sqlalchemy.orm import DeclarativeBase, Session

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

    id: int = sa.Column(sa.Integer, primary_key=True)
    name: str = sa.Column(sa.String, nullable=False, unique=False)
    name_temp: str = sa.Column(sa.String, nullable=True, unique=False)


def upgrade() -> None:
    """Upgrade the database schema.

    Removes the unique constraint from the 'name' column by:
    1. Adding a temporary 'name_temp' column
    2. Copying all data from 'name' to 'name_temp'
    3. Dropping the original 'name' column (which has the unique constraint)
    4. Renaming 'name_temp' to 'name' and making it non-nullable without unique constraint
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("name_temp", sa.String, nullable=True, unique=False))

    session.query(Password).update({Password.name_temp: Password.name})

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.drop_column("name")
        batch_op.alter_column("name_temp", new_column_name="name", nullable=False, unique=False)


def downgrade() -> None:
    """Downgrade the database schema.

    This migration cannot be reversed as restoring the unique constraint would fail
    if duplicate names exist in the database. The downgrade function is intentionally
    left empty (no-op).
    """
    pass
