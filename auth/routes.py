"""Authentication endpoints."""
from flask import Blueprint, jsonify, request, g

from models import ActivityLog, User, db
from .decorators import jwt_required
from .jwt_handler import create_access_token, revoke_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(user.id)
    db.session.add(ActivityLog(user_id=user.id, action="login", ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({"token": token}), 200


@auth_bp.post("/logout")
@jwt_required
def logout():
    """Invalidate the current JWT token."""
    jti = g.jwt_payload.get("jti")
    revoke_token(jti)
    db.session.add(ActivityLog(user_id=g.current_user.id, action="logout", ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.post("/set-password")
def set_password():
    """Set or reset a user's password."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.set_password(password)
    db.session.add(ActivityLog(user_id=user.id, action="set_password", ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200
