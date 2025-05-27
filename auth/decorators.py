"""Authentication-related decorators."""

from functools import wraps
from typing import Callable

from flask import g, jsonify, request
from jwt import DecodeError, ExpiredSignatureError

from models import ActivityLog, User, db
from .jwt_handler import decode_token, is_token_revoked


def jwt_required(func: Callable) -> Callable:
    """Ensure a valid JWT token is present."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header else None
        if not token:
            return jsonify({"error": "Missing token"}), 401
        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except DecodeError:
            return jsonify({"error": "Invalid token"}), 401
        if is_token_revoked(payload["jti"]):
            return jsonify({"error": "Token revoked"}), 401
        user = User.query.get(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


def log_activity(action: str) -> Callable:
    """Log user actions for auditing."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
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

        return wrapper

    return decorator
