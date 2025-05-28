# api/logs.py - Enhanced logs API with filtering and pagination
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import text

from models import ActivityLog, User, db
from auth.decorators import admin_required, log_activity


bp = Blueprint("logs", __name__, url_prefix="/api/logs")


@bp.route("", methods=["GET"])
@admin_required
@log_activity("view_logs", "Accessed activity logs")
def list_logs():
    """Return filtered activity logs with pagination."""
    try:
        # Extract query parameters
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action', '').strip()
        status = request.args.get('status', '').strip()
        resource_type = request.args.get('resource_type', '').strip()
        
        # Date filtering
        start_date_str = request.args.get('start_date', '').strip()
        end_date_str = request.args.get('end_date', '').strip()
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid start_date format"}), 400
                
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                # Add 24 hours to include the entire end date
                end_date = end_date + timedelta(days=1)
            except ValueError:
                return jsonify({"error": "Invalid end_date format"}), 400
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)  # Max 100 per page
        
        # Get filtered logs
        pagination = ActivityLog.get_filtered_logs(
            user_id=user_id if user_id else None,
            action=action if action else None,
            status=status if status else None,
            resource_type=resource_type if resource_type else None,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        # Convert to dictionaries
        logs = [log.to_dict() for log in pagination.items]
        
        # Get summary statistics
        total_logs = pagination.total
        
        # Get unique values for filter dropdowns
        users = db.session.query(User.id, User.email).all()
        actions = db.session.query(ActivityLog.action).distinct().order_by(ActivityLog.action).all()
        statuses = db.session.query(ActivityLog.status).distinct().order_by(ActivityLog.status).all()
        resource_types = db.session.query(ActivityLog.resource_type).distinct().filter(
            ActivityLog.resource_type.isnot(None)
        ).order_by(ActivityLog.resource_type).all()
        
        return jsonify({
            "logs": logs,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_logs,
                "pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next
            },
            "filters": {
                "users": [{"id": u.id, "email": u.email} for u in users],
                "actions": [a[0] for a in actions if a[0]],
                "statuses": [s[0] for s in statuses if s[0]],
                "resource_types": [rt[0] for rt in resource_types if rt[0]]
            },
            "summary": {
                "total_logs": total_logs,
                "filtered_count": len(logs)
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch logs: {str(e)}"}), 500


@bp.route("/export", methods=["GET"])
@admin_required  
@log_activity("export_logs", "Exported activity logs")
def export_logs():
    """Export logs as CSV."""
    try:
        # Same filtering logic as above
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action', '').strip()
        status = request.args.get('status', '').strip()
        resource_type = request.args.get('resource_type', '').strip()
        
        start_date_str = request.args.get('start_date', '').strip()
        end_date_str = request.args.get('end_date', '').strip()
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')) + timedelta(days=1)
        
        # Get all matching logs (no pagination for export)
        query = ActivityLog.query.join(User)
        
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
            
        logs = query.order_by(ActivityLog.created_at.desc()).limit(10000).all()  # Limit exports
        
        # Generate CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Date/Time', 'User Email', 'Action', 'Status', 'Resource Type', 
            'Resource ID', 'IP Address', 'Duration (ms)', 'Details'
        ])
        
        # Data rows
        for log in logs:
            writer.writerow([
                log.created_at.isoformat() if log.created_at else '',
                log.user.email if log.user else '',
                log.action or '',
                log.status or '',
                log.resource_type or '',
                log.resource_id or '',
                log.ip_address or '',
                log.duration_ms or '',
                log.details or ''
            ])
        
        output.seek(0)
        
        return jsonify({
            "csv_data": output.getvalue(),
            "filename": f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "count": len(logs)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to export logs: {str(e)}"}), 500


@bp.route("/stats", methods=["GET"])
@admin_required
@log_activity("view_log_stats", "Viewed activity log statistics")
def log_stats():
    """Get activity log statistics."""
    try:
        # Get date range for stats (default to last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        start_date_str = request.args.get('start_date', '').strip()
        end_date_str = request.args.get('end_date', '').strip()
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        # Activity by day
        daily_activity = db.session.query(
            db.func.date(ActivityLog.created_at).label('date'),
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date
        ).group_by(
            db.func.date(ActivityLog.created_at)
        ).order_by('date').all()
        
        # Activity by user - FIXED: Using text() for ORDER BY
        user_activity = db.session.query(
            User.email,
            db.func.count(ActivityLog.id).label('count')
        ).join(ActivityLog).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date
        ).group_by(User.email).order_by(text('count DESC')).limit(10).all()
        
        # Activity by action - FIXED: Using text() for ORDER BY
        action_activity = db.session.query(
            ActivityLog.action,
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date
        ).group_by(ActivityLog.action).order_by(text('count DESC')).limit(10).all()
        
        # Error rate
        total_actions = db.session.query(ActivityLog).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date
        ).count()
        
        error_actions = db.session.query(ActivityLog).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date,
            ActivityLog.status == 'error'
        ).count()
        
        error_rate = (error_actions / total_actions * 100) if total_actions > 0 else 0
        
        return jsonify({
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "error_actions": error_actions,
                "error_rate": round(error_rate, 2)
            },
            "daily_activity": [
                {"date": str(day.date), "count": day.count} 
                for day in daily_activity
            ],
            "top_users": [
                {"email": user.email, "count": user.count} 
                for user in user_activity
            ],
            "top_actions": [
                {"action": action.action, "count": action.count} 
                for action in action_activity
            ]
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500