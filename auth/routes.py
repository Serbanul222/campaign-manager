"""Authentication route handlers."""

from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash

from models import User, db
from .decorators import jwt_required, log_activity
from .jwt_handler import create_access_token, decode_token, revoke_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
@log_activity("login")
def login():
    """Authenticate a user and return a JWT token."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing credentials"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(user.id)
    return jsonify({"token": token})


@auth_bp.post("/logout")
@jwt_required
@log_activity("logout")
def logout():
    """Revoke the current user's token."""
    auth_header = request.headers.get("Authorization")
    token = auth_header.replace("Bearer ", "")
    jti = decode_token(token)["jti"]
    revoke_token(jti)
    return jsonify({"message": "Logged out"})


@auth_bp.post("/set-password")
@jwt_required
@log_activity("set_password")
def set_password():
    """Allow a user to set or reset their password."""
    user = request.get_json() or {}
    password = user.get("password")
    if not password:
        return jsonify({"error": "Password required"}), 400
    g.current_user.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify({"message": "Password updated"})
