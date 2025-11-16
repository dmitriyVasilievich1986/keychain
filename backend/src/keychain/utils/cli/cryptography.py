"""CLI for managing the cryptography of the Keychain Application."""

__all__ = ["cryptography"]

import click

from keychain.services.cryptography.client import CryptographyClient


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


@cryptography.command(help="Encrypt a string")
@click.option("--string", prompt="Enter the string to encrypt", help="The string to encrypt")
@click.pass_context
def encrypt(ctx: click.Context, string: str) -> None:
    """Encrypt a string using the cryptography client.

    This command encrypts a string using the cryptography client and outputs the encrypted string.

    Args:
        ctx: Click context object containing the cryptography client.
        string: The string to encrypt.

    """
    cryptography_client: CryptographyClient = ctx.obj["cryptography_client"]
    encrypted_string = cryptography_client.encrypt(string)
    click.echo(f"Encrypted string: {encrypted_string}")


@cryptography.command(help="Decrypt a string")
@click.option("--string", prompt="Enter the string to decrypt", help="The string to decrypt")
@click.pass_context
def decrypt(ctx: click.Context, string: str) -> None:
    """Decrypt a string using the cryptography client.

    This command decrypts a string using the cryptography client and outputs the decrypted string.

    Args:
        ctx: Click context object containing the cryptography client.
        string: The string to decrypt.

    """
    cryptography_client: CryptographyClient = ctx.obj["cryptography_client"]
    decrypted_string = cryptography_client.decrypt(string)
    click.echo(f"Decrypted string: {decrypted_string}")
