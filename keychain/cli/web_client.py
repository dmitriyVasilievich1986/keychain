import logging

import click
from click.core import Context

from keychain.client.types import FluidResponse
from keychain.client.web_client import WebClient, WebClientCreds
from keychain.config.config import config, web_client_config

logger = logging.getLogger(__name__)


@click.group(help="Keychain client commands")
@click.pass_context
@click.password_option()
@click.option("--username", "-U", help="The username to use for authentication.")
def web_client(ctx: Context, password: str, username: str | None = None) -> None:  # pylint: disable=redefined-outer-name
    """The main entry point for the CLI."""
    ctx.ensure_object(dict)
    creds = WebClientCreds(
        username=username or web_client_config.API_USERNAME,
        password=password,
        host=config.APP_HOST,
        port=config.APP_PORT,
        timeout=web_client_config.timeout,
    )
    ctx.obj["client"] = WebClient[FluidResponse](creds=creds, transform_cls=FluidResponse)


@web_client.command()
@click.pass_context
def passwords(ctx: Context) -> None:
    """Retrieve and display a list of passwords.

    This function retrieves a list of passwords using the caller object
    from the context. If the retrieval is successful (status code 200),
    it prints the list of passwords in JSON format.
    Otherwise, it prints an error message indicating the failure.

    Args:
        ctx (Context): The Click context object containing the caller object.

    """
    client: WebClient[FluidResponse] = ctx.obj["client"]
    data = client.get_passwords_list()
    click.echo(data.model_dump_json(indent=2))


@web_client.command()
@click.pass_context
@click.argument("pk")
def password(ctx: Context, pk: str) -> None:
    """Retrieve and display the password associated with the given primary key (pk).

    Args:
        ctx (Context): The Click context object containing the caller instance.
        pk (str): The primary key for which the password is to be retrieved.

    """
    client: WebClient[FluidResponse] = ctx.obj["client"]
    data = client.get_password(pk)
    click.echo(data.model_dump_json(indent=2))
