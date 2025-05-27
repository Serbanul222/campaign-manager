"""Flask application factory."""
from flask import Flask

from config import Config
from auth.routes import auth_bp
from api.campaigns import campaign_bp
from api.uploads import upload_bp
from database.db_setup import create_tables, init_app


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app)
    create_tables(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(campaign_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")

    return app


if __name__ == "__main__":  # pragma: no cover
    app = create_app()
    app.run(debug=True)