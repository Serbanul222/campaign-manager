"""Activity logging and JWT blacklist models."""

from datetime import datetime

from sqlalchemy.orm import relationship

from . import db


class ActivityLog(db.Model):
    """Record of user actions for auditing."""

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship("User", backref="logs")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog {self.action}>"


class JWTBlacklist(db.Model):
    """List of revoked JWT tokens."""

    __tablename__ = "jwt_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<JWTBlacklist {self.jti}>"
