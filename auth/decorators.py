from functools import wraps
from typing import Callable

import jwt
from flask import g, jsonify, request
from jwt import ExpiredSignatureError, InvalidTokenError

from models import User
from .jwt_handler import decode_access_token, is_token_revoked


def jwt_required(view: Callable) -> Callable:
    """Ensure a valid JWT is present in the request."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = header.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
        except (ExpiredSignatureError, InvalidTokenError, jwt.PyJWTError):
            return jsonify({"error": "Invalid token"}), 401
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            return jsonify({"error": "Token revoked"}), 401
        user = User.query.get(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 401
        g.current_user = user
        g.jwt_payload = payload
        return view(*args, **kwargs)

    return wrapped
