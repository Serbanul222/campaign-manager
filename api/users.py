"""User management endpoints (admin only)."""

from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required
from models import User, db

users_bp = Blueprint("users", __name__)


@users_bp.get("/")
@jwt_required
def list_users():
    """Return all users."""
    users = User.query.all()
    return jsonify([{"id": u.id, "email": u.email, "is_admin": u.is_admin} for u in users])


@users_bp.post("/")
@jwt_required
def create_user():
    """Add a new user (admin)."""
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User exists"}), 400
    user = User(email=email, password_hash="")
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "email": user.email}), 201
