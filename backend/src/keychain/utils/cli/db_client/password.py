"""CLI for managing passwords of the Keychain Application."""

__all__ = ["password"]

import asyncio
import json

import click

from keychain.modules.routers.models.response import PasswordGetResponseModel, PasswordGetResponseModelSimple
from keychain.services.daos import PasswordDAO


@click.group(help="CLI for managing passwords of the Keychain Application.")
def password() -> None:
    """Initialize the password CLI group for the Keychain Application.

    This function serves as the root command group for all password CLI operations.
    """
    pass


@password.command(help="Create a new password")
@click.option("--name", prompt="Enter the password name", help="The name of the password")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user who owns the password", type=int)
@click.option("--image-url", default=None, help="The URL of the image associated with the password")
@click.pass_context
def create_password(ctx: click.Context, name: str, user_id: int, image_url: str | None) -> None:
    """Create a new password in the database.

    This command prompts for a password name and user ID, creates a new password
    record in the database, and outputs the created password information as JSON.

    Args:
        ctx: Click context object containing the password DAO.
        name: The name of the password to create.
        user_id: The unique identifier of the user who owns the password.
        image_url: Optional URL of the image associated with the password.

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    password = asyncio.run(password_dao.create(name, user_id, image_url))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Get a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=int)
@click.pass_context
def get_password(ctx: click.Context, password_id: int) -> None:
    """Retrieve a password from the database by its ID.

    This command fetches a password record by ID and outputs the password information
    as JSON. If the password does not exist, an error will be raised.

    Args:
        ctx: Click context object containing the password DAO.
        password_id: The unique identifier of the password to retrieve.

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    password = asyncio.run(password_dao.get_by_id(password_id))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Update a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=int)
@click.option("--name", prompt="Enter the new name", help="The new name of the password")
@click.option("--image-url", default=None, help="The new image URL of the password")
@click.pass_context
def update_password(ctx: click.Context, password_id: int, name: str, image_url: str | None) -> None:
    """Update a password's name and/or image URL in the database.

    This command updates the name and/or image URL of an existing password identified
    by its ID and outputs the updated password information as JSON.

    Args:
        ctx: Click context object containing the password DAO.
        password_id: The unique identifier of the password to update.
        name: The new name to assign to the password.
        image_url: Optional new image URL to assign to the password.

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    password = asyncio.run(password_dao.update(password_id, name, image_url))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Delete a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=int)
@click.pass_context
def delete_password(ctx: click.Context, password_id: int) -> None:
    """Delete a password from the database by its ID.

    This command permanently removes a password record from the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx: Click context object containing the password DAO.
        password_id: The unique identifier of the password to delete.

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    asyncio.run(password_dao.delete(password_id))
    click.echo(f"Password with id {password_id} deleted successfully")


@password.command(help="List all passwords")
@click.pass_context
def list_passwords(ctx: click.Context) -> None:
    """List all passwords in the database.

    This command retrieves all passwords from the database and outputs them
    as a JSON array. Each password includes its ID and name.

    Args:
        ctx: Click context object containing the password DAO.

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    passwords = asyncio.run(password_dao.get_all())
    password_responses = [
        PasswordGetResponseModelSimple.model_validate({"id": pwd.id, "name": pwd.name}) for pwd in passwords
    ]
    click.echo(json.dumps([pwd.model_dump() for pwd in password_responses], indent=2))
