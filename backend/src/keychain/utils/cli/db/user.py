"""CLI for managing users of the Keychain Application."""

__all__ = ("user",)

from typing import cast

import asyncclick as click
from colorama import Fore, Style

from keychain.modules.routers.models.request.user import UserCreateRequestModel, UserUpdateRequestModel
from keychain.modules.routers.models.response.user import UserGetResponseModel
from keychain.services.daos import UserDAO
from keychain.services.db_client.client import DBClient


@click.group(help="CLI for managing users of the Keychain Application.")
@click.pass_context
def user(ctx: click.Context) -> None:
    """Initialize the user CLI group for the Keychain Application.

    This function serves as the root command group for all user CLI operations.
    It builds the user DAO from the shared DB client and stores it on the
    context for use by subcommands.

    Args:
        ctx (click.Context): Click context object containing the DB client
            instance and used to share the user DAO with subcommands.

    Returns:
        None

    """
    db_client: DBClient = ctx.obj["db_client_instance"]
    ctx.obj["user_dao"] = UserDAO(db_client)


@user.command(help="Create a new user")
@click.option("--username", help="The username of the user", required=True, type=str)
@click.option(
    "--password",
    prompt="Enter your password",
    help="The password of the user",
    hide_input=True,
    confirmation_prompt=True,
)
@click.pass_context
async def create_user(ctx: click.Context, username: str, password: str) -> None:
    """Create a new user in the database.

    This command prompts for a password, creates a new user record in the
    database, and outputs the created user information as JSON.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        username (str): The username of the user to create.
        password (str): The password for the user (hashed before storage).

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    body = UserCreateRequestModel(name=username, password=password)
    user = await user_dao.create(**body.model_dump())
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Get a user by ID")
@click.option("--user-id", help="The ID of the user", required=False, type=int)
@click.option("--username", help="The username of the user", required=False, type=str)
@click.pass_context
async def get_user(ctx: click.Context, user_id: int | None, username: str | None) -> None:
    """Retrieve a user from the database by ID or username.

    This command fetches a user record by ID or username and outputs the user
    information as JSON.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        user_id (int, optional): The unique identifier of the user to
            retrieve. Defaults to None.
        username (str, optional): The username of the user to retrieve.
            Defaults to None.

    Returns:
        None

    Raises:
        click.BadParameter: If neither ``user_id`` nor ``username`` is
            provided.

    """
    if user_id is None and username is None:
        raise click.BadParameter("Either user ID or username must be provided")

    user_dao: UserDAO = ctx.obj["user_dao"]
    user = (
        await user_dao.get_by_pk(cast(int, user_id))
        if user_id is not None
        else await user_dao.get_by_username(cast(str, username))
    )
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Update a user by ID")
@click.option("--user-id", help="The ID of the user", required=True, type=int)
@click.option("--username", help="The new name of the user", required=True, type=str)
@click.pass_context
async def update_user(ctx: click.Context, user_id: int, username: str) -> None:
    """Update a user's name in the database.

    This command updates the name of an existing user identified by their ID
    and outputs the updated user information as JSON.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        user_id (int): The unique identifier of the user to update.
        username (str): The new name to assign to the user.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    body = UserUpdateRequestModel(name=username)
    user = await user_dao.update(user_id, **body.model_dump())
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))


@user.command(help="Delete a user by ID")
@click.option("--user-id", help="The ID of the user", required=True, type=int)
@click.pass_context
async def delete_user(ctx: click.Context, user_id: int) -> None:
    """Delete a user from the database by their ID.

    This command permanently removes a user record from the database.
    After successful deletion, a confirmation message is displayed.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        user_id (int): The unique identifier of the user to delete.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    await user_dao.delete(user_id)
    click.echo(f"User with id {user_id} deleted successfully")


@user.command(help="Verify a user's password")
@click.option("--user-id", help="The ID of the user", required=False, type=int)
@click.option("--username", help="The username of the user", required=False, type=str)
@click.option("--password", prompt="Enter the password", help="The password of the user", hide_input=True)
@click.pass_context
async def verify_password(ctx: click.Context, user_id: int | None, username: str | None, password: str) -> None:
    """Verify a user's password.

    This command checks if the provided password matches the stored password
    for the specified user. The result is displayed with color-coded output:
    green for valid passwords and red for invalid ones.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        user_id (int, optional): The unique identifier of the user whose
            password to verify. Defaults to None.
        username (str, optional): The username of the user whose password to
            verify. Defaults to None.
        password (str): The password to verify against the user's stored
            password.

    Returns:
        None

    Raises:
        click.BadParameter: If neither ``user_id`` nor ``username`` is
            provided.

    """
    if user_id is None and username is None:
        raise click.BadParameter("Either user ID or username must be provided")

    user_dao: UserDAO = ctx.obj["user_dao"]
    user = (
        await user_dao.get_by_pk(cast(int, user_id))
        if user_id is not None
        else await user_dao.get_by_username(cast(str, username))
    )
    is_valid = user.verify_password(password)
    is_valid_text = "valid" if is_valid else "invalid"
    is_valid_color = Fore.GREEN if is_valid else Fore.RED
    click.echo(f"Password for user is {is_valid_color}{is_valid_text}{Style.RESET_ALL}")


@user.command(help="Reset a user's password by ID")
@click.option("--user-id", help="The ID of the user", required=True, type=int)
@click.option(
    "--password",
    prompt="Enter the new password",
    help="The new password of the user",
    hide_input=True,
    confirmation_prompt=True,
)
@click.pass_context
async def reset_password(ctx: click.Context, user_id: int, password: str) -> None:
    """Reset a user's password.

    This command resets the password for an existing user identified by their ID
    and outputs the updated user information as JSON.

    Args:
        ctx (click.Context): Click context object containing the user DAO.
        user_id (int): The unique identifier of the user to reset the password
            for.
        password (str): The new password for the user.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = await user_dao.reset_password(user_id, password)
    user_response = UserGetResponseModel.model_validate(user)
    click.echo(user_response.model_dump_json(indent=2))
