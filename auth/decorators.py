 
"""Request decorators for authentication and logging."""

from functools import wraps
from flask import request, jsonify, g

from models import User, ActivityLog, db
from .jwt_handler import decode_token


def jwt_required(func):
    """Ensure the request has a valid JWT token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except Exception:  # pragma: no cover - decode errors
            return jsonify({"message": "Invalid token"}), 401
        user = User.query.get(payload.get("sub"))
        if not user or not user.is_active: # Assuming User model has an is_active attribute
            return jsonify({"message": "Invalid user"}), 401
        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    """Allow only admin users to access the route."""

    @wraps(func)
    @jwt_required
    def wrapper(*args, **kwargs):
        user = g.current_user
        if not user.is_admin:
            return jsonify({"message": "Forbidden"}), 403
        return func(*args, **kwargs)

    return wrapper


def log_activity(action: str):
    """Log the activity for the current user."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            user = getattr(g, "current_user", None)
            if user:
                log = ActivityLog(
                    user_id=user.id,
                    action=action,
                    ip_address=request.remote_addr,
                )
                db.session.add(log)
                db.session.commit()
            return response

        return wrapper

    return decorator