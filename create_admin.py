#!/usr/bin/env python3
"""
Script to create or reset the admin user
Run this with: python create_admin.py
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from models import db, User

def create_admin():
    """Create or reset admin user"""
    app = create_app('production')

    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@zenpdf.com').first()

        if admin:
            print("Admin user already exists. Resetting password...")
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin.set_password(admin_password)
            db.session.commit()
            print("Admin password reset successfully!")
        else:
            print("Creating new admin user...")
            admin = User(
                username='admin',
                email='admin@zenpdf.com',
                is_admin=True,
                is_active=True,
                email_verified=True,
                subscription_tier='premium',
                created_at=datetime.utcnow()
            )
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")

        print("\nAdmin credentials:")
        print("  Email: admin@zenpdf.com")
        if os.environ.get('ADMIN_PASSWORD'):
            print("  Password: [Set via ADMIN_PASSWORD env var]")
        else:
            print("  Password: admin123")
            print("  WARNING: Using default password. Set ADMIN_PASSWORD env var for security!")

if __name__ == '__main__':
    create_admin()
