from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict

import jwt
from flask import current_app

from models import JWTBlacklist, db


def create_access_token(user_id: int) -> str:
    """Generate a JWT access token for the given user."""
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(hours=8),
        "jti": str(uuid.uuid4()),
    }
    secret = current_app.config["SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""
    secret = current_app.config["SECRET_KEY"]
    return jwt.decode(token, secret, algorithms=["HS256"])


def is_token_revoked(jti: str) -> bool:
    """Check if a token ID is in the blacklist."""
    return JWTBlacklist.query.filter_by(jti=jti).first() is not None


def revoke_token(jti: str) -> None:
    """Add a token ID to the blacklist."""
    db.session.add(JWTBlacklist(jti=jti))
    db.session.commit()
