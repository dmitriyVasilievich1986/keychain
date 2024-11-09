from cryptography.fernet import Fernet
from flask import Flask

from .api.index import base_view


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

    app.register_blueprint(base_view)
    app.init_fernet()

    return app
