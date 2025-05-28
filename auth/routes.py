"""Authentication route handlers."""

from flask import Blueprint, jsonify, request, g

from models import User, db
from .jwt_handler import create_token
from .decorators import jwt_required


bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login() -> tuple:
    """Authenticate a user and return a JWT."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # If user doesn't exist, check if email is authorized
    if not user:
        return jsonify({"message": "Email not authorized"}), 401
    
    # If user exists but has no password set (first time login)
    if not user.password_hash or user.password_hash == "":
        return jsonify({
            "message": "First time login - password required",
            "requires_password_setup": True,
            "email": email
        }), 200
    
    # Normal login flow
    if not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    token = create_token(user.id)
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    })


@bp.route("/set-password", methods=["POST"])
def set_password() -> tuple:
    """Allow a user to set their password for the first time."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email not authorized"}), 404
    
    # Set the password
    user.set_password(password)
    db.session.commit()
    
    # Return JWT token for immediate login
    token = create_token(user.id)
    return jsonify({
        "message": "Password set successfully",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    })


@bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user() -> tuple:
    """Get current user information from JWT token."""
    user = g.current_user
    return jsonify({
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    })


@bp.route("/logout", methods=["POST"])
@jwt_required
def logout() -> tuple:
    """Logout endpoint (token revocation placeholder)."""
    # For a real logout, the token JTI would be added to a blacklist.
    # See jwt_handler.py in other branches for an example.
    return jsonify({"message": "Logged out"})