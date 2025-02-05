from logging import getLogger
from typing import override

import sqlalchemy as sa
from flask import Response, request
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.const import API_RESULT_RES_KEY, LOGMSG_WAR_DBI_EDIT_INTEGRITY
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask_appbuilder.models.sqla.interface import SQLAInterface
from marshmallow import Schema, ValidationError, fields
from marshmallow.validate import Validator
from sqlalchemy.exc import IntegrityError

from keychain import db
from keychain.database.models import Field, Password

from .get_user_id import get_user_id

logger = getLogger(__name__)


class FieldSQLAInterface(SQLAInterface):
    def add_and_edit(
        self,
        *,
        to_edit: Field,
        raise_exception: bool = False,
        to_add: Field | None = None,
    ) -> bool:
        """
        Add and edit a field in the database.

        Args:
            to_edit (Field): The field to edit.
            raise_exception (bool, optional): Whether to raise an exception
                if an IntegrityError occurs. Defaults to False.
            to_add (Optional[Field], optional): The field to add.
                Defaults to None.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """

        try:
            if to_add is not None:
                self.session.add(to_add)
            self.session.merge(to_edit)
            self.session.commit()
            self.message = (as_unicode(self.edit_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.edit_integrity_error_message), "warning")
            logger.warning(LOGMSG_WAR_DBI_EDIT_INTEGRITY, e)
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:  # pylint: disable=broad-except
            self.message = (as_unicode(self.database_error_message), "danger")
            logger.exception("Database error")
            self.session.rollback()
            if raise_exception:
                raise e
            return False


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


class FieldDeleteSchema(Schema):
    is_deleted = fields.Bool()


class FieldModelApi(ModelRestApi):
    resource_name = "field"
    datamodel: FieldSQLAInterface = FieldSQLAInterface(Field)
    allow_browser_login = True
    base_filters = [["password.user_id", FilterEqualFunction, get_user_id]]
    edit_columns = [
        Field.value.key,
    ]
    show_columns = [
        Field.name.key,
        Field.id.key,
        Field.value.key,
        Field.is_deleted.key,
        Field.created_at.key,
        Field.password.key,  # pylint: disable=no-member
        "get_value",
    ]
    add_columns = [
        Field.name.key,
        Field.value.key,
        Field.password_id.key,
    ]
    validators_columns = {
        Field.password_id.key: PasswordValidator(),
    }

    @override
    def post_headless(self) -> Response:
        if not request.is_json:
            return self.response_400(message="Request is not JSON")
        try:
            item = self.add_model_schema.load(request.json)
        except ValidationError as err:
            return self.response_422(message=err.messages)
        self.pre_add(item)
        try:
            self.datamodel.add(item, raise_exception=True)
            self.post_add(item)
            pk = self.datamodel.get_pk_value(item)
            response_item = self.datamodel.get(pk, self._base_filters)
            return self.response(
                201,
                **{
                    API_RESULT_RES_KEY: self.show_model_schema.dump(response_item),
                },
            )
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @override
    def put_headless(self, pk: str | int) -> Response:
        """
        Update an item in the keychain API.

        Args:
            pk (str | int): The primary key of the item to be updated.

        Returns:
            Response: The response object containing the result of the update operation.
        """

        item: Field = self.datamodel.get(pk, self._base_filters)
        if not request.is_json:
            return self.response(400, **{"message": "Request is not JSON"})
        if not item:
            return self.response_404()

        new_data = {
            Field.password_id.key: item.password_id,
            Field.value.key: request.json["value"],
            Field.name.key: item.name,
        }
        try:
            new_item = self.add_model_schema.load(new_data)
        except ValidationError as err:
            return self.response_422(message=err.messages)
        item.is_deleted = True
        self.pre_update(item)
        self.pre_add(new_item)
        try:
            self.datamodel.add_and_edit(
                to_add=new_item, to_edit=item, raise_exception=True
            )
            self.post_update(item)
            self.post_add(new_item)
            pk = self.datamodel.get_pk_value(new_item)
            response_item = self.datamodel.get(pk, self._base_filters)
            return self.response(
                201,
                **{
                    API_RESULT_RES_KEY: self.show_model_schema.dump(
                        response_item, many=False
                    )
                },
            )
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @override
    def delete_headless(self, pk: str | int) -> Response:
        """
        Deletes a resource without returning a response body.

        Args:
            pk (str | int): The primary key of the resource to delete.

        Returns:
            Response: The response object.
        """

        item: Field = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self.response_404()
        item.is_deleted = True
        self.pre_delete(item)
        try:
            self.datamodel.edit(item, raise_exception=True)
            self.post_delete(item)
            return self.response(200, message="OK")
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))
