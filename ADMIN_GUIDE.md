# Admin Guide - ZenPDF

## Admin Login Credentials

### Default Admin Account

**Email**: `admin@zenpdf.com`
**Password**: `admin123`

⚠️ **IMPORTANT**: Change this password immediately in production!

---

## How to Login as Admin

### Step 1: Access the Login Page

Go to: https://bestpdfconverter.online/auth/login

### Step 2: Enter Admin Credentials

- **Email**: admin@zenpdf.com
- **Password**: admin123

### Step 3: Access Admin Panel

After login, navigate to:
- **URL**: https://bestpdfconverter.online/admin
- **OR**: Click "Admin" button in the navigation bar (visible only to admin users)

---

## Admin Panel Features

### Dashboard Overview

The admin panel shows:

#### 1. **System Statistics**
- **Total Users**: All registered users
- **Active Users**: Users with active accounts
- **Premium Users**: Users with paid subscriptions
- **Total Operations**: All PDF operations performed
- **Today's Operations**: Operations performed today

#### 2. **User Management**

View all users with:
- Username
- Email
- Account created date
- Subscription tier (Free/Premium/Enterprise)
- Active status
- Admin status

#### 3. **User Actions**

For each user, you can:

**Toggle Active Status**:
- Activate/Deactivate user accounts
- Deactivated users cannot login

**Update Subscription Tier**:
- Change: Free → Premium → Enterprise
- Manually upgrade users
- Set subscription dates automatically

**Grant/Revoke Admin**:
- Make users administrators
- Remove admin privileges
- Cannot remove admin from yourself (safety)

#### 4. **Recent Operations**

View last 20 operations across all users:
- Operation type (split, merge, compress, rotate, pdf2word)
- User who performed it
- Timestamp
- File size
- Pages processed
- Success/failure status

---

## Viewing Paid Users & Revenue

### Current Implementation

The admin panel shows:
- **Premium Users Count**: Number of paid subscribers
- **User Subscription Tiers**: Individual user payment status

### To See Detailed Payment Information

Currently, payment tracking is done through:

1. **Premium Users Count**
   - Shows total number of paying customers
   - Located in admin dashboard statistics

2. **Individual User Subscriptions**
   - View each user's subscription tier
   - See subscription start/end dates
   - Check if subscription is active

3. **Pesapal Dashboard** (for actual transactions)
   - Login to: https://www.pesapal.com/merchant/
   - View all transactions
   - Download financial reports
   - See actual revenue

### Revenue Calculation

**Monthly Revenue (estimated)**:
```
Premium Users × $9.99/month = Monthly Revenue
```

Example: 10 premium users = 10 × $9.99 = $99.90/month

---

## Admin Operations

### 1. Manually Upgrade a User to Premium

**Steps**:
1. Login as admin
2. Go to admin panel
3. Find the user
4. Click "Update Tier" dropdown
5. Select "Premium"
6. Click "Update"
7. Subscription valid for 1 year from today

**Use case**:
- Comp a user's subscription
- Resolve payment issues
- Provide trial access

### 2. Deactivate a User

**Steps**:
1. Find user in admin panel
2. Click "Deactivate" button
3. User account suspended
4. User cannot login

**Use case**:
- Ban abusive users
- Suspend accounts for violation
- Temporary account freeze

### 3. Grant Admin Privileges

**Steps**:
1. Find user in admin panel
2. Click "Make Admin" button
3. User becomes admin
4. Can access admin panel

**Use case**:
- Add team members as admins
- Delegate admin tasks

### 4. View User Activity

**Steps**:
1. Check "Recent Operations" section
2. Filter by user (manually scan)
3. See what operations user performed

**Use case**:
- Monitor user behavior
- Detect abuse
- Analyze usage patterns

---

## Changing Admin Password

### Method 1: Set Environment Variable

**Locally** (.env file):
```bash
ADMIN_PASSWORD=your_secure_password_here
```

Then run:
```bash
python create_admin.py
```

**On Railway**:
1. Go to Railway dashboard
2. Add variable: `ADMIN_PASSWORD=your_secure_password`
3. SSH into Railway and run: `python create_admin.py`

### Method 2: Via Database (Advanced)

```python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@zenpdf.com').first()
    admin.set_password('new_secure_password')
    db.session.commit()
    print("Password updated!")
```

