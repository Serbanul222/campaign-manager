"""Flask application factory."""
from flask import Flask

from config import Config
from models import db
from database.db_setup import init_app
from auth.routes import auth_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_app(app)
    app.register_blueprint(auth_bp)
    return app


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        db.create_all()
    application.run(debug=True)
