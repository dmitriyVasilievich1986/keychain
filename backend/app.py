from api.index import base_view
from cryptography.fernet import Fernet
from flask import Flask


class PasswordApp(Flask):
    fernet: Fernet

    def init_fernet(self):
        self.fernet = Fernet(self.config["SECRET_KEY"])


def create_app():
    app = PasswordApp(__name__)

    app.config.from_object("config")
    app.static_url_path = app.config["STATIC_URL_PATH"]
    app.static_folder = app.config["STATIC_FOLDER"]

    app.register_blueprint(base_view)
    app.init_fernet()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"])
