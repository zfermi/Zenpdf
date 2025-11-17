#!/usr/bin/env python3
"""
Database initialization script for ZenPDF
Run this to create database tables and optionally seed initial data
"""
from app_new import create_app
from models import db, User
from datetime import datetime

def init_database():
    """Initialize database tables"""
    app = create_app('development')

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")

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
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created:")
            print("  Email: admin@zenpdf.com")
            print("  Password: admin123")
            print("  ⚠️  IMPORTANT: Change this password in production!")
        else:
            print("\n✓ Admin user already exists")

        print("\n✅ Database initialization complete!")


if __name__ == '__main__':
    init_database()
