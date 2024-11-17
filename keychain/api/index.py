from __future__ import annotations

from logging import getLogger
from typing import override

from flask import Response, g, request
from flask_appbuilder import IndexView
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.baseviews import expose
from flask_appbuilder.const import API_RESULT_RES_KEY, LOGMSG_WAR_DBI_EDIT_INTEGRITY
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_login import login_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from keychain.database.models import Field, Password

logger = getLogger(__name__)


def get_user_id() -> int | None:
    """
    Retrieves the user ID from the current user object.

    Returns:
        int | None: The user ID if available, otherwise None.
    """

    return getattr(g.user, "id", None)


class KeychainIndexView(IndexView):
    index_template = "index.html"

    @expose("/")
    @login_required
    @override
    def index(self):
        self.update_redirect()
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class PasswordModelApi(ModelRestApi):
    resource_name = "password"
    datamodel = SQLAInterface(Password)
    allow_browser_login = True
    exclude_route_methods = {"delete"}
    base_filters = [["user_id", FilterEqualFunction, get_user_id]]
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

        try:
            new_data = self._merge_update_item(item, request.json)
            new_data[Field.value.key] = item.get_value()
            new_item = self.add_model_schema.load(new_data)
            item = self.edit_model_schema.load(
                {Field.is_deleted.key: True}, instance=item
            )
        except ValidationError as err:
            return self.response_422(message=err.messages)
        self.pre_update(item)
        self.pre_add(new_item)
        try:
            self.datamodel.add_and_edit(
                to_add=new_item, to_edit=item, raise_exception=True
            )
            self.post_update(item)
            self.post_add(new_item)
            return self.response(
                201,
                **{
                    API_RESULT_RES_KEY: self.show_model_schema.dump(
                        [item, new_item], many=True
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

        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            return self.response_404()
        try:
            item = self.edit_model_schema.load(
                {Field.is_deleted.key: True}, instance=item
            )
        except ValidationError as err:
            return self.response_422(message=err.messages)
        self.pre_delete(item)
        try:
            self.datamodel.edit(item, raise_exception=True)
            self.post_delete(item)
            return self.response(
                200,
                **{API_RESULT_RES_KEY: self.edit_model_schema.dump(item, many=False)},
            )
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))
