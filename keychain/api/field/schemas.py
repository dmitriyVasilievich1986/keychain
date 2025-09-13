import sqlalchemy as sa
from marshmallow import fields, Schema, ValidationError
from marshmallow.validate import Validator

from keychain import db
from keychain.api.get_user_id import get_user_id
from keychain.models import Password


class FieldDeleteSchema(Schema):
    is_deleted = fields.Bool()


class PasswordValidator(Validator):  # pylint: disable=too-few-public-methods
    def __call__(self, value: str) -> None:
        """
        Validates the given value.

        Args:
            value (str): The value to validate.

        Raises:
            ValidationError: If the value is not valid.
        """

        password = (
            db.session.query(Password)  # pylint: disable=no-member
            .filter(sa.and_(Password.id == value, Password.user_id == get_user_id()))
            .one_or_none()
        )
        if password is None:
            raise ValidationError("Password not found")
