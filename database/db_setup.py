"""Database initialization utilities."""

from flask import Flask

from models import db  # Import db instance and models


def init_app(app: Flask) -> None:
    """Initialize the application with database settings."""
    db.init_app(app)


def create_tables(app: Flask) -> None:
    """Create database tables within the app context."""
    with app.app_context():
        db.create_all()
