"""
Configuration classes for ZenPDF application
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""

    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'ZenPDF'
    VERSION = '1.0.0'

    # Database
    # Fix for Railway PostgreSQL URL (postgres:// -> postgresql://)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url or f'sqlite:///{os.path.join(basedir, "zenpdf.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # File upload settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for free tier
    MAX_FILE_SIZE_PREMIUM = 100 * 1024 * 1024  # 100MB for premium
    MAX_MERGE_FILES = 5
    MAX_MERGE_FILES_PREMIUM = 20
    ALLOWED_EXTENSIONS = {'pdf'}
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    SPLIT_FOLDER = os.path.join(basedir, 'split_folder')
    MERGED_FOLDER = os.path.join(basedir, 'merged_folder')

    # Session
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Remember me cookie
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Rate limiting (free tier)
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    DAILY_OPERATION_LIMIT_FREE = 5
    DAILY_OPERATION_LIMIT_PREMIUM = 1000  # Effectively unlimited

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@zenpdf.com')

    # Stripe (payment processing)
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_ID_PREMIUM = os.environ.get('STRIPE_PRICE_ID_PREMIUM')  # Monthly premium price ID

    # Security headers (Talisman)
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_STRICT_TRANSPORT_SECURITY_MAX_AGE = 31536000  # 1 year
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "https://pagead2.googlesyndication.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "data:"],
    }

    # WTForms CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit

    # File cleanup
    FILE_CLEANUP_HOURS = 1


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # Disable HTTPS requirements in development
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    TALISMAN_FORCE_HTTPS = False

    # Use SQLite for development only if DATABASE_URL not set
    if not os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "zenpdf_dev.db")}'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Warn if DATABASE_URL not set but don't fail
    # App will fall back to SQLite if DATABASE_URL not provided
    def __init__(self):
        if not os.environ.get('DATABASE_URL'):
            import warnings
            warnings.warn(
                "DATABASE_URL not set - using SQLite. "
                "For production, add PostgreSQL database in Railway dashboard.",
                RuntimeWarning
            )
        if not os.environ.get('SECRET_KEY'):
            import warnings
            warnings.warn(
                "SECRET_KEY not set - using default (INSECURE!). "
                "Set SECRET_KEY environment variable in Railway.",
                RuntimeWarning
            )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
