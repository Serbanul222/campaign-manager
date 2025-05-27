 
"""User management API routes."""

from flask import Blueprint, jsonify, request, g

from models import User, db
from auth.decorators import admin_required, log_activity


bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("", methods=["GET"])
@admin_required
def list_users() -> tuple:
    """Return all users."""
    users = [
        {"id": u.id, "email": u.email, "is_admin": u.is_admin}
        for u in User.query.all()
    ]
    return jsonify(users)


@bp.route("", methods=["POST"])
@admin_required
@log_activity("add_user")
def create_user() -> tuple:
    """Create a new user."""
    data = request.get_json() or {}
    email = data.get("email")
    is_admin = bool(data.get("is_admin"))
    if not email:
        return jsonify({"message": "Email required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User exists"}), 400
    user = User(email=email, is_admin=is_admin, password_hash="")
    db.session.add(user)
    db.session.commit()
    return (
        jsonify({"id": user.id, "email": user.email, "is_admin": user.is_admin}),
        201,
    )


@bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
@log_activity("delete_user")
def delete_user(user_id: int) -> tuple:
    """Delete a user by ID."""
    user = User.query.get_or_404(user_id)
    if user.id == g.current_user.id:
        return jsonify({"message": "Cannot delete yourself"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})