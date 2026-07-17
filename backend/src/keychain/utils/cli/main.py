"""CLI for the Keychain Application."""

__all__ = ("main",)


import asyncclick as click
import uvicorn
from uvicorn import Config, Server

from keychain.config import AppConfig

from .access_token import access_token
from .cryptography import cryptography
from .db import db


@click.group(help="CLI for managing the Keychain Application.")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Initialize the main CLI group for the Keychain Application.

    This function serves as the root command group for all CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.

    Args:
        ctx: Click context object for sharing data between commands.

    Returns:
        None

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = AppConfig.get_or_create()


@main.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Display the version information of the Chat History Service.

    Retrieves the version number from the application settings and displays
    it in a user-friendly format.

    Args:
        ctx: Click context object containing the application settings.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    click.echo(f"Keychain Application, version {config.info.version}")


@main.command()
@click.pass_context
def show_config(ctx: click.Context) -> None:
    """Display the application configuration of the Keychain Application.

    Retrieves the application configuration from the application configuration and displays
    it in a user-friendly format.

    Args:
        ctx: Click context object containing the application configuration.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    click.echo(config.model_dump_json(indent=2))


@main.command(help="Run the Keychain Application server.")
@click.option("--host", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", default=8000, help="Port to bind the server to.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload for development.")
async def run(host: str, port: int, reload: bool) -> None:
    """Start the Keychain Application web server using Uvicorn.

    Launches the FastAPI application server with the specified configuration.
    The server can be run in development mode with auto-reload enabled for
    rapid iteration.

    Args:
        host: The network interface to bind the server to (default: "0.0.0.0").
        port: The port number to listen on (default: 8000).
        reload: Enable auto-reload when code changes are detected (default: False).

    Returns:
        None

    """
    click.echo(f"Starting Keychain Application on {host}:{port} (reload={reload})")
    app = "keychain.modules.app:get_app"

    if reload:
        uvicorn.run(app, host=host, port=port, reload=True, factory=True)
    else:
        await Server(Config(app, host=host, port=port, factory=True)).serve()


main.add_command(db)
main.add_command(cryptography)
main.add_command(access_token)
