"""Change 'Field' value field data type.

Revision ID: 56fda1ef4adc
Revises: 85a3c034b32b
Create Date: 2024-11-16 20:17:06.978705

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from flask_appbuilder import Model
from sqlalchemy.orm import Session


class Field(Model):
    __tablename__ = "field"

    password_id = sa.Column(sa.Integer, nullable=True)


# revision identifiers, used by Alembic.
revision: str = "56fda1ef4adc"
down_revision: Union[str, None] = "85a3c034b32b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute("DELETE FROM field WHERE password_id IS NULL")

    with op.batch_alter_table("field", recreate="always") as batch_op:
        batch_op.alter_column("value", type_=sa.String, existing_type=sa.BINARY)
        batch_op.alter_column("password_id", nullable=False, existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("field", recreate="always") as batch_op:
        batch_op.alter_column("value", type_=sa.BINARY, existing_type=sa.String)
        batch_op.alter_column("password_id", nullable=True, existing_nullable=False)
