# auth/routes.py - Clean rewrite with proper imports and error handling
from flask import Blueprint, jsonify, request, g
import json

from models import User, ActivityLog, db
from .jwt_handler import create_token
from .decorators import jwt_required, log_activity


bp = Blueprint("auth", __name__)


def _log_activity(user_id, action, status, details_dict):
    """Helper function to safely log activity."""
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            status=status,
            ip_address=request.remote_addr,
            details=json.dumps(details_dict)
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log activity: {e}")
        try:
            db.session.rollback()
        except:
            pass


@bp.route("/login", methods=["POST"])
@log_activity("login_attempt", "User login attempt")
def login():
    """Authenticate a user and return a JWT."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # Prepare login attempt details
    attempt_details = {
        "email": email,
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "")[:255]
    }
    
    # User not found
    if not user:
        _log_activity(
            user_id=None,
            action="login_failed",
            status="error",
            details_dict={**attempt_details, "reason": "email_not_authorized"}
        )
        return jsonify({"message": "Email not authorized"}), 401
    
    # First time login (no password set)
    if not user.password_hash or user.password_hash == "":
        _log_activity(
            user_id=user.id,
            action="first_time_login_detected",
            status="success",
            details_dict={**attempt_details, "requires_password_setup": True}
        )
        return jsonify({
            "message": "First time login - password required",
            "requires_password_setup": True,
            "email": email
        }), 200
    
    # Wrong password
    if not user.check_password(password):
        _log_activity(
            user_id=user.id,
            action="login_failed",
            status="error",
            details_dict={**attempt_details, "reason": "invalid_password"}
        )
        return jsonify({"message": "Invalid credentials"}), 401
    
    # Successful login
    token = create_token(user.id)
    
    _log_activity(
        user_id=user.id,
        action="login_success",
        status="success",
        details_dict={
            **attempt_details,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
    )
    
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    })


@bp.route("/set-password", methods=["POST"])
@log_activity("set_password", "User set password")
def set_password():
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
    
    # Log password setup
    _log_activity(
        user_id=user.id,
        action="password_set_success",
        status="success",
        details_dict={
            "email": email,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
    )
    
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
@log_activity("get_user_profile", "Retrieved user profile")
def get_current_user():
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
@log_activity("logout", "User logged out")
def logout():
    """Logout endpoint with activity logging."""
    _log_activity(
        user_id=g.current_user.id,
        action="logout_success",
        status="success",
        details_dict={
            "user_id": g.current_user.id,
            "email": g.current_user.email
        }
    )
    
    return jsonify({"message": "Logged out successfully"})