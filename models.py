"""
Database models for ZenPDF SaaS application
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    """User model for authentication and account management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # User metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Subscription info
    subscription_tier = db.Column(db.String(20), default='free', nullable=False)  # 'free', 'premium', 'enterprise'
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(100), unique=True)

    # Relationships
    usage_records = db.relationship('UsageRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_premium(self):
        """Check if user has active premium subscription"""
        if self.subscription_tier == 'free':
            return False
        if self.subscription_end and self.subscription_end > datetime.utcnow():
            return True
        return False

    def get_daily_usage_count(self, operation_type=None):
        """Get count of operations performed today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = self.usage_records.filter(UsageRecord.created_at >= today_start)
        if operation_type:
            query = query.filter(UsageRecord.operation_type == operation_type)
        return query.count()

    def get_monthly_usage_count(self, operation_type=None):
        """Get count of operations performed this month"""
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = self.usage_records.filter(UsageRecord.created_at >= month_start)
        if operation_type:
            query = query.filter(UsageRecord.operation_type == operation_type)
        return query.count()

    def can_perform_operation(self):
        """Check if user can perform an operation based on their tier limits"""
        if self.is_premium:
            return True  # Unlimited for premium users

        # Free tier: 5 operations per day
        daily_count = self.get_daily_usage_count()
        return daily_count < 5


class UsageRecord(db.Model):
    """Track user operations for analytics and rate limiting"""
    __tablename__ = 'usage_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Operation details
    operation_type = db.Column(db.String(50), nullable=False, index=True)  # 'split', 'merge', 'compress', 'rotate'
    file_size = db.Column(db.Integer)  # Size in bytes
    pages_processed = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f'<UsageRecord {self.operation_type} by User {self.user_id}>'


class APIKey(db.Model):
    """API keys for programmatic access"""
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    key_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    key_prefix = db.Column(db.String(20), nullable=False)  # First 8 chars for display (e.g., "zenpdf_abc12345...")
    name = db.Column(db.String(100), nullable=False)  # User-defined name

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Rate limiting
    requests_count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f'<APIKey {self.key_prefix}... for User {self.user_id}>'

    @property
    def is_expired(self):
        """Check if API key has expired"""
        if self.expires_at and self.expires_at < datetime.utcnow():
            return True
        return False

    @property
    def is_valid(self):
        """Check if API key is valid and active"""
        return self.is_active and not self.is_expired


class Subscription(db.Model):
    """Subscription history and billing records"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Stripe integration
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_invoice_id = db.Column(db.String(100))

    # Subscription details
    tier = db.Column(db.String(20), nullable=False)  # 'premium', 'enterprise'
    status = db.Column(db.String(20), nullable=False)  # 'active', 'canceled', 'past_due', 'trialing'
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    currency = db.Column(db.String(3), default='usd', nullable=False)

    # Dates
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    canceled_at = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)

    # Relationship
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))

    def __repr__(self):
        return f'<Subscription {self.tier} for User {self.user_id}>'


class SystemMetrics(db.Model):
    """Track system-wide metrics for monitoring"""
    __tablename__ = 'system_metrics'

    id = db.Column(db.Integer, primary_key=True)

    # Metrics
    total_operations = db.Column(db.Integer, default=0, nullable=False)
    total_users = db.Column(db.Integer, default=0, nullable=False)
    total_premium_users = db.Column(db.Integer, default=0, nullable=False)
    total_revenue = db.Column(db.Integer, default=0, nullable=False)  # In cents

    # Storage
    total_storage_used = db.Column(db.BigInteger, default=0, nullable=False)  # In bytes

    # Timestamp
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<SystemMetrics at {self.recorded_at}>'
