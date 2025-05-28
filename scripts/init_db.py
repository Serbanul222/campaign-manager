import os
import sys

# Add parent directory to Python path to find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.db_setup import create_tables
from scripts.migrate_enhanced_logs import migrate_activity_logs


def main():
    """Initialize the database with enhanced logging support."""
    print("🚀 Initializing Campaign Manager Database")
    print("=" * 50)
    
    app = create_app()
    
    # Create all tables
    print("📋 Creating database tables...")
    create_tables(app)
    print("✅ Database tables created")
    
    # Run enhanced logging migration
    print("\n📈 Setting up enhanced activity logging...")
    migrate_activity_logs()
    
    print("\n🎉 Database initialization complete!")
    print("💡 Next steps:")
    print("   1. Run 'python scripts/setup_admin.py' to create admin user")
    print("   2. Start the application with 'flask run'")


if __name__ == "__main__":
    main()