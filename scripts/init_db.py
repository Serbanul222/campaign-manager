"""Create database tables for the campaign manager."""

from app import create_app
from database.db_setup import create_tables


def main() -> None:
    """Initialize the database using the app context."""
    app = create_app()
    create_tables(app)


if __name__ == "__main__":
    main()
