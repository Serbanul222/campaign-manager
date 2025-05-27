"""Flask application factory."""

from flask import Flask

from config import Config
from database.db_setup import create_tables, init_app
from auth import auth_bp
from api import campaign_bp, uploads_bp, users_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory for the campaign manager."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app)
    create_tables(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(campaign_bp, url_prefix="/campaigns")
    app.register_blueprint(uploads_bp, url_prefix="/uploads")
    app.register_blueprint(users_bp, url_prefix="/users")

    return app


if __name__ == "__main__":  # pragma: no cover - manual run
    create_app().run(debug=True)
