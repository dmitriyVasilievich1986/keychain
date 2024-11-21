from cryptography.fernet import Fernet
from flask import Flask

from keychain import appbuilder, db, migrate
from keychain.views.views import KeychainIndexView, PasswordView

from .api.field import FieldModelApi
from .api.password import PasswordModelApi
from .logging_config import setup_logging


class PasswordApp(Flask):
    fernet: Fernet

    def init_fernet(self) -> None:
        """
        Initializes the Fernet encryption object.
        This method initializes the Fernet encryption object
        using the secret key specified in the configuration.
        """

        self.fernet = Fernet(self.config["SECRET_KEY"])


def create_app() -> PasswordApp:
    """
    Creates and configures the Flask application.

    Returns:
        PasswordApp: The configured Flask application.
    """

    app = PasswordApp(__name__)

    app.config.from_object("keychain.config")
    app.static_url_path = app.config["STATIC_URL_PATH"]
    app.static_folder = app.config["STATIC_FOLDER"]

    setup_logging(app.config)
    db.init_app(app)
    app.init_fernet()

    with app.app_context():
        appbuilder.indexview = KeychainIndexView
        appbuilder.init_app(app, db.session)
        appbuilder.add_api(PasswordModelApi)
        appbuilder.add_api(FieldModelApi)
        appbuilder.add_view(PasswordView, "Password", icon="fa-key")
        appbuilder.add_permissions(update_perms=True)
        appbuilder.sm.lm.login_view = "AuthDBView.login"

        migrate.directory = app.config["MIGRATIONS_DIR"]
        migrate.init_app(app, db)

    return app
