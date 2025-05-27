"""User model for authentication and authorization."""

from datetime import datetime
import re


from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(db.Model):
    """Database model representing a user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash and store a password for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if the password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    @validates("email")
    def validate_email(self, _key: str, address: str) -> str:
        """Validate email format."""
        pattern = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(pattern, address):
            raise ValueError("Invalid email format")
        return address

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<User {self.email}>"