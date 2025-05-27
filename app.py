"""Flask application factory for the campaign manager."""

from flask import Flask

from config import Config
from database.db_setup import init_app


def register_blueprints(app: Flask) -> None:
    """Register available blueprints if their modules exist."""
    blueprints = [
        # Module path, blueprint attribute name, URL prefix
        ("auth.routes", "bp", "/auth"),
        ("api.campaigns", "campaign_bp", "/api/campaigns"),
        ("api.users", "users_bp", "/api/users"),
        ("api.uploads", "uploads_bp", "/api/uploads"),
    ]
    for module_name, blueprint_name, url_prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        except Exception as e: # pylint: disable=broad-except
            # If a blueprint module is missing or has an error, skip it
            # This allows for modularity, e.g., deploying without 'api.campaigns'
            app.logger.warning(f"Could not register blueprint from {module_name}: {str(e)}")


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory used by Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app) # Initialize database with app context
    
    register_blueprints(app)
    return app


if __name__ == "__main__":  # pragma: no cover - manual launch
    # This allows running the app directly with `python app.py`
    # Host 0.0.0.0 makes it accessible externally, debug=True for development
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", debug=True)