"""CLI for managing users of the Keychain Application."""

__all__ = ["user"]

import asyncio

import click
from colorama import Fore, Style

from keychain.modules.routers.models.response import UserGetResponseModel
from keychain.services.daos import UserDAO


@click.group(help="CLI for managing users of the Keychain Application.")
def user() -> None:
    """Initialize the user CLI group for the Keychain Application.

    This function serves as the root command group for all user CLI operations.
    """
    pass


@user.command(help="Create a new user")
@click.option("--name", prompt="Enter your name", help="The name of the user")
@click.option(
    "--password",
    prompt="Enter your password",
    help="The password of the user",
    hide_input=True,
    confirmation_prompt=True,
)
@click.pass_context
def create_user(ctx: click.Context, name: str, password: str) -> None:
    """Create a new user in the database.

    This command prompts for a user name and password, creates a new user
    record in the database, and outputs the created user information as JSON.

    Args:
        ctx: Click context object containing the user DAO.
        name: The name of the user to create.
        password: The password for the user (will be hashed before storage).

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = asyncio.run(user_dao.create(name, password))
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Get a user by ID")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user")
@click.pass_context
def get_user(ctx: click.Context, user_id: int) -> None:
    """Retrieve a user from the database by their ID.

    This command fetches a user record by ID and outputs the user information
    as JSON. If the user does not exist, an error will be raised.

    Args:
        ctx: Click context object containing the user DAO.
        user_id: The unique identifier of the user to retrieve.

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = asyncio.run(user_dao.get_by_id(user_id))
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Update a user by ID")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user")
@click.option("--name", prompt="Enter the new name", help="The new name of the user")
@click.pass_context
def update_user(ctx: click.Context, user_id: int, name: str) -> None:
    """Update a user's name in the database.

    This command updates the name of an existing user identified by their ID
    and outputs the updated user information as JSON.

    Args:
        ctx: Click context object containing the user DAO.
        user_id: The unique identifier of the user to update.
        name: The new name to assign to the user.

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = asyncio.run(user_dao.update(user_id, name))
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Delete a user by ID")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user")
@click.pass_context
def delete_user(ctx: click.Context, user_id: int) -> None:
    """Delete a user from the database by their ID.

    This command permanently removes a user record from the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx: Click context object containing the user DAO.
        user_id: The unique identifier of the user to delete.

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    asyncio.run(user_dao.delete(user_id))
    click.echo(f"User with id {user_id} deleted successfully")


@user.command(help="List all users")
@click.option("--user-id", prompt="Enter the user ID", help="The ID of the user")
@click.option("--password", prompt="Enter the password", help="The password of the user", hide_input=True)
@click.pass_context
def verify_password(ctx: click.Context, user_id: int, password: str) -> None:
    """Verify a user's password.

    This command checks if the provided password matches the stored password
    for the specified user. The result is displayed with color-coded output:
    green for valid passwords and red for invalid ones.

    Args:
        ctx: Click context object containing the user DAO.
        user_id: The unique identifier of the user whose password to verify.
        password: The password to verify against the user's stored password.

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    is_valid = asyncio.run(user_dao.verify_password(user_id, password))
    is_valid_text = "valid" if is_valid else "invalid"
    is_valid_color = Fore.GREEN if is_valid else Fore.RED
    click.echo(f"Password for user with id {user_id} is {is_valid_color}{is_valid_text}{Style.RESET_ALL}")
