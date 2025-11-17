#!/usr/bin/env python3
"""
Database initialization script for ZenPDF
Run this to create database tables and optionally seed initial data
"""
import os
import sys
from app import create_app
from models import db, User
from datetime import datetime

def init_database():
    """Initialize database tables"""
    # Detect environment
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"Initializing database for environment: {env}")

    app = create_app(env)

    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️  Database tables may already exist: {e}")

        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@zenpdf.com').first()
        if not admin:
            print("\nCreating admin user...")
            admin = User(
                username='admin',
                email='admin@zenpdf.com',
                is_admin=True,
                is_active=True,
                email_verified=True,
                subscription_tier='premium',
                created_at=datetime.utcnow()
            )
            # Use environment variable for admin password if available
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created:")
            print("  Email: admin@zenpdf.com")
            if env == 'production':
                print("  Password: [Set via ADMIN_PASSWORD env var]")
            else:
                print("  Password: admin123")
                print("  ⚠️  IMPORTANT: Change this password in production!")
        else:
            print("\n✓ Admin user already exists")

        print("\n✅ Database initialization complete!")


if __name__ == '__main__':
    init_database()
