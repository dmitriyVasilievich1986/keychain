from .app import create_app


def main() -> None:
    """
    Entry point of the application.
    Creates an instance of the app using `create_app()` function and runs it.
    The app is run on the host and port specified in the app configuration.
    """

    app = create_app()
    app.run(host=app.config["APP_HOST"], port=app.config["APP_PORT"])
