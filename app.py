 
"""Flask application factory."""

from flask import Flask

from config import Config
from models import db
from database.db_setup import create_tables
from auth.routes import bp as auth_bp
from api.users import bp as users_bp
from api.logs import bp as logs_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    create_tables(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(logs_bp)

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(debug=True)