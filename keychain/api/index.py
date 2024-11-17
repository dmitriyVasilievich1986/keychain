from __future__ import annotations

from logging import getLogger
from typing import override

from flask import Response, request
from flask_appbuilder import IndexView
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.const import API_RESULT_RES_KEY, LOGMSG_WAR_DBI_EDIT_INTEGRITY
from flask_appbuilder.models.sqla.interface import SQLAInterface
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from keychain.database.models import Field, Password

logger = getLogger(__name__)


class KeychainIndexView(IndexView):
    index_template = "index.html"


class PasswordModelApi(ModelRestApi):
    resource_name = "password"
    datamodel = SQLAInterface(Password)
    allow_browser_login = True
    exclude_route_methods = {"delete"}
    edit_columns = [
        Password.name.key,
    ]


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


class FieldModelApi(ModelRestApi):
    resource_name = "field"
    datamodel: FieldSQLAInterface = FieldSQLAInterface(Field)
    allow_browser_login = True
    edit_columns = [
        Field.value.key,
        Field.is_deleted.key,
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

    @override
    def put_headless(self, pk: str | int) -> Response:  # noqa: C901
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

        value = request.json.get(Field.value.key)
        if value is not None and not item.check(value):
            json_data = {Field.is_deleted.key: True, Field.value.key: item.get_value}
            new_data = {
                Field.value.key: value,
                Field.name.key: item.name,
                Field.password_id.key: item.password_id,
            }
        else:
            json_data = {
                Field.value.key: item.get_value,
                Field.is_deleted.key: request.json.get(
                    Field.is_deleted.key, item.is_deleted
                ),
            }
            new_data = None

        try:
            data = self._merge_update_item(item, json_data)
            item = self.edit_model_schema.load(data, instance=item)
            new_item = new_data and self.add_model_schema.load(new_data)
        except ValidationError as err:
            return self.response_422(message=err.messages)
        self.pre_update(item)
        if new_item is not None:
            self.pre_add(new_item)
        try:
            self.datamodel.add_and_edit(
                to_add=new_item, to_edit=item, raise_exception=True
            )
            self.post_update(item)
            if new_item:
                self.post_add(new_item)
                return self.response(
                    201,
                    **{
                        API_RESULT_RES_KEY: self.show_model_schema.dump(
                            [item, new_item], many=True
                        )
                    },
                )
            return self.response(
                200,
                **{API_RESULT_RES_KEY: self.show_model_schema.dump(item, many=False)},
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

        request.json = {Field.is_deleted.key: True}
        return self.put_headless(pk)
