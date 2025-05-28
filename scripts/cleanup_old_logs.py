# scripts/cleanup_old_logs.py - Log cleanup utility
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to Python path to find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, ActivityLog
from config import Config


def cleanup_old_logs(days_to_keep=None):
    """Remove activity logs older than specified days."""
    app = create_app()
    
    if days_to_keep is None:
        days_to_keep = getattr(Config, 'MAX_LOG_RETENTION_DAYS', 90)
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        print(f"🧹 Cleaning up activity logs older than {days_to_keep} days...")
        print(f"📅 Cutoff date: {cutoff_date}")
        
        # Count logs to be deleted
        old_logs_count = ActivityLog.query.filter(
            ActivityLog.created_at < cutoff_date
        ).count()
        
        if old_logs_count == 0:
            print("✅ No old logs to clean up.")
            return
        
        print(f"🗑️ Found {old_logs_count} logs to delete...")
        
        # Delete old logs
        try:
            deleted_count = ActivityLog.query.filter(
                ActivityLog.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            print(f"✅ Successfully deleted {deleted_count} old activity logs.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to delete old logs: {e}")


def main():
    """Run the log cleanup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up old activity logs')
    parser.add_argument(
        '--days', 
        type=int, 
        help='Number of days to keep (default: from config)'
    )
    
    args = parser.parse_args()
    cleanup_old_logs(args.days)


if __name__ == "__main__":
    main()