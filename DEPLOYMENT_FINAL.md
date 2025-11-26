# ZenPDF Production Deployment Guide

## 🚀 Quick Start for Railway

### Step 1: Set Environment Variables

In Railway dashboard, add these variables:

```bash
SECRET_KEY=ed5eddef3548207313b022f46b9baa8cdb7120b2ebd12f902ecbb46c5fbb1fbf
FLASK_ENV=production
FLASK_DEBUG=False
```

### Step 2: Add PostgreSQL

1. Click "New" → "Database" → "PostgreSQL"
2. Railway auto-sets `DATABASE_URL`

### Step 3: Deploy

Push to GitHub - Railway auto-deploys!

### Step 4: Change Admin Password

Default login:
- Email: `admin@zenpdf.com`
- Password: `admin123`

**Change immediately via:**
```bash
python create_admin.py
```

---

## 🔒 Security Checklist

- [ ] `SECRET_KEY` set (64+ chars)
- [ ] PostgreSQL connected
- [ ] `.env` NOT in git
- [ ] Admin password changed
- [ ] `/health` endpoint tested

---

## 📊 Key Endpoints

- **Home**: `/`
- **Health**: `/health`
- **Login**: `/auth/login`
- **Dashboard**: `/dashboard`
- **Admin**: `/admin` (admin only)

---

## 🆘 Troubleshooting

**Database errors**: Check `DATABASE_URL` is set in Railway

**429 errors**: Rate limit hit - adjust in `app.py` or add Redis

**File upload fails**: Check folders auto-create on startup

---

## 📈 What's Fixed

✅ Secure SECRET_KEY generated
✅ Database credentials removed from git
✅ All PDF operations implemented
✅ Comprehensive error handling
✅ Production logging configured
✅ Health check endpoint added
✅ Rate limiting on auth routes
✅ Backup files removed

---

**Ready to ship! 🎉**
