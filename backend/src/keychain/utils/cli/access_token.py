"""CLI for managing the access token of the Keychain Application."""

__all__ = ("access_token",)


import asyncclick as click

from keychain.config import AppConfig
from keychain.services.auth.client import AuthClient


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
@click.option("--user-id", help="The ID of the user", type=int, required=True)
@click.pass_context
def generate_access_token(ctx: click.Context, user_id: int) -> None:
    """Generate a new access token for a user.

    This command generates a new access token for a user and outputs the token.
    """
    auth_client: AuthClient = ctx.obj["auth_client"]
    access_token = auth_client.encode_token(user_id)
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
