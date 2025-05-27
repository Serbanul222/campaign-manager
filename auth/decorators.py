"""Authentication and logging decorators."""

from functools import wraps
from typing import Any, Callable, TypeVar

from flask import g, jsonify, request
import jwt

from models import ActivityLog, User, db
from .jwt_handler import decode_token, is_token_revoked

F = TypeVar("F", bound=Callable[..., Any])


def jwt_required(func: F) -> F:
    """Ensure that a valid JWT is present."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        if is_token_revoked(payload.get("jti")):
            return jsonify({"error": "Token revoked"}), 401
        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"error": "User not found"}), 404
        g.current_user = user
        return func(*args, **kwargs)

    return wrapper  # type: ignore[misc]


def log_activity(action: str) -> Callable[[F], F]:
    """Log user action to the database."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            response = func(*args, **kwargs)
            user = getattr(g, "current_user", None)
            db.session.add(
                ActivityLog(
                    user_id=user.id if user else None,
                    action=action,
                    ip_address=request.remote_addr,
                )
            )
            db.session.commit()
            return response

        return wrapper  # type: ignore[misc]

    return decorator