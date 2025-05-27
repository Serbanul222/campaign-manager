 
"""JWT encoding and decoding utilities."""

from datetime import datetime, timedelta
import jwt
from flask import current_app


def create_token(user_id: int) -> str:
    """Return a signed JWT for the given user."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    secret = current_app.config["SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode a JWT and return the payload."""
    secret = current_app.config["SECRET_KEY"]
    return jwt.decode(token, secret, algorithms=["HS256"])

