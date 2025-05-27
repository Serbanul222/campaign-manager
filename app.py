"""Flask application factory for the campaign manager."""

from flask import Flask

from config import Config
from database.db_setup import init_app


def register_blueprints(app: Flask) -> None:
    """Register available blueprints if their modules exist."""
    blueprints = [
        ("auth.routes", "/auth"),
        ("api.campaigns", "/api/campaigns"),
        ("api.users", "/api/users"),
        ("api.uploads", "/api/uploads"),
    ]
    for module_name, url_prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=["bp"])
            app.register_blueprint(module.bp, url_prefix=url_prefix)
        except Exception:
            pass


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory used by Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app)
    register_blueprints(app)
    return app


if __name__ == "__main__":  # pragma: no cover - manual launch
    create_app().run(host="0.0.0.0", debug=True)
