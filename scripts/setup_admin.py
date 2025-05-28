"""Create initial admin user and authorized users."""

import os
import sys

# Add parent directory to Python path to find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User


def create_admin_user():
    """Create the initial admin user."""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin_email = "serban.damian@lensa.ro"
        existing_user = User.query.filter_by(email=admin_email).first()
        
        if existing_user:
            print(f"Admin user {admin_email} already exists.")
            return
        
        # Create admin user with empty password (will be set on first login)
        admin_user = User(
            email=admin_email,
            is_admin=True,
            password_hash=""  # Empty password hash - user will set on first login
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ Admin user created: {admin_email}")
        print("👉 User can now login and will be prompted to set password")


def add_authorized_users():
    """Add other authorized users."""
    app = create_app()
    
    authorized_emails = [
        "admin@lensa.ro"
        # Add more authorized emails here
    ]
    
    with app.app_context():
        for email in authorized_emails:
            existing_user = User.query.filter_by(email=email).first()
            
            if not existing_user:
                user = User(
                    email=email,
                    is_admin=False,
                    password_hash=""  # Empty password hash
                )
                
                db.session.add(user)
                print(f"✅ Authorized user created: {email}")
        
        db.session.commit()


def main():
    """Run the setup script."""
    print("🚀 Setting up admin user and authorized users...")
    
    create_admin_user()
    add_authorized_users()
    
    print("\n🎉 Setup complete!")
    print("Users can now login with their authorized emails and set their passwords.")


if __name__ == "__main__":
    main()