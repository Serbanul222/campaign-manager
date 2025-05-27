"""JWT token management utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from flask import current_app

from models import JWTBlacklist, db


def create_access_token(user_id: int) -> str:
    """Generate a JWT token with user identifier."""
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=8),
        "jti": str(user_id) + str(datetime.utcnow().timestamp()),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return the payload."""
    return jwt.decode(
        token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
    )


def is_token_revoked(jti: str) -> bool:
    """Check if the given token identifier has been revoked."""
    return JWTBlacklist.query.filter_by(jti=jti).first() is not None


def revoke_token(jti: str) -> None:
    """Store the token identifier in the blacklist."""
    db.session.add(JWTBlacklist(jti=jti))
    db.session.commit()