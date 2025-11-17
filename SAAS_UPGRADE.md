# ZenPDF SaaS Upgrade Guide

## Overview

ZenPDF has been upgraded from a simple MVP (v1.0) to a full-fledged SaaS application (v2.0) with:

- ✅ User authentication & authorization
- ✅ Database layer (PostgreSQL/SQLite)
- ✅ Subscription management
- ✅ Usage tracking & analytics
- ✅ Rate limiting
- ✅ CSRF protection
- ✅ Security headers
- ✅ User dashboard
- ✅ Premium/Free tier system

---

## What's New in v2.0

### 1. **User Authentication System**
- User registration and login
- Password hashing with bcrypt
- Remember me functionality
- Session management
- Protected routes

### 2. **Database Layer**
- PostgreSQL support (production)
- SQLite support (development)
- SQLAlchemy ORM
- Models: User, UsageRecord, Subscription, APIKey, SystemMetrics

### 3. **Subscription Tiers**
- **Free Tier**: 5 operations/day, 10MB files
- **Premium Tier**: Unlimited operations, 100MB files
- **Enterprise**: Custom limits (contact sales)

### 4. **Usage Tracking**
- Track every PDF operation
- Analytics dashboard
- Daily/monthly usage stats
- IP and user agent logging

### 5. **Security Enhancements**
- CSRF protection with Flask-WTF
- Security headers with Flask-Talisman
- Rate limiting with Flask-Limiter
- Input validation and sanitization
- SQL injection protection (ORM)

### 6. **User Dashboard**
- Usage statistics
- Recent activity
- Account information
- Upgrade prompts

---

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for rate limiting)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL` (PostgreSQL for production, SQLite for development)
- Email settings (optional, for password reset)
- Stripe keys (optional, for payments)

### Step 3: Initialize Database

```bash
python init_db.py
```

This creates:
- All database tables
- Admin user (email: admin@zenpdf.com, password: admin123)

**⚠️ IMPORTANT**: Change the admin password immediately!

### Step 4: Run the Application

**Development:**
```bash
python app_new.py
```

**Production (with gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app_new:create_app('production')"
```

---

## Migration from v1.0 to v2.0

### File Changes

**New Files:**
- `app_new.py` - Refactored application with auth
- `models.py` - Database models
- `config.py` - Configuration classes
- `forms.py` - WTForms for authentication
- `auth.py` - Authentication blueprint
- `init_db.py` - Database initialization script
- `templates/auth/login.html`
- `templates/auth/register.html`
- `templates/dashboard.html`
- `templates/pricing.html`

**Modified Files:**
- `requirements.txt` - Added database and auth dependencies

**Original Files (kept for reference):**
- `app.py` - Original application (can be removed after migration)

### Database Schema

**Users Table:**
```sql
- id (primary key)
- email (unique, indexed)
- username (unique, indexed)
- password_hash
- created_at
- last_login
- is_active
- is_admin
- email_verified
- subscription_tier (free/premium/enterprise)
- subscription_start
- subscription_end
- stripe_customer_id
```

**Usage Records Table:**
```sql
- id (primary key)
- user_id (foreign key)
- operation_type (split/merge/compress/rotate)
- file_size
- pages_processed
- created_at (indexed)
- ip_address
- user_agent
- success
- error_message
```

---

## API Changes

### Route Updates

All PDF operation routes now require authentication:

**Before (v1.0):**
```python
@app.route('/split')
def split_pdf():
    # Anyone can access
```

**After (v2.0):**
```python
@app.route('/split')
@login_required
@limiter.limit("30 per hour")
def split_pdf():
    # Must be logged in
    # Rate limited
```

### New Routes

**Authentication:**
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - User registration
- `GET /auth/logout` - User logout

**Dashboard:**
- `GET /dashboard` - User dashboard (requires auth)

**Public:**
- `GET /pricing` - Pricing page

---

## Configuration

### Environment-Specific Configs

**Development** (`config.DevelopmentConfig`):
- SQLite database
- Debug mode enabled
- HTTPS not required
- In-memory rate limiting

**Production** (`config.ProductionConfig`):
- PostgreSQL database
- Debug mode disabled
- HTTPS enforced
- Redis rate limiting
- Security headers enabled

Set environment: `FLASK_ENV=production` or `FLASK_ENV=development`

---

## Security Features

### 1. CSRF Protection
All forms include CSRF tokens:
```html
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- form fields -->
</form>
```

### 2. Security Headers (Production Only)
- `Strict-Transport-Security` - Force HTTPS
- `Content-Security-Policy` - Prevent XSS
- `X-Frame-Options` - Prevent clickjacking
- `X-Content-Type-Options` - Prevent MIME sniffing

### 3. Rate Limiting
- 200 requests per day (default)
- 50 requests per hour (default)
- 30 requests per hour for PDF operations

### 4. Password Security
- Bcrypt hashing
- Minimum 8 characters
- Stored as hash, never plaintext

---

## Usage Limits

### Free Tier
- **Operations**: 5 per day
- **File Size**: 10 MB
- **Features**: All basic PDF tools
- **Ads**: Enabled

### Premium Tier ($9.99/month)
- **Operations**: Unlimited
- **File Size**: 100 MB
- **Features**: All tools + priority support
- **Ads**: Disabled
- **API Access**: Enabled

### Checking Limits in Code
```python
# Check if user can perform operation
can_proceed, error_msg = check_usage_limit()
if not can_proceed:
    flash(error_msg, 'error')
    return redirect(url_for('dashboard'))

# Record operation
record_usage(
    operation_type='split',
    file_size=file_size,
    pages_processed=page_count
)
```

---

## Testing

### Create Test User

```python
from app_new import create_app
from models import db, User

app = create_app('development')
with app.app_context():
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
```

### Test Login Flow

1. Visit `/auth/register`
2. Create account
3. Login at `/auth/login`
4. Access dashboard at `/dashboard`
5. Use PDF tools (tracked in usage)

---

## Deployment

### Railway / Heroku

1. Set environment variables in platform dashboard
2. Add PostgreSQL database addon
3. Set `FLASK_ENV=production`
4. Deploy with `gunicorn`

**Procfile:**
```
web: gunicorn "app_new:create_app('production')"
```

### Database Migrations (Future)

For schema changes, use Flask-Migrate:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## Stripe Integration (TODO)

To enable premium subscriptions:

1. Create Stripe account
2. Get API keys (dashboard → Developers → API keys)
3. Create Premium product and price
4. Set environment variables:
   - `STRIPE_PUBLIC_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PRICE_ID_PREMIUM`
5. Implement webhook handler for subscription events

---

## Admin Features

### Admin User
- Created by `init_db.py`
- Email: `admin@zenpdf.com`
- Can access all user data
- Can view system metrics

### Admin Dashboard (TODO)
Future features:
- User management
- System analytics
- Revenue tracking
- Support tickets

---

## Monitoring & Analytics

### Usage Tracking
All operations are logged in `usage_records` table:
- Operation type
- User ID
- File size
- Pages processed
- Success/failure
- IP address
- Timestamp

### System Metrics
Tracked in `system_metrics` table:
- Total operations
- Total users
- Premium users
- Revenue
- Storage used

---

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: unable to open database file
```
**Solution**: Run `python init_db.py` to create database

### CSRF Token Missing
```
flask_wtf.csrf.CSRFError: The CSRF token is missing
```
**Solution**: Include `{{ form.hidden_tag() }}` in form templates

### Rate Limit Exceeded
```
429 Too Many Requests
```
**Solution**: Wait or upgrade to premium

---

## Next Steps

### Priority 1 (Immediate)
- [ ] Test authentication flow
- [ ] Configure email service
- [ ] Set up production database
- [ ] Deploy to production

### Priority 2 (Short-term)
- [ ] Integrate Stripe payments
- [ ] Add email verification
- [ ] Implement password reset
- [ ] Create admin dashboard

### Priority 3 (Medium-term)
- [ ] Add OAuth (Google, GitHub)
- [ ] Implement API keys
- [ ] Add webhooks for subscriptions
- [ ] Create mobile app

---

## Support

For issues or questions:
- GitHub Issues: [Create issue](https://github.com/yourusername/zenpdf/issues)
- Email: support@zenpdf.com
- Documentation: [docs.zenpdf.com](https://docs.zenpdf.com)

---

## License

MIT License - see LICENSE file for details
