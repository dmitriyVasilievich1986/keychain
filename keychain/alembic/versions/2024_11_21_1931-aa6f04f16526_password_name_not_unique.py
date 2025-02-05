"""Password name not unique

Revision ID: aa6f04f16526
Revises: 51c70769c18a
Create Date: 2024-11-21 19:31:09.323648

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "aa6f04f16526"
down_revision: str | None = "51c70769c18a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column("name_temp", sa.String, nullable=True, unique=False)
        )

    session.execute("UPDATE password SET name_temp = name")

    with op.batch_alter_table("password", recreate="always") as batch_op:
        batch_op.drop_column("name")
        batch_op.alter_column(
            "name_temp", new_column_name="name", nullable=False, unique=False
        )


def downgrade() -> None:
    pass
