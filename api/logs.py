"""Activity log API routes."""

from flask import Blueprint, jsonify

from models import ActivityLog
from auth.decorators import admin_required


bp = Blueprint("logs", __name__, url_prefix="/api/logs")


@bp.route("", methods=["GET"])
@admin_required
def list_logs() -> tuple:
    """Return recent activity logs."""
    logs = (
        ActivityLog.query.order_by(ActivityLog.created_at.desc())
        .limit(100)
        .all()
    )
    result = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
    return jsonify(result)

