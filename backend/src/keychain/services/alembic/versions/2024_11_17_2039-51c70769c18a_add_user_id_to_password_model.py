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
from sqlalchemy.orm import DeclarativeBase, Session

# revision identifiers, used by Alembic.
revision: str = "51c70769c18a"
down_revision: str | None = "56fda1ef4adc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models.

    Used to define the User and Password models for querying during migration.
    """

    pass


class User(Base):
    """Temporary model for the 'user' table.

    Used during migration to query the first user for assigning existing passwords.

    Attributes:
        id: Primary key identifier for the user

    """

    __tablename__ = "user"

    id: int = sa.Column(sa.Integer, primary_key=True)


class Password(Base):
    """Temporary model for the 'password' table.

    Used during migration to update existing password records with user_id values.

    Attributes:
        id: Primary key identifier for the password
        user_id: Foreign key reference to the user table

    """

    __tablename__ = "password"

    id: int = sa.Column(sa.Integer, primary_key=True)
    user_id: int | None = sa.Column(sa.Integer, nullable=False)


def upgrade() -> None:
    """Upgrade the database schema.

    Performs the following operations:
    1. Verifies that at least one user exists in the database
    2. Adds a nullable 'user_id' column to the 'password' table
    3. Creates a foreign key constraint linking password.user_id to user.id with CASCADE delete
    4. Assigns all existing passwords to the first user in the database
    5. Makes the 'user_id' column non-nullable

    Raises:
        ValueError: If no users exist in the database

    """
    bind = op.get_bind()
    session = Session(bind=bind)
    user = session.query(User).first()
    if user is None:
        raise ValueError("To proceed, please create at least one user.")

    user_id = user.id

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer, nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_password_user_id_user"),
            "user",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    session.query(Password).update({Password.user_id: user_id})

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.alter_column("user_id", nullable=False, existing_nullable=True)


def downgrade() -> None:
    """Downgrade the database schema.

    Removes the user_id column and its foreign key constraint from the 'password' table,
    reverting the password table to its previous state without user association.
    """
    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.drop_column("user_id")
