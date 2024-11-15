from cryptography.fernet import Fernet
from flask import Flask
from flask_appbuilder import AppBuilder

from keychain.database.db import db

from .api.index import KeychainIndexView, base_view
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

    setup_logging()

    app.config.from_object("keychain.config")
    app.static_url_path = app.config["STATIC_URL_PATH"]
    app.static_folder = app.config["STATIC_FOLDER"]

    db.init_app(app)
    app.register_blueprint(base_view)
    app.init_fernet()

    with app.app_context():
        appbuilder = AppBuilder(
            update_perms=False, app=app, session=db.session, indexview=KeychainIndexView
        )

    return app
