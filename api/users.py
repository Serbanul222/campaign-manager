# api/users.py - Enhanced with comprehensive logging
from flask import Blueprint, jsonify, request, g
import json

from models import User, db
from auth.decorators import admin_required, log_activity


users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
@admin_required
@log_activity("list_users", "Retrieved user list")
def list_users():
    """Return all users."""
    users = User.query.all()
    user_data = [
        {
            "id": u.id, 
            "email": u.email, 
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]
    
    return jsonify(user_data)


@users_bp.route("", methods=["POST"])
@admin_required
@log_activity("create_user", resource_type="user")
def create_user():
    """Create a new user."""
    data = request.get_json() or {}
    email = data.get("email")
    is_admin = bool(data.get("is_admin"))
    
    if not email:
        return jsonify({"message": "Email required"}), 400
        
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    user = User(email=email, is_admin=is_admin, password_hash="")
    db.session.add(user)
    db.session.flush()  # Get the ID
    
    db.session.commit()
    
    # Update log with user creation details
    from models import ActivityLog
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="create_user"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "created_user_id": user.id,
            "created_user_email": email,
            "is_admin": is_admin,
            "created_by": g.current_user.email
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(user.id)
        db.session.commit()
    
    return jsonify({
        "id": user.id, 
        "email": user.email, 
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 201


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
@log_activity("delete_user", resource_type="user")
def delete_user(user_id: int):
    """Delete a user by ID."""
    user = User.query.get_or_404(user_id)
    
    if user.id == g.current_user.id:
        return jsonify({"message": "Cannot delete yourself"}), 400
    
    # Collect user info before deletion
    user_info = {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
    
    # Check if user has associated campaigns
    campaign_count = Campaign.query.filter_by(user_id=user.id).count()
    
    db.session.delete(user)
    db.session.commit()
    
    # Update log with deletion details
    from models import ActivityLog
    recent_log = ActivityLog.query.filter_by(
        user_id=g.current_user.id,
        action="delete_user"
    ).order_by(ActivityLog.created_at.desc()).first()
    
    if recent_log:
        details = {
            "deleted_user": user_info,
            "associated_campaigns": campaign_count,
            "deleted_by": g.current_user.email
        }
        recent_log.details = json.dumps(details)
        recent_log.resource_id = str(user_id)
        db.session.commit()
    
    return jsonify({"message": "User deleted successfully"})