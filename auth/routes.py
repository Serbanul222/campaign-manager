# auth/routes.py - Enhanced with comprehensive logging
from flask import Blueprint, jsonify, request, g
import json

from models import User, db
from .jwt_handler import create_token
from .decorators import jwt_required, log_activity


bp = Blueprint("auth", __name__)


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
    
    # Track login attempt details
    attempt_details = {
        "email": email,
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "")[:255]
    }
    
    if not user:
        # Update log with failed attempt
        from models import ActivityLog
        log = ActivityLog(
            user_id=None,
            action="login_failed",
            status="error",
            ip_address=request.remote_addr,
            details=json.dumps({**attempt_details, "reason": "email_not_authorized"})
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({"message": "Email not authorized"}), 401
    
    # If user exists but has no password set (first time login)
    if not user.password_hash or user.password_hash == "":
        # Log first-time login detection
        log = ActivityLog(
            user_id=user.id,
            action="first_time_login_detected",
            status="success",
            ip_address=request.remote_addr,
            details=json.dumps({**attempt_details, "requires_password_setup": True})
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "message": "First time login - password required",
            "requires_password_setup": True,
            "email": email
        }), 200
    
    # Normal login flow
    if not user.check_password(password):
        # Log failed login
        log = ActivityLog(
            user_id=user.id,
            action="login_failed",
            status="error",
            ip_address=request.remote_addr,
            details=json.dumps({**attempt_details, "reason": "invalid_password"})
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({"message": "Invalid credentials"}), 401
    
    # Successful login
    token = create_token(user.id)
    
    # Log successful login
    log = ActivityLog(
        user_id=user.id,
        action="login_success",
        status="success",
        ip_address=request.remote_addr,
        details=json.dumps({
            **attempt_details,
            "user_id": user.id,
            "is_admin": user.is_admin
        })
    )
    db.session.add(log)
    db.session.commit()
    
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
    from models import ActivityLog
    log = ActivityLog(
        user_id=user.id,
        action="password_set_success",
        status="success",
        ip_address=request.remote_addr,
        details=json.dumps({
            "email": email,
            "user_id": user.id,
            "is_admin": user.is_admin,
            "ip_address": request.remote_addr
        })
    )
    db.session.add(log)
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
    # Log the logout
    from models import ActivityLog
    log = ActivityLog(
        user_id=g.current_user.id,
        action="logout_success",
        status="success",
        ip_address=request.remote_addr,
        details=json.dumps({
            "user_id": g.current_user.id,
            "email": g.current_user.email
        })
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"message": "Logged out successfully"})