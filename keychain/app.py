from cryptography.fernet import Fernet
from flask import Flask
from loguru import logger

from keychain import appbuilder, db, migrate
from keychain.logging_config import setup_logging


class PasswordApp(Flask):
    fernet: Fernet

    def init_fernet(self) -> None:
        """Initializes the Fernet encryption object.

        This method initializes the Fernet encryption object
        using the secret key specified in the configuration.
        """
        from keychain.config.config import config

        self.fernet = Fernet(config.SECRET_KEY)


def create_app() -> PasswordApp:
    """Creates and configures the Flask application.

    Returns:
        PasswordApp: The configured Flask application.

    """
    from keychain.api import CommonApi, FieldModelApi, PasswordModelApi
    from keychain.config.config import config, web_client_config
    from keychain.views import KeychainIndexView, PasswordView

    setup_logging(config)

    logger.debug("Creating Flask app with config: {}", config.model_dump())
    logger.debug("Web client config: {}", web_client_config.model_dump())

    app = PasswordApp(
        import_name=__name__,
        static_folder=config.static_folder,
        static_url_path=config.static_url_path,
        template_folder=config.template_folder,
    )

    app.config.from_mapping(config.model_dump())

    db.init_app(app)
    app.init_fernet()

    with app.app_context():
        logger.debug("Initializing Flask-AppBuilder")
        appbuilder.indexview = KeychainIndexView
        appbuilder.init_app(app, db.session)

        logger.debug("Adding APIs and views to Flask-AppBuilder")
        appbuilder.add_api(PasswordModelApi)
        appbuilder.add_api(FieldModelApi)
        appbuilder.add_api(CommonApi)
        appbuilder.add_view(PasswordView, "Password", icon="fa-key")

        logger.debug("Setting up authentication and migrations")
        appbuilder.add_permissions(update_perms=True)
        appbuilder.sm.lm.login_view = "AuthDBView.login"

        logger.debug("Configuring Flask-Migrate")
        migrate.directory = config.migrations_dir
        migrate.init_app(app, db)

    return app
