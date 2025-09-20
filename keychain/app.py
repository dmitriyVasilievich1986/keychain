from cryptography.fernet import Fernet
from flask import Flask

from keychain import appbuilder, db, migrate
from keychain.config.config import config
from keychain.logging_config import setup_logging


class PasswordApp(Flask):
    fernet: Fernet

    def init_fernet(self) -> None:
        """Initializes the Fernet encryption object.

        This method initializes the Fernet encryption object
        using the secret key specified in the configuration.
        """
        self.fernet = Fernet(config.SECRET_KEY)


def create_app() -> PasswordApp:
    """Creates and configures the Flask application.

    Returns:
        PasswordApp: The configured Flask application.

    """
    from keychain.api import FieldModelApi, PasswordModelApi
    from keychain.views import KeychainIndexView, PasswordView

    app = PasswordApp(
        import_name=__name__,
        static_folder=config.static_folder,
        static_url_path=config.static_url_path,
        template_folder=config.template_folder,
    )

    app.config.from_mapping(config.model_dump())

    setup_logging(config)
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

        migrate.directory = config.migrations_dir
        migrate.init_app(app, db)

    return app