---

## Security Best Practices

### 1. Change Default Password

⚠️ **CRITICAL**: Never use `admin123` in production!

Set strong password:
```bash
# In .env or Railway
ADMIN_PASSWORD=SecurePassword123!@#
```

### 2. Limit Admin Accounts

- Only give admin access to trusted people
- Review admin list regularly
- Remove admin from former employees

### 3. Monitor Admin Actions

- Check admin panel regularly
- Review user modifications
- Look for suspicious activity

### 4. Use Strong Credentials

Admin password should:
- Be at least 12 characters
- Include uppercase, lowercase, numbers, symbols
- Not be reused from other sites
- Be stored securely (password manager)

---

## Revenue Tracking Enhancement (Future)

To add detailed revenue tracking to admin panel, we can add:

### Payment Records Table

Track each payment:
- User ID
- Amount paid
- Payment date
- Payment method
- Pesapal transaction ID
- Status (completed/failed/refunded)

### Revenue Dashboard

Show:
- **Today's Revenue**: Sum of payments today
- **This Month's Revenue**: Sum of payments this month
- **Total Revenue**: All-time revenue
- **Average Revenue per User**: Total / Premium Users
- **Monthly Recurring Revenue (MRR)**: Active subscriptions × $9.99
- **Revenue Chart**: Graph showing revenue over time

### Export Reports

- Generate CSV/PDF reports
- Filter by date range
- Group by payment method
- Show refunds separately

**Would you like me to implement this enhanced revenue tracking?**

---

## Common Admin Tasks

### Task 1: Check Total Premium Users

1. Login as admin
2. View "Premium Users" statistic
3. Shows count of all paying customers

### Task 2: Find Specific User

1. Go to admin panel
2. Scroll through user list
3. OR use browser search (Ctrl+F) for email/username

### Task 3: Manually Process Payment

If user paid but subscription not updated:

1. Find user in admin panel
2. Click "Update Tier" → "Premium"
3. Subscription activated for 1 year

### Task 4: Handle Refund

1. Process refund in Pesapal dashboard
2. Find user in admin panel
3. Change tier back to "Free"
4. User loses premium access

### Task 5: View System Health

Check statistics:
- **Total Operations**: System usage
- **Active Users**: User engagement
- **Today's Operations**: Current activity

---

## Troubleshooting

### Can't Access Admin Panel

**Problem**: "Access denied. Admin privileges required."

**Solution**:
- Verify you're logged in as admin@zenpdf.com
- Check user.is_admin flag in database
- Re-run create_admin.py if needed

### Can't See Revenue

**Problem**: No revenue information in admin panel

**Solution**:
- Current system shows premium user count only
- For detailed revenue, login to Pesapal dashboard
- Future enhancement can add payment tracking

### User List Not Loading

**Problem**: Admin panel shows no users

**Solution**:
- Check database connection
- Verify DATABASE_URL is set
- Check application logs for errors

---

## Admin Panel URLs

| Page | URL |
|------|-----|
| Login | https://bestpdfconverter.online/auth/login |
| Admin Panel | https://bestpdfconverter.online/admin |
| Dashboard | https://bestpdfconverter.online/dashboard |
| Pricing | https://bestpdfconverter.online/pricing |

---

## Creating Additional Admins

### Method 1: Via Admin Panel

1. Have user register normally
2. Login as admin
3. Find new user in admin panel
4. Click "Make Admin"

### Method 2: Via Script

```python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    # Find existing user
    user = User.query.filter_by(email='user@example.com').first()

    # Make admin
    user.is_admin = True
    db.session.commit()
    print(f"{user.email} is now an admin!")
```

---

## Summary

### Quick Reference

**Login**: admin@zenpdf.com / admin123
**Admin Panel**: https://bestpdfconverter.online/admin
**Change Password**: Set ADMIN_PASSWORD env var
**View Revenue**: Pesapal dashboard + Premium user count
**Manage Users**: Admin panel → User actions

### Key Capabilities

✅ View all users and statistics
✅ Manage user subscriptions
✅ Activate/deactivate accounts
✅ Grant admin privileges
✅ Monitor system operations
✅ Track premium users
⏳ Detailed revenue tracking (future enhancement)

---

**You now have full admin control over your ZenPDF application!** 🎯
