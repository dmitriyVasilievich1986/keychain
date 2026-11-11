"""CLI for managing passwords of the Keychain Application."""

__all__ = ("password",)

import json
from uuid import UUID

import asyncclick as click

from keychain.config import AppConfig
from keychain.modules.routers.models.request.password import PasswordCreateRequestModel, PasswordPatchRequestModel
from keychain.modules.routers.models.response.password import PasswordGetResponseModel, SimplePasswordGet
from keychain.services.daos import PasswordDAO
from keychain.services.daos.firestore.models import Password
from keychain.utils.cli.user_dek import build_password_dao, build_user_dao, load_user_dek
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
    ctx.obj["password_dao"] = build_password_dao(config)


async def _owner_password_dao(ctx: click.Context, user_id: UUID, user_password: str) -> PasswordDAO:
    """Build a password DAO holding the data encryption key of a user.

    Args:
        ctx (click.Context): Click context object containing the app config
            and the password DAO.
        user_id (UUID): The unique identifier of the user.
        user_password (str): The user's plaintext password.

    Returns:
        PasswordDAO: A DAO that decrypts and encrypts the user's field values.

    """
    config: AppConfig = ctx.obj["config"]
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    dek = await load_user_dek(build_user_dao(config), str(user_id), user_password)
    return PasswordDAO(password_dao.firestore_client, password_dao.collection_name, dek=dek)


async def _get_owned_password(password_dao: PasswordDAO, password_id: UUID, user_id: UUID) -> Password:
    """Load a password and ensure it belongs to the given user.

    Args:
        password_dao (PasswordDAO): DAO used to load the password.
        password_id (UUID): The unique identifier of the password.
        user_id (UUID): The unique identifier of the user who must own it.

    Returns:
        Password: The requested password.

    Raises:
        click.BadParameter: If the password belongs to another user.

    """
    password = await password_dao.get_by_id(str(password_id))
    if password.user_id != str(user_id):
        raise click.BadParameter(f"Password {password_id} does not belong to user {user_id}", param_hint="--user-id")
    return password


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
@click.option("--user-id", help="The ID of the user who owns the password", type=click.UUID, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def get_password(ctx: click.Context, password_id: UUID, user_id: UUID, user_password: str) -> None:
    """Retrieve a password from the database by its ID.

    This command fetches a password document by ID, decrypts its field values
    with the owner's data encryption key and outputs the password information
    as JSON.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to retrieve.
        user_id (UUID): The unique identifier of the user who owns the password.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    password_dao = await _owner_password_dao(ctx, user_id, user_password)
    password = await _get_owned_password(password_dao, password_id, user_id)
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Update a password by ID")
@click.option("--password-id", help="The ID of the password", type=click.UUID, required=True)
@click.option("--name", help="The new name of the password", type=str, required=True)
@click.option("--image-url", help="The new image URL of the password", type=str, required=False)
@click.option("--user-id", help="The ID of the user who owns the password", type=click.UUID, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the owner", hide_input=True)
@click.pass_context
async def update_password(
    ctx: click.Context, password_id: UUID, name: str, image_url: str | None, user_id: UUID, user_password: str
) -> None:
    """Update a password's name and/or image URL in the database.

    This command updates the name and/or image URL of an existing password
    identified by its ID and outputs the updated password information as JSON.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to update.
        name (str): The new name to assign to the password.
        image_url (str, optional): New image URL to assign to the password.
            Defaults to None.
        user_id (UUID): The unique identifier of the user who owns the password.
        user_password (str): The owner's password, used to decrypt field values.

    Returns:
        None

    """
    password_dao = await _owner_password_dao(ctx, user_id, user_password)
    await _get_owned_password(password_dao, password_id, user_id)
    body = PasswordPatchRequestModel(name=name, image_url=image_url)
    password = await password_dao.update(str(password_id), **body.model_dump(exclude={"fields"}))
    password_response = PasswordGetResponseModel.model_validate(password)
    click.echo(password_response.model_dump_json(indent=2))


@password.command(help="Delete a password by ID")
@click.option("--password-id", prompt="Enter the password ID", help="The ID of the password", type=click.UUID)
@click.option(
    "--mark-deleted/--no-mark-deleted",
    default=True,
    show_default=True,
    help="Mark the password as deleted instead of permanently removing it",
)
@click.pass_context
async def delete_password(ctx: click.Context, password_id: UUID, mark_deleted: bool) -> None:
    """Delete a password from the database by its ID.

    By default the password is only marked as deleted and kept in the
    database. With ``--no-mark-deleted`` the password document is permanently
    removed. After successful deletion, a confirmation message is displayed.

    Args:
        ctx (click.Context): Click context object containing the password DAO.
        password_id (UUID): The unique identifier of the password to delete.
        mark_deleted (bool): Whether to mark the password as deleted instead
            of permanently removing it. Defaults to True.

    Returns:
        None

    """
    password_dao: PasswordDAO = ctx.obj["password_dao"]
    if mark_deleted:
        await password_dao.mark_as_deleted(str(password_id))
        click.echo(f"Password with id {password_id} marked as deleted successfully")
    else:
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
