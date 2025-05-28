# scripts/migrate_enhanced_logs_fixed.py - Fixed migration script using direct SQL
import os
import sys
import sqlite3

def find_database():
    """Find the database file location."""
    possible_paths = [
        "./instance/campaigns.db",
        "instance/campaigns.db", 
        "campaigns.db",
        "/app/instance/campaigns.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def migrate_activity_logs():
    """Migrate activity logs using direct SQLite commands."""
    print("🔄 Starting activity logs migration...")
    
    db_path = find_database()
    
    if not db_path:
        print("❌ Database file not found in any of these locations:")
        possible_paths = [
            "./instance/campaigns.db",
            "instance/campaigns.db", 
            "campaigns.db",
            "/app/instance/campaigns.db"
        ]
        for path in possible_paths:
            print(f"   - {path}")
        return False
    
    print(f"📍 Found database at: {db_path}")
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if activity_logs table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='activity_logs'
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists:
            print("❌ activity_logs table not found!")
            conn.close()
            return False
        
        print("✅ Found activity_logs table")
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(activity_logs)")
        columns_info = cursor.fetchall()
        existing_columns = [col[1] for col in columns_info]
        print(f"📋 Current columns: {existing_columns}")
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM activity_logs")
        record_count = cursor.fetchone()[0]
        print(f"📊 Found {record_count} existing activity log records")
        
        # Add new columns if they don't exist
        new_columns = [
            ("status", "VARCHAR(20) DEFAULT 'success'"),
            ("details", "TEXT"),
            ("resource_type", "VARCHAR(50)"),
            ("resource_id", "VARCHAR(50)"),
            ("duration_ms", "INTEGER")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE activity_logs ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    if "duplicate column name" in str(e):
                        print(f"⏭️ Column {column_name} already exists")
                    else:
                        print(f"⚠️ Could not add column {column_name}: {e}")
            else:
                print(f"⏭️ Column {column_name} already exists")
        
        # Update existing records with default status
        try:
            cursor.execute("UPDATE activity_logs SET status = 'success' WHERE status IS NULL OR status = ''")
            updated_rows = cursor.rowcount
            print(f"✅ Updated {updated_rows} existing records with default status")
        except sqlite3.Error as e:
            print(f"⚠️ Could not update existing records: {e}")
        
        # Create performance indexes
        indexes_to_create = [
            ('idx_activity_logs_action', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action)'),
            ('idx_activity_logs_status', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_status ON activity_logs(status)'),
            ('idx_activity_logs_resource_type', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_resource_type ON activity_logs(resource_type)'),
            ('idx_activity_logs_created_at', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at)'),
            ('idx_activity_logs_user_date', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_user_date ON activity_logs(user_id, created_at)'),
            ('idx_activity_logs_action_date', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_action_date ON activity_logs(action, created_at)'),
            ('idx_activity_logs_resource_date', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_resource_date ON activity_logs(resource_type, created_at)'),
            ('idx_activity_logs_status_date', 'CREATE INDEX IF NOT EXISTS idx_activity_logs_status_date ON activity_logs(status, created_at)')
        ]
        
        print("\n🔗 Creating performance indexes...")
        for index_name, sql in indexes_to_create:
            try:
                cursor.execute(sql)
                print(f"✅ Created index: {index_name}")
            except sqlite3.Error as e:
                print(f"⚠️ Could not create index {index_name}: {e}")
        
        # Commit all changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(activity_logs)")
        final_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE status IS NOT NULL")
        records_with_status = cursor.fetchone()[0]
        
        print(f"\n📋 Final columns: {final_columns}")
        print(f"📊 Records with status: {records_with_status}/{record_count}")
        
        conn.close()
        print("\n🎉 Migration completed successfully!")
        return True, db_path  # Return the db_path for verification
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False, None


def verify_migration(db_path):
    """Verify that the migration was successful using the correct database path."""
    print("\n🔍 Verifying migration...")
    
    if not db_path:
        db_path = find_database()
        
    if not db_path:
        print("❌ Could not find database for verification")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if all new columns exist
        cursor.execute("PRAGMA table_info(activity_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['status', 'details', 'resource_type', 'resource_id', 'duration_ms']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            conn.close()
            return False
        
        print(f"✅ All required columns present: {required_columns}")
        
        # Check if indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_activity_logs_%'")
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✅ Created indexes: {len(indexes)} indexes")
        
        # Test a sample query with the new columns
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status IS NOT NULL THEN 1 END) as with_status,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count
            FROM activity_logs
        """)
        
        stats = cursor.fetchone()
        print(f"✅ Query test successful:")
        print(f"   - Total records: {stats[0]}")
        print(f"   - With status: {stats[1]}")
        print(f"   - Success status: {stats[2]}")
        
        conn.close()
        print("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False


def check_runtime_environment():
    """Check if we're running in the expected Flask environment."""
    print("🔍 Checking runtime environment...")
    
    # Check if we're in the right directory
    if os.path.exists("app.py") and os.path.exists("models"):
        print("✅ Found Flask application files")
    else:
        print("⚠️ Flask application files not found in current directory")
    
    # Check database location
    db_path = find_database()
    if db_path:
        print(f"✅ Database found at: {db_path}")
    else:
        print("❌ Database not found")
    
    # Check if we can import Flask modules
    try:
        sys.path.insert(0, os.getcwd())
        from models import db, ActivityLog
        print("✅ Can import Flask models")
        return True
    except Exception as e:
        print(f"⚠️ Cannot import Flask models: {e}")
        print("   - This is normal if Flask app isn't initialized")
        return False


def main():
    """Run the migration at runtime."""
    print("🚀 Enhanced Activity Logs Migration (Runtime)")
    print("=" * 60)
    
    # Check environment
    flask_available = check_runtime_environment()
    
    # Run migration
    print("\n" + "=" * 60)
    success, db_path = migrate_activity_logs()
    
    if success:
        if verify_migration(db_path):
            print("\n🎊 All operations completed successfully!")
            print("\n📝 Next steps:")
            if flask_available:
                print("   1. Enhanced logging is now active in your Flask app")
                print("   2. Visit http://localhost:5173/logs to see the activity logs")
                print("   3. All new actions will be logged with detailed information")
            else:
                print("   1. Restart your Flask application")
                print("   2. Enhanced logging will be active after restart")
                print("   3. Visit http://localhost:5173/logs to see the activity logs")
            
            print("\n🎯 Features now available:")
            print("   ✅ User attribution for all actions")
            print("   ✅ Status tracking (success/error/warning)")
            print("   ✅ Resource type and ID tracking")
            print("   ✅ Request duration monitoring")
            print("   ✅ Detailed context logging")
            print("   ✅ Advanced filtering and search")
            print("   ✅ CSV export functionality")
            print("   ✅ Activity statistics dashboard")
            
        else:
            print("\n⚠️ Migration completed but verification failed.")
            return 1
    else:
        print("\n❌ Migration failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())