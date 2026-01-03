"""
Database migration script to add AI credits columns to existing users.
Run this script once after deploying the updated models.py
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db

def migrate_database():
    """Add AI credits columns to the users table"""
    app = create_app()
    
    with app.app_context():
        # Check if columns already exist
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'ai_credits_used' not in columns:
                print("Adding ai_credits_used column...")
                db.session.execute(db.text(
                    "ALTER TABLE users ADD COLUMN ai_credits_used INTEGER DEFAULT 0 NOT NULL"
                ))
                print("✓ Added ai_credits_used column")
            else:
                print("✓ ai_credits_used column already exists")
            
            if 'ai_credits_reset_date' not in columns:
                print("Adding ai_credits_reset_date column...")
                db.session.execute(db.text(
                    "ALTER TABLE users ADD COLUMN ai_credits_reset_date DATETIME"
                ))
                print("✓ Added ai_credits_reset_date column")
            else:
                print("✓ ai_credits_reset_date column already exists")
            
            db.session.commit()
            print("\n✅ Database migration complete!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            db.session.rollback()
            
            # Try to create all tables if they don't exist
            print("Attempting to create all tables...")
            db.create_all()
            print("✓ Tables created/updated")

if __name__ == '__main__':
    migrate_database()
