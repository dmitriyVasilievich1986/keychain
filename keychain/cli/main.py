import click
from flask.cli import FlaskGroup
from flask_appbuilder.security.sqla.models import PermissionView
from loguru import logger
from sqlalchemy.orm import eagerload
from werkzeug.security import generate_password_hash

from keychain import appbuilder, db
from keychain.app import create_app
from keychain.cli.web_client import web_client

main = FlaskGroup(create_app=create_app)
main.add_command(web_client)


BASIC_PERMISSIONS = {
    "can_post": (
        "PasswordModelApi",
        "FieldModelApi",
    ),
    "can_get": (
        "PasswordModelApi",
        "FieldModelApi",
    ),
    "can_put": (
        "PasswordModelApi",
        "FieldModelApi",
    ),
    "can_delete": (
        "PasswordModelApi",
        "FieldModelApi",
    ),
    "can_index": ("KeychainIndexView",),
    "can_pasword_view": ("PasswordView",),
}


@main.command(help="Sync the permissions of the 'Basic' role")  # type: ignore[no-untyped-call]
def sync_roles() -> None:
    """Synchronizes the permissions of the 'Basic' role.

    This function adds the 'Basic' role if it doesn't exist
    and syncs its permissions based on the predefined basic permissions.
    It retrieves the list of permission views from the database,
    eager loading the associated permission and view menu objects.
    It then filters the permission views based on the predefined basic permissions
    and assigns them to the 'Basic' role.
    Finally, it commits the changes to the database.
    """
    role_name = "Basic"
    logger.info("Syncing %s perms", role_name)
    role = appbuilder.sm.add_role(role_name)
    pvms: list[PermissionView] = (
        db.session.query(PermissionView)  # pylint: disable=no-member
        .options(eagerload(PermissionView.permission), eagerload(PermissionView.view_menu))
        .all()
    )
    role_pvms = [
        permission_view
        for permission_view in pvms
        if permission_view.view_menu.name in BASIC_PERMISSIONS.get(permission_view.permission.name, [])
    ]
    role.permissions = role_pvms
    db.session.commit()  # pylint: disable=no-member


@main.command(help="Create a new user with the given username and password")  # type: ignore[no-untyped-call]
@click.option("-U", "--username", required=True, type=str)
@click.option("-P", "--password", prompt=True, hide_input=True, required=True, type=str)
def create_user(username: str, password: str) -> None:
    """Create a new user with the given username and password.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    """
    role_name = "Basic"
    logger.info("Create new user '%s'", username)
    role = appbuilder.sm.find_role(role_name)
    user = appbuilder.sm.user_model(
        username=username,
        password=generate_password_hash(password=password),
        first_name="first_name",
        last_name="last_name",
        email=f"{username}@mail.com",
        roles=[role],
        active=True,
    )
    db.session.add(user)  # pylint: disable=no-member
    db.session.commit()  # pylint: disable=no-member
