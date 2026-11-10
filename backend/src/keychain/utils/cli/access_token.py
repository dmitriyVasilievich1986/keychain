"""CLI for managing the access token of the Keychain Application."""

__all__ = ("access_token",)


from uuid import UUID

import asyncclick as click

from keychain.config import AppConfig
from keychain.services.auth.client import AuthClient

from .user_dek import build_user_dao, load_user_dek


@click.group(help="CLI for managing the access token of the Keychain Application.")
@click.pass_context
def access_token(ctx: click.Context) -> None:
    """Initialize the access token CLI group for the Keychain Application.

    This function serves as the root command group for all access token CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.
    """
    ctx.ensure_object(dict)
    config: AppConfig = ctx.obj["config"]
    auth_client = AuthClient(config)
    ctx.obj["auth_client"] = auth_client


@access_token.command(help="Generate a new access token")
@click.option("--user-id", help="The ID of the user", type=click.UUID, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the user", hide_input=True)
@click.pass_context
async def generate_access_token(ctx: click.Context, user_id: UUID, user_password: str) -> None:
    """Generate a new access token for a user.

    This command verifies the user's password, resolves their data encryption
    key and generates a new access token that carries it.

    Args:
        ctx (click.Context): Click context object containing the app config
            and auth client.
        user_id (UUID): The unique identifier of the user.
        user_password (str): The user's password.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    auth_client: AuthClient = ctx.obj["auth_client"]
    dek = await load_user_dek(build_user_dao(config), str(user_id), user_password)

    access_token = auth_client.encode_token(str(user_id), dek)
    click.echo(access_token.model_dump_json(indent=2))


@access_token.command(help="Decode an access token")
@click.option("--token", help="The token to decode", type=str, required=True)
@click.pass_context
def decode_access_token(ctx: click.Context, token: str) -> None:
    """Decode an access token.

    This command decodes an access token and outputs the payload.
    """
    auth_client: AuthClient = ctx.obj["auth_client"]
    payload = auth_client.decode_token(token)
    click.echo(payload.model_dump_json(indent=2))
