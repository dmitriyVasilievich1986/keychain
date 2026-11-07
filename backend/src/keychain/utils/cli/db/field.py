"""CLI for managing fields of the Keychain Application."""

__all__ = ("field",)

import json

import asyncclick as click

from keychain.config import AppConfig
from keychain.modules.routers.models.request.field import FieldCreateRequestModel, FieldUpdateRequestModel
from keychain.modules.routers.models.response.field import FieldGetResponseModel, SimpleFieldGet
from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos import FieldDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.password import Password
from keychain.utils.cli.user_dek import load_user_dek


@click.group(help="CLI for managing fields of the Keychain Application.")
@click.pass_context
def field(ctx: click.Context) -> None:
    """Initialize the field CLI group for the Keychain Application.

    This function serves as the root command group for all field CLI
    operations. It builds the cryptography client from the app config and
    stores it on the context for use by subcommands.

    Args:
        ctx (click.Context): Click context object containing the app config
            and used to share the cryptography client with subcommands.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    cryptography_client = CryptographyClient(config)
    ctx.obj["cryptography_client"] = cryptography_client


@field.command(help="Create a new field")
@click.option("--name", help="The name of the field", type=str, required=True)
@click.option(
    "--value",
    prompt="Enter the field value",
    help="The value of the field",
    type=str,
    required=True,
    hide_input=True,
    confirmation_prompt=True,
)
@click.option("--password-id", help="The ID of the password that owns the field", type=int, required=True)
@click.option("--user-id", help="The ID of the user who owns the password", type=int, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def create_field(
    ctx: click.Context, name: str, value: str, password_id: int, user_id: int, user_password: str
) -> None:
    """Create a new field in the database.

    This command creates a new field record in the database and outputs the
    created field information as JSON.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        name (str): The name of the field to create.
        value (str): The value of the field to create (encrypted before
            storage).
        password_id (int): The unique identifier of the password that owns the
            field.
        user_id (int): The unique identifier of the user who owns the password.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client)
    body = FieldCreateRequestModel(name=name, value=value, password_id=password_id)
    dek = await load_user_dek(db_client, user_id, user_password)
    field = await field_dao.create(**body.model_dump(), filters=[Password.user_id == user_id], dek=dek)
    field_response = FieldGetResponseModel.model_validate(field, context={"dek": dek})
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Get a field by ID")
@click.option("--field-id", help="The ID of the field", type=int, required=True)
@click.option("--user-id", help="The ID of the user who owns the field", type=int, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def get_field(ctx: click.Context, field_id: int, user_id: int, user_password: str) -> None:
    """Retrieve a field from the database by its ID.

    This command fetches a field record by ID and outputs the field information
    as JSON.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        field_id (int): The unique identifier of the field to retrieve.
        user_id (int): The unique identifier of the user who owns the field.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client)
    dek = await load_user_dek(db_client, user_id, user_password)
    field = await field_dao.get_by_pk(field_id, filters=[Password.user_id == user_id])
    field_response = FieldGetResponseModel.model_validate(field, context={"dek": dek})
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Update a field by ID")
@click.option("--field-id", help="The ID of the field", type=int, required=True)
@click.option(
    "--value",
    prompt="Enter the new field value",
    help="The new value of the field",
    type=str,
    required=True,
    hide_input=True,
    confirmation_prompt=True,
)
@click.option("--user-id", help="The ID of the user who owns the field", type=int, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def update_field(ctx: click.Context, field_id: int, value: str, user_id: int, user_password: str) -> None:
    """Update a field's value in the database.

    This command updates the value of an existing field identified by its ID
    and outputs the updated field information as JSON. Note that updating a
    field creates a new field record and marks the old one as deleted.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        field_id (int): The unique identifier of the field to update.
        value (str): The new value to assign to the field (encrypted before
            storage).
        user_id (int): The unique identifier of the user who owns the field.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client)
    body = FieldUpdateRequestModel(value=value)
    dek = await load_user_dek(db_client, user_id, user_password)
    field = await field_dao.update(field_id, **body.model_dump(), filters=[Password.user_id == user_id], dek=dek)
    field_response = FieldGetResponseModel.model_validate(field, context={"dek": dek})
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Delete a field by ID")
@click.option("--field-id", help="The ID of the field", type=int, required=True)
@click.pass_context
async def delete_field(ctx: click.Context, field_id: int) -> None:
    """Delete a field from the database by its ID.

    This command permanently marks a field record as deleted in the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        field_id (int): The unique identifier of the field to delete.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client)
    await field_dao.delete(field_id)
    click.echo(f"Field with id {field_id} deleted successfully")


@field.command(help="List all fields for a user")
@click.option("--user-id", help="The ID of the user who owns the field", type=int, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def list_fields(ctx: click.Context, user_id: int, user_password: str) -> None:
    """List all fields of a user.

    This command retrieves the fields owned by a user and outputs them as a
    JSON array. Each field includes its ID, name, deletion status and
    decrypted value.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        user_id (int): The unique identifier of the user whose fields to list.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client)
    dek = await load_user_dek(db_client, user_id, user_password)
    fields, _ = await field_dao.get_all(filters=[Password.user_id == user_id])
    field_responses = [SimpleFieldGet.model_validate(field, context={"dek": dek}) for field in fields]
    click.echo(json.dumps([field.model_dump() for field in field_responses], indent=2))
