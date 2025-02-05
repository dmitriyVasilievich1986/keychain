"""Add user_id to 'Password' model

Revision ID: 51c70769c18a
Revises: 56fda1ef4adc
Create Date: 2024-11-17 20:39:38.678721

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "51c70769c18a"
down_revision: str | None = "56fda1ef4adc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    user_id = session.query(User).first().id

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer, nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_password_user_id_user"),
            User.__tablename__,
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    session.execute(f"UPDATE password SET user_id = {user_id}")

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.alter_column("user_id", nullable=False, existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.drop_column("user_id")
