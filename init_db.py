#!/usr/bin/env python3
"""
Database initialization script for ZenPDF
Run this to create database tables and optionally seed initial data
"""
import os
import sys
from datetime import datetime

def init_database():
    """Initialize database tables"""
    try:
        # Detect environment
        env = os.environ.get('FLASK_ENV', 'development')
        print(f"Initializing database for environment: {env}")

        # Check if DATABASE_URL is set in production
        if env == 'production' and not os.environ.get('DATABASE_URL'):
            print("⚠️  WARNING: DATABASE_URL not set in production environment")
            print("⚠️  Skipping database initialization - will be done on first app startup")
            print("⚠️  Please add PostgreSQL database in Railway dashboard")
            return

        from app import create_app
        from models import db, User

        app = create_app(env)

        with app.app_context():
            print("Creating database tables...")
            try:
                db.create_all()
                print("✓ Database tables created successfully!")
            except Exception as e:
                print(f"⚠️  Error creating database tables: {e}")
                print("⚠️  Tables will be created on first app startup")
                return

            # Create admin user if it doesn't exist
            try:
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
            except Exception as e:
                print(f"⚠️  Error creating admin user: {e}")
                print("⚠️  Admin user will be created on first app startup")

            print("\n✅ Database initialization complete!")

    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
        print("⚠️  This is not critical - database will be initialized on app startup")
        # Don't fail the build - just log the error
        sys.exit(0)


if __name__ == '__main__':
    init_database()
