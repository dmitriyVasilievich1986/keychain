import logging

import click
from click.core import Context

from keychain.client.client import Caller
from keychain.client.dataclasses import CallerProps

logger = logging.getLogger(__name__)


@click.group(help="Keychain client commands")
@click.pass_context
@click.password_option()
@click.option("--username", "-U", help="The username to use for authentication.")
def web_client(ctx: Context, password: str, username: str | None = None) -> None:  # pylint: disable=redefined-outer-name
    """
    The main entry point for the CLI.
    """

    ctx.ensure_object(dict)
    ctx.obj["caller"] = Caller(
        caller_props=CallerProps(username=username, password=password)
    )


@web_client.command()
@click.pass_context
def passwords(ctx: Context) -> None:
    """
    Retrieve and display a list of passwords.
    This function retrieves a list of passwords using the caller object
    from the context. If the retrieval is successful (status code 200),
    it prints the list of passwords in JSON format.
    Otherwise, it prints an error message indicating the failure.

    Args:
        ctx (Context): The Click context object containing the caller object.
    """

    response = ctx.obj["caller"].get_passwords_list()
    if response.status_code == 200:
        click.echo(response.json())
    else:
        click.echo("Failed to retrieve passwords.")


@web_client.command()
@click.pass_context
@click.argument("pk")
def password(ctx: Context, pk: str) -> None:
    """
    Retrieve and display the password associated with the given primary key (pk).

    Args:
        ctx (Context): The Click context object containing the caller instance.
        pk (str): The primary key for which the password is to be retrieved.
    """

    response = ctx.obj["caller"].get_password(pk)
    if response.status_code == 200:
        click.echo(response.json())
    else:
        click.echo("Failed to retrieve passwords.")
