"""CLI for managing passwords of the Keychain Application."""

__all__ = ("password",)

import json

import asyncclick as click

from keychain.config import AppConfig
from keychain.modules.routers.models.request.password import PasswordCreateRequestModel, PasswordUpdateRequestModel
from keychain.modules.routers.models.response.password import PasswordGetResponseModel, SimplePasswordGet
from keychain.services.cryptography.client import CryptographyClient
from keychain.services.daos import PasswordDAO
from keychain.services.db_client.client import DBClient
from keychain.services.db_client.models.password import Password


@click.group(help="CLI for managing passwords of the Keychain Application.")
@click.pass_context
def password(ctx: click.Context) -> None:
    """Initialize the password CLI group for the Keychain Application.

    This function serves as the root command group for all password CLI
    operations.

    Args:
        ctx (click.Context): Click context object containing the app config.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    cryptography_client = CryptographyClient(config)
    ctx.obj["cryptography_client"] = cryptography_client


@password.command(help="Create a new password")
@click.option("--name", help="The name of the password", required=True, type=str)
@click.option("--user-id", help="The ID of the user who owns the password", required=True, type=int)
@click.option("--image-url", help="The URL of the image associated with the password", type=str, required=False)
@click.pass_context
async def create_password(ctx: click.Context, name: str, user_id: int, image_url: str | None) -> None:
    """Create a new password in the database.

    This command creates a new password record in the database and outputs the
    created password information as JSON.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        name (str): The name of the password to create.
        user_id (int): The unique identifier of the user who owns the password.
        image_url (str, optional): URL of the image associated with the
            password. Defaults to None.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    password_dao = PasswordDAO(db_client)
    body = PasswordCreateRequestModel(name=name, image_url=image_url)
    password = await password_dao.create(**body.model_dump(), user_id=user_id)
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Get a password by ID")
@click.option("--password-id", help="The ID of the password", type=int, required=True)
@click.pass_context
async def get_password(ctx: click.Context, password_id: int) -> None:
    """Retrieve a password from the database by its ID.

    This command fetches a password record by ID and outputs the password
    information as JSON.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        password_id (int): The unique identifier of the password to retrieve.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    password_dao = PasswordDAO(db_client)
    password = await password_dao.get_by_pk(password_id)
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Update a password by ID")
@click.option("--password-id", help="The ID of the password", type=int, required=True)
@click.option("--name", help="The new name of the password", type=str, required=True)
@click.option("--image-url", help="The new image URL of the password", type=str, required=False)
@click.pass_context
async def update_password(ctx: click.Context, password_id: int, name: str, image_url: str | None) -> None:
    """Update a password's name and/or image URL in the database.

    This command updates the name and/or image URL of an existing password
    identified by its ID and outputs the updated password information as JSON.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        password_id (int): The unique identifier of the password to update.
        name (str): The new name to assign to the password.
        image_url (str, optional): New image URL to assign to the password.
            Defaults to None.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    password_dao = PasswordDAO(db_client)
    body = PasswordUpdateRequestModel(name=name, image_url=image_url)
    password = await password_dao.update(password_id, **body.model_dump())
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Delete a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=int)
@click.pass_context
async def delete_password(ctx: click.Context, password_id: int) -> None:
    """Delete a password from the database by its ID.

    This command permanently removes a password record from the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        password_id (int): The unique identifier of the password to delete.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    password_dao = PasswordDAO(db_client)
    await password_dao.delete(password_id)
    click.echo(f"Password with id {password_id} deleted successfully")


@password.command(help="List all passwords for a user")
@click.option("--user-id", help="The ID of the user who owns the password", type=int, required=False)
@click.pass_context
async def list_passwords(ctx: click.Context, user_id: int | None) -> None:
    """List all passwords, optionally filtered by owner.

    This command retrieves passwords from the database and outputs them as a
    JSON array. When a user ID is provided, only that user's passwords are
    returned. Each password includes its ID and name.

    Args:
        ctx (click.Context): Click context object containing the DB client.
        user_id (int, optional): The unique identifier of the user whose
            passwords to list. Defaults to None.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    password_dao = PasswordDAO(db_client)
    filters = [] if user_id is None else [Password.user_id == user_id]
    passwords, _ = await password_dao.get_all(filters=filters)
    password_responses = [SimplePasswordGet.model_validate(pwd) for pwd in passwords]
    click.echo(json.dumps([pwd.model_dump() for pwd in password_responses], indent=2))
