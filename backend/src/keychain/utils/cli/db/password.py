"""CLI for managing passwords of the Keychain Application."""

__all__ = ("password",)

import json
from datetime import datetime, timezone
from uuid import UUID

import asyncclick as click

from keychain.config import AppConfig
from keychain.modules.routers.models.request.password import PasswordCreateRequestModel, PasswordPatchRequestModel
from keychain.modules.routers.models.response.password import PasswordGetResponseModel, SimplePasswordGet
from keychain.services.daos.firestore import PasswordDAO
from keychain.services.db_client.firestore import FirestoreClient
from keychain.utils.filter import Filter


@click.group(help="CLI for managing passwords of the Keychain Application.")
@click.pass_context
def password(ctx: click.Context) -> None:
    """Initialize the password CLI group for the Keychain Application.

    This function serves as the root command group for all password CLI
    operations. It builds the Firestore password DAO from the app config and
    stores it on the context for use by subcommands.

    Args:
        ctx (click.Context): Click context object containing the app config
            and used to share the password DAO with subcommands.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    ctx.obj["password_dao"] = PasswordDAO(FirestoreClient(config.db.firestore, config.google))


@password.command(help="Create a new password")
@click.option("--name", help="The name of the password", required=True, type=str)
@click.option("--user-id", help="The ID of the user who owns the password", required=True, type=click.UUID)
@click.option("--image-url", help="The URL of the image associated with the password", type=str, required=False)
@click.pass_context
async def create_password(ctx: click.Context, name: str, user_id: UUID, image_url: str | None) -> None:
    """Create a new password without fields in the database.

    This command creates a new password document and outputs the created
    password information as JSON.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        name (str): The name of the password to create.
        user_id (UUID): The unique identifier of the user who owns the password.
        image_url (str, optional): URL of the image associated with the
            password. Defaults to None.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    body = PasswordCreateRequestModel(name=name, image_url=image_url)
    password = await password_dao.create(**body.model_dump(exclude={"fields"}), fields=[], user_id=str(user_id))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Get a password by ID")
@click.option("--password-id", help="The ID of the password", type=click.UUID, required=True)
@click.pass_context
async def get_password(ctx: click.Context, password_id: UUID) -> None:
    """Retrieve a password from the database by its ID.

    This command fetches a password document by ID and outputs the password
    information as JSON.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to retrieve.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    password = await password_dao.get_by_id(str(password_id))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Update a password by ID")
@click.option("--password-id", help="The ID of the password", type=click.UUID, required=True)
@click.option("--name", help="The new name of the password", type=str, required=True)
@click.option("--image-url", help="The new image URL of the password", type=str, required=False)
@click.pass_context
async def update_password(ctx: click.Context, password_id: UUID, name: str, image_url: str | None) -> None:
    """Update a password's name and/or image URL in the database.

    This command updates the name and/or image URL of an existing password
    identified by its ID and outputs the updated password information as JSON.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to update.
        name (str): The new name to assign to the password.
        image_url (str, optional): New image URL to assign to the password.
            Defaults to None.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    body = PasswordPatchRequestModel(name=name, image_url=image_url)
    password = await password_dao.update(
        str(password_id),
        **body.model_dump(exclude={"fields"}),
        updated_at=datetime.now(timezone.utc),
    )
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Delete a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=click.UUID)
@click.pass_context
async def delete_password(ctx: click.Context, password_id: UUID) -> None:
    """Delete a password from the database by its ID.

    This command permanently removes a password document from the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to delete.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    await password_dao.delete(str(password_id))
    click.echo(f"Password with id {password_id} deleted successfully")


@password.command(help="List all passwords for a user")
@click.option("--user-id", help="The ID of the user who owns the password", type=click.UUID, required=False)
@click.pass_context
async def list_passwords(ctx: click.Context, user_id: UUID | None) -> None:
    """List all passwords, optionally filtered by owner.

    This command retrieves passwords from the database and outputs them as a
    JSON array. When a user ID is provided, only that user's passwords are
    returned.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        user_id (UUID, optional): The unique identifier of the user whose
            passwords to list. Defaults to None.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    filters = [] if user_id is None else [Filter[str](column="user_id", operator="eq", value=str(user_id))]
    passwords, _ = await password_dao.get_all(filters=filters)
    password_responses = [SimplePasswordGet.model_validate(pwd) for pwd in passwords]
    click.echo(json.dumps([pwd.model_dump(mode="json") for pwd in password_responses], indent=2))
