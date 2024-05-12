from os import environ

class DefaultConfig:
    """Flask configuration variables."""

    # General Config
    APP_NAME = "O.G Paper-Trading"
    DEBUG = bool(int(environ.get("FLASK_DEBUG")))
    SECRET_KEY =  environ.get("SECRET_KEY")
    PORT = environ.get("FLASK_PORT")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATE_FOLDER = "templates"