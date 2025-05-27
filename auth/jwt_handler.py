"""JWT token creation and validation utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict
import uuid

import jwt
from flask import current_app

from models import JWTBlacklist, db


def generate_token(user_id: int) -> str:
    """Return an encoded JWT for the given user."""
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=8),
        "jti": str(uuid.uuid4()),
    }
    secret = current_app.config["SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its payload."""
    secret = current_app.config["SECRET_KEY"]
    return jwt.decode(token, secret, algorithms=["HS256"])


def revoke_token(jti: str) -> None:
    """Store the token identifier in the blacklist."""
    db.session.add(JWTBlacklist(jti=jti))
    db.session.commit()


def is_token_revoked(jti: str) -> bool:
    """Return True if the token identifier exists in the blacklist."""
    return db.session.query(JWTBlacklist.id).filter_by(jti=jti).first() is not None