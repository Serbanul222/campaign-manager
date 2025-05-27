"""Create database tables for the campaign manager."""

import os
import sys

# Add parent directory to Python path to find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.db_setup import create_tables


def main() -> None:
    """Initialize the database using the app context."""
    app = create_app()
    create_tables(app)


if __name__ == "__main__":
    main()
