"""CLI for managing the cryptography of the Keychain Application."""

__all__ = ("cryptography",)

from uuid import UUID

import asyncclick as click

from keychain.config import AppConfig
from keychain.services.cryptography.client import CryptographyClient

from .user_dek import build_user_dao, load_user_dek


@click.group(help="CLI for managing the cryptography of the Keychain Application.")
@click.pass_context
def cryptography(ctx: click.Context) -> None:
    """Initialize the cryptography CLI group for the Keychain Application.

    This function serves as the root command group for all cryptography CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.
    """
    ctx.ensure_object(dict)
    cryptography_client = CryptographyClient(ctx.obj["config"])
    ctx.obj["cryptography_client"] = cryptography_client


async def _resolve_dek(ctx: click.Context, user_id: UUID, user_password: str) -> bytes:
    """Verify a user's password and return their data encryption key.

    Args:
        ctx (click.Context): Click context object containing the app config.
        user_id (UUID): The unique identifier of the user.
        user_password (str): The user's plaintext password.

    Returns:
        bytes: The user's plaintext data encryption key.

    """
    config: AppConfig = ctx.obj["config"]
    return await load_user_dek(build_user_dao(config), str(user_id), user_password)


@cryptography.command(help="Encrypt a string with a user's data encryption key")
@click.option("--string", help="The string to encrypt", type=str, required=True)
@click.option("--user-id", help="The ID of the user whose key is used", type=click.UUID, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the user", hide_input=True)
@click.pass_context
async def encrypt(ctx: click.Context, string: str, user_id: UUID, user_password: str) -> None:
    """Encrypt a string using a user's data encryption key.

    This command verifies the user's password, resolves their data encryption
    key and outputs the encrypted string.

    Args:
        ctx (click.Context): Click context object containing the cryptography client.
        string (str): The string to encrypt.
        user_id (UUID): The unique identifier of the user.
        user_password (str): The user's password.

    """
    cryptography_client: CryptographyClient = ctx.obj["cryptography_client"]
    dek = await _resolve_dek(ctx, user_id, user_password)
    encrypted_string = cryptography_client.encrypt(string, dek)
    click.echo(f"Encrypted string: {encrypted_string}")


@cryptography.command(help="Decrypt a string with a user's data encryption key")
@click.option("--string", help="The string to decrypt", type=str, required=True)
@click.option("--user-id", help="The ID of the user whose key is used", type=click.UUID, required=True)
@click.option("--user-password", prompt="Enter the user password", help="The password of the user", hide_input=True)
@click.pass_context
async def decrypt(ctx: click.Context, string: str, user_id: UUID, user_password: str) -> None:
    """Decrypt a string using a user's data encryption key.

    This command verifies the user's password, resolves their data encryption
    key and outputs the decrypted string.

    Args:
        ctx (click.Context): Click context object containing the cryptography client.
        string (str): The string to decrypt.
        user_id (UUID): The unique identifier of the user.
        user_password (str): The user's password.

    """
    cryptography_client: CryptographyClient = ctx.obj["cryptography_client"]
    dek = await _resolve_dek(ctx, user_id, user_password)
    decrypted_string = cryptography_client.decrypt(string, dek)
    click.echo(f"Decrypted string: {decrypted_string}")
