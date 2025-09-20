from logging import getLogger
from typing import override

from flask import request, Response
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from keychain.api.field.schemas import PasswordValidator
from keychain.api.field.sqla_interface import FieldSQLAInterface
from keychain.api.get_user_id import get_user_id
from keychain.models import Field

logger = getLogger(__name__)


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
        """Handles a POST request for creating a new item in a headless (API-only) manner.

        Validates that the request contains JSON data, deserializes it using the model schema,
        and performs pre-add logic. Attempts to add the item to the data model, handling
        validation and integrity errors appropriately. On success, returns a 201 response
        with the serialized item.

        Returns:
            Response: A Flask response object with appropriate status code and message.
                - 400 if the request is not JSON.
                - 422 if validation or integrity errors occur.
                - 201 with the created item if successful.

        """
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
        """Update an item in the keychain API.

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
            self.datamodel.add_and_edit(to_add=new_item, to_edit=item, raise_exception=True)
            self.post_update(item)
            self.post_add(new_item)
            pk = self.datamodel.get_pk_value(new_item)
            response_item = self.datamodel.get(pk, self._base_filters)
            return self.response(
                201,
                **{API_RESULT_RES_KEY: self.show_model_schema.dump(response_item, many=False)},
            )
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))

    @override
    def delete_headless(self, pk: str | int) -> Response:
        """Deletes a resource without returning a response body.

        Args:
            pk (str | int): The primary key of the resource to delete.

        Returns:
            Response: The response object.

        """
        item: Field = self.datamodel.get(pk, self._base_filters)
        if not item:  # pylint: disable=consider-using-assignment-expr
            return self.response_404()

        item.is_deleted = True
        self.pre_delete(item)
        try:
            self.datamodel.edit(item, raise_exception=True)
            self.post_delete(item)
            return self.response(200, message="OK")
        except IntegrityError as e:
            return self.response_422(message=str(e.orig))
