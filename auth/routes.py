 
"""Authentication route handlers."""

from flask import Blueprint, jsonify, request

from models import User, db
from .jwt_handler import create_token
from .decorators import jwt_required


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login() -> tuple:
    """Authenticate a user and return a JWT."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_token(user.id)
    return jsonify({"token": token})


@bp.route("/set-password", methods=["POST"])
def set_password() -> tuple:
    """Allow a user to set or reset their password."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Missing data"}), 400
    user = User.query.filter_by(email=email).first_or_404()
    user.set_password(password)
    db.session.commit()
    return jsonify({"message": "Password updated"})


@bp.route("/logout", methods=["POST"])
@jwt_required
def logout() -> tuple:
    """Logout endpoint (token revocation placeholder)."""
    # For a real logout, the token JTI would be added to a blacklist.
    # See jwt_handler.py in other branches for an example.
    return jsonify({"message": "Logged out"})