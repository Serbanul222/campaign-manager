"""Authentication related routes."""

from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash

from models import User, db
from .decorators import jwt_required, log_activity
from .jwt_handler import decode_token, generate_token, revoke_token


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
@log_activity("login")
def login():
    """Authenticate user and return JWT."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = generate_token(user.id)
    return jsonify({"token": token})


@auth_bp.route("/set-password", methods=["POST"])
@log_activity("set_password")
def set_password():
    """Allow a user to set their password."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify({"message": "Password updated"})


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
@log_activity("logout")
def logout():
    """Revoke the user's JWT."""
    token = request.headers.get("Authorization").split()[1]
    jti = decode_token(token).get("jti")
    revoke_token(jti)
    return jsonify({"message": "Logged out"})