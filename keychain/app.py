from cryptography.fernet import Fernet
from flask import Flask

from keychain import appbuilder, db, migrate

from .api.index import FieldModelApi, KeychainIndexView, PasswordModelApi
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
        appbuilder.add_permissions(update_perms=True)

        migrate.directory = app.config["MIGRATIONS_DIR"]
        migrate.init_app(app, db)

    return app
