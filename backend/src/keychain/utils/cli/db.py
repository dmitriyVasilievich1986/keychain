import click
from alembic import command
from alembic.config import Config

from keychain.config import AppConfig


@click.group(help="CLI for managing the database of the Keychain Application.")
@click.pass_context
def db(ctx: click.Context) -> None:
    """Initialize the database CLI group for the Keychain Application.

    This function serves as the root command group for all database CLI operations.
    It initializes the application configuration and stores them in the Click
    context for use by subcommands.

    Args:
        ctx: Click context object for sharing data between commands.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    alembic_cfg = Config(config.db.alembic_ini_path)
    ctx.obj["alembic_cfg"] = alembic_cfg


@db.command()
@click.pass_context
def current(ctx: click.Context) -> None:
    """Display the current database revision.

    Retrieves the current database revision from the Alembic configuration and displays
    it in a user-friendly format.

    Args:
        ctx: Click context object containing the Alembic configuration.

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    command.current(alembic_cfg)


@db.command()
@click.option(
    "--revision",
    default="head",
    help="The target revision to upgrade to. Use 'head' to upgrade to the latest revision.",
)
@click.pass_context
def upgrade(ctx: click.Context, revision: str) -> None:
    """Upgrade the database to a specific revision.

    Applies pending migrations to upgrade the database schema to the specified
    revision. If no revision is specified, upgrades to the latest (head) revision.

    Args:
        ctx: Click context object containing the Alembic configuration.
        revision: The target revision identifier (e.g., 'head', 'abc123', '+1').

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    command.upgrade(alembic_cfg, revision)


@db.command()
@click.option(
    "--revision",
    required=True,
    help="The target revision to downgrade to. Use '-1' to downgrade one revision, or a specific revision ID.",
)
@click.pass_context
def downgrade(ctx: click.Context, revision: str) -> None:
    """Downgrade the database to a specific revision.

    Reverts database migrations to downgrade the schema to the specified revision.
    This operation will undo the changes made by migrations.

    Args:
        ctx: Click context object containing the Alembic configuration.
        revision: The target revision identifier (e.g., '-1', 'abc123', 'base').

    Returns:
        None

    """
    alembic_cfg: Config = ctx.obj["alembic_cfg"]
    command.downgrade(alembic_cfg, revision)
