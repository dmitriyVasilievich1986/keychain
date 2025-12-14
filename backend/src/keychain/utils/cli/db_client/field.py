"""CLI for managing fields of the Keychain Application."""

__all__ = ["field"]

import asyncio
import json

import click

from keychain.config import AppConfig
from keychain.modules.routers.models.response import FieldGetResponseModel, FieldGetResponseModelSimple
from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos import FieldDAO
from keychain.services.db_client.client import DBClient


@click.group(help="CLI for managing fields of the Keychain Application.")
@click.pass_context
def field(ctx: click.Context) -> None:
    """Initialize the field CLI group for the Keychain Application.

    This function serves as the root command group for all field CLI operations.
    """
    config: AppConfig = ctx.obj["config"]
    cryptography_client = CryptographyClient(config)
    ctx.obj["cryptography_client"] = cryptography_client


@field.command(help="Create a new field")
@click.option("--name", prompt="Enter the field name", help="The name of the field")
@click.option("--value", prompt="Enter the field value", help="The value of the field", hide_input=True)
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the field", type=int)
@click.option(
    "--password-id", prompt="Enter the password ID", help="The ID of the password that owns the field", type=int
)
@click.pass_context
def create_field(ctx: click.Context, name: str, value: str, user_id: int, password_id: int) -> None:
    """Create a new field in the database.

    This command prompts for a field name, value, and password ID, creates a new field
    record in the database, and outputs the created field information as JSON.

    Args:
        ctx: Click context object containing the field DAO.
        name: The name of the field to create.
        value: The value of the field to create (will be encrypted before storage).
        user_id: The unique identifier of the user who owns the field.
        password_id: The unique identifier of the password that owns the field.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client, user_id)
    field = asyncio.run(field_dao.create(name, value, password_id))
    field_response = FieldGetResponseModel.model_validate(field)
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Get a field by ID")
@click.option("--field-id", prompt="Enter the field ID", help="The ID of the field", type=int)
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the field", type=int)
@click.pass_context
def get_field(ctx: click.Context, field_id: int, user_id: int) -> None:
    """Retrieve a field from the database by its ID.

    This command fetches a field record by ID and outputs the field information
    as JSON. If the field does not exist, an error will be raised.

    Args:
        ctx: Click context object containing the field DAO.
        field_id: The unique identifier of the field to retrieve.
        user_id: The unique identifier of the user who owns the field.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client, user_id)
    field = asyncio.run(field_dao.get_by_id(field_id))
    field_response = FieldGetResponseModel.model_validate(field)
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Update a field by ID")
@click.option("--field-id", prompt="Enter the field ID", help="The ID of the field", type=int)
@click.option("--value", prompt="Enter the new value", help="The new value of the field", hide_input=True)
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the field", type=int)
@click.pass_context
def update_field(ctx: click.Context, field_id: int, value: str, user_id: int) -> None:
    """Update a field's value in the database.

    This command updates the value of an existing field identified by its ID
    and outputs the updated field information as JSON. Note that updating a field
    creates a new field record and marks the old one as deleted.

    Args:
        ctx: Click context object containing the field DAO.
        field_id: The unique identifier of the field to update.
        value: The new value to assign to the field (will be encrypted before storage).
        user_id: The unique identifier of the user who owns the field.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client, user_id)
    field = asyncio.run(field_dao.update(field_id, value))
    field_response = FieldGetResponseModel.model_validate(field)
    click.echo(field_response.model_dump_json(indent=2))


@field.command(help="Delete a field by ID")
@click.option("--field-id", prompt="Enter the field ID", help="The ID of the field", type=int)
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the field", type=int)
@click.pass_context
def delete_field(ctx: click.Context, field_id: int, user_id: int) -> None:
    """Delete a field from the database by its ID.

    This command permanently marks a field record as deleted in the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx: Click context object containing the field DAO.
        field_id: The unique identifier of the field to delete.
        user_id: The unique identifier of the user who owns the field.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client, user_id)
    asyncio.run(field_dao.delete(field_id))
    click.echo(f"Field with id {field_id} deleted successfully")


@field.command(help="List all fields")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the field", type=int)
@click.pass_context
def list_fields(ctx: click.Context, user_id: int) -> None:
    """List all fields in the database.

    This command retrieves all fields from the database and outputs them
    as a JSON array. Each field includes its ID, name, and deletion status.

    Args:
        ctx: Click context object containing the field DAO.
        user_id: The unique identifier of the user who owns the field.

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    field_dao = FieldDAO(db_client, user_id)
    fields = asyncio.run(field_dao.get_all())
    field_responses = [FieldGetResponseModelSimple.model_validate(field) for field in fields]
    click.echo(json.dumps([field.model_dump() for field in field_responses], indent=2))
