# setup_admin.py - Run this script to set up the admin system

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

# Import your existing app and db
from hotel_app import app, db
from hotel_app.models import Admin

def create_admin_tables():
    """Create the admin table if it doesn't exist"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created/updated successfully!")

def create_default_admin():
    """Create a default admin user"""
    with app.app_context():
        # Check if admin already exists
        existing_admin = Admin.query.first()
        if existing_admin:
            print("⚠️  Admin user already exists!")
            print(f"Username: {existing_admin.username}")
            return
        
        # Create default admin
        admin = Admin(
            username='admin',
            email='admin@example.com'
        )
        admin.set_password('admin123')  # Change this password!
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Default admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("⚠️  IMPORTANT: Please change the password after first login!")

def update_user_model():
    from sqlalchemy import text

    """Add is_active column to User model if it doesn't exist"""
    with app.app_context():
        try:
            # Try to add the is_active column if it doesn't exist
            db.engine.connect("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("✅ Added is_active column to User table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  is_active column already exists in User table")
            else:
                print(f"❌ Error updating User table: {e}")

def setup_admin_system():
    """Complete setup of the admin system"""
    print("🚀 Setting up Admin System...")
    print("=" * 50)
    
    # Step 1: Create tables
    print("1. Creating/updating database tables...")
    create_admin_tables()
    
    # Step 2: Update user model
    print("\n2. Updating User model...")
    update_user_model()
    
    # Step 3: Create default admin
    print("\n3. Creating default admin user...")
    create_default_admin()
    
    print("\n" + "=" * 50)
    print("✅ Admin system setup complete!")
    print("\nNext steps:")
    print("1. Start your Flask application")
    print("2. Navigate to /admin/login")
    print("3. Login with username: admin, password: admin123")
    print("4. Change the default password immediately!")
    print("5. Update your main app routes to prevent conflicts")

# Additional helper functions

def create_additional_admin(username, email, password):
    """Create an additional admin user"""
    with app.app_context():
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"❌ Admin with username '{username}' already exists!")
            return False
        
        existing_email = Admin.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Admin with email '{email}' already exists!")
            return False
        
        # Create new admin
        admin = Admin(
            username=username,
            email=email
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user '{username}' created successfully!")
        return True

def reset_admin_password(username, new_password):
    """Reset an admin user's password"""
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            print(f"❌ Admin with username '{username}' not found!")
            return False
        
        admin.set_password(new_password)
        db.session.commit()
        
        print(f"✅ Password reset for admin '{username}'!")
        return True

# CLI commands for Flask-CLI (optional)
def init_admin_commands(app):
    """Add CLI commands to your Flask app"""
    
    @app.cli.command()
    def setup_admin():
        """Set up the admin system"""
        setup_admin_system()
    
    @app.cli.command()
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username, email, password):
        """Create a new admin user"""
        create_additional_admin(username, email, password)
    
    @app.cli.command()
    @click.argument('username')
    @click.argument('new_password')
    def reset_password(username, new_password):
        """Reset an admin user's password"""
        reset_admin_password(username, new_password)

# Security configurations
ADMIN_SESSION_CONFIG = {
    'SESSION_COOKIE_SECURE': True,  # Enable in production with HTTPS
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
}

def configure_admin_security(app):
    """Configure security settings for admin"""
    for key, value in ADMIN_SESSION_CONFIG.items():
        app.config[key] = value

# Route protection middleware
def protect_admin_routes():
    """Middleware to protect admin routes"""
    @app.before_request
    def admin_route_protection():
        if request.endpoint and request.endpoint.startswith('admin'):
            if request.endpoint == 'admin_login':
                return  # Allow access to login page
            
            if 'admin_id' not in session:
                return redirect(url_for('admin_login'))
            
            # Check if admin is still valid
            admin = Admin.query.get(session['admin_id'])
            if not admin or not admin.is_active:
                session.pop('admin_id', None)
                flash('Session expired. Please login again.', 'warning')
                return redirect(url_for('admin_login'))

if __name__ == "__main__":
    # Run setup if this file is executed directly
    setup_admin_system()