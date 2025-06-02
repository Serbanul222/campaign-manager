# models/log.py - Simple fix for ActivityLog model
"""Activity logging and JWT blacklist models - simplified version."""

from datetime import datetime
from sqlalchemy.orm import relationship

from . import db


class ActivityLog(db.Model):
    """Record of user actions for auditing."""
    
    __tablename__ = "activity_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced columns - now that migration is complete, these should work
    status = db.Column(db.String(20), default="success")
    details = db.Column(db.Text)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(50))
    duration_ms = db.Column(db.Integer)
    
    user = relationship("User", backref="activity_logs")
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None,
            "action": self.action,
            "status": self.status or "success",
            "ip_address": self.ip_address,
            "details": self.details,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_filtered_logs(user_id=None, action=None, status=None, resource_type=None, 
                         start_date=None, end_date=None, page=1, per_page=50):
        """Get filtered activity logs with pagination."""
        from models import User  # Import here to avoid circular import
        
        query = ActivityLog.query.join(User)
        
        # Apply filters
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if action:
            query = query.filter(ActivityLog.action.ilike(f"%{action}%"))
        if status:
            query = query.filter(ActivityLog.status == status)
        if resource_type:
            query = query.filter(ActivityLog.resource_type == resource_type)
        if start_date:
            query = query.filter(ActivityLog.created_at >= start_date)
        if end_date:
            query = query.filter(ActivityLog.created_at <= end_date)
        
        # Order by most recent first
        query = query.order_by(ActivityLog.created_at.desc())
        
        # Paginate
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} by {self.user_id}>"


class JWTBlacklist(db.Model):
    """List of revoked JWT tokens."""
    
    __tablename__ = "jwt_blacklist"
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<JWTBlacklist {self.jti}>"