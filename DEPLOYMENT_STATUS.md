# Deployment Status & Checklist

## Current Issue

❌ **Payment button doesn't work** on https://bestpdfconverter.online/pricing

**Reason**: Payment integration code is pushed to GitHub, but Railway needs:
1. Environment variables to be added
2. Deployment to complete
3. Database to be initialized on Railway

---

## What's Been Done

✅ Code pushed to GitHub (commit: 7a2ddbd)
✅ Admin account created locally
✅ All payment files committed:
  - payment.py
  - pesapal_service.py
  - Updated app.py
  - Updated config.py
  - Updated requirements.txt

---

## What You MUST Do NOW

### Step 1: Add Environment Variables to Railway

**Go to**: https://railway.app/ → Your ZenPDF Project → Variables

**Add these 5 variables**:

```
PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd
PESAPAL_CONSUMER_SECRET=FsMt3oRVio2gqIPdgAzEepPo0f4=
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

**Also add** (for admin and database):

```
ADMIN_PASSWORD=YourSecurePassword123!
DATABASE_URL=your_postgresql_url_from_railway
```

### Step 2: Verify Railway Deployment

**Check Deployment Status**:
1. Go to Railway dashboard
2. Click "Deployments" tab
3. Look for latest deployment (should show commit: 7a2ddbd)
4. Status should be ✅ **Success** (not building or failed)

**If deployment is failed or stuck**:
- Check build logs for errors
- Look for missing dependencies
- Verify all files were pushed

### Step 3: Initialize Database on Railway

Once deployed, Railway needs to create database tables.

**Option A: Auto-create on first run**

The app is configured to create tables automatically when it starts.

**Option B: Manual creation via Railway CLI**

If tables aren't created:
```bash
# Login to Railway
railway login

# Link to your project
railway link

# Run database setup
railway run python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('Done!')"
```

### Step 4: Create Admin on Railway

After database exists:

```bash
# Via Railway CLI
railway run python create_admin.py
```

**OR** set ADMIN_PASSWORD env var and redeploy (admin will be created automatically on first login attempt).

---

## How to Verify It's Working

### Test 1: Check Pricing Page

```bash
curl https://bestpdfconverter.online/pricing | grep "payment.subscribe_premium"
```

**Should show**: URL with `payment.subscribe_premium`

### Test 2: Check Payment Routes

```bash
# IPN endpoint (should return JSON, not 404)
curl https://bestpdfconverter.online/payment/ipn
```

**Expected**: JSON response or error (NOT 404)

### Test 3: Click Payment Button

1. Login to site: https://bestpdfconverter.online/auth/login
2. Go to pricing: https://bestpdfconverter.online/pricing
3. Click "Upgrade to Premium"
4. **Should redirect to Pesapal** (or show error if credentials invalid)
5. **Should NOT**: Do nothing, 404, or stay on same page

---

## Troubleshooting

### Issue: Button does nothing when clicked

**Possible causes**:
1. ❌ Payment blueprint not registered → Check Railway logs
2. ❌ Environment variables not set → Add to Railway
3. ❌ Old code still deployed → Check deployment logs
4. ❌ JavaScript error → Check browser console
5. ❌ Not logged in → Login first

**Solutions**:

**1. Check if you're logged in**:
- Payment requires login
- Go to: https://bestpdfconverter.online/auth/login
- Login with admin or regular account
- Then try payment button

**2. Check Railway deployment**:
```bash
# View Railway logs
railway logs
```

**Look for**:
- "ZenPDF startup"
- No import errors for payment/pesapal_service
- No 500 errors

**3. Check environment variables are set**:
- Railway dashboard → Variables
- Should see all 5 PESAPAL_* variables
- If missing, add them

**4. Force redeploy**:
```bash
# Locally
git commit --allow-empty -m "Force redeploy"
git push origin main
```

### Issue: 404 on /payment routes

**Cause**: Payment blueprint not loaded

**Check**:
```bash
curl https://bestpdfconverter.online/payment/ipn
```

**If 404**: Railway hasn't deployed the new code

**Solutions**:
1. Check Railway deployments tab
2. Verify latest commit is deployed
3. Check build logs for errors
4. Manually trigger redeploy

### Issue: Invalid Pesapal credentials

**Expected**: This is normal! Your credentials are being rejected by Pesapal.

**When you click payment button**:
- You'll be redirected to payment page
- But then you'll see: "Failed to authenticate with Pesapal"

**This is OK for now** - it proves the integration is working, just need valid credentials.

**To fix**:
1. Contact Pesapal support: support@pesapal.com
2. Register app in Pesapal portal
3. Get valid API 3.0 credentials
4. Update Railway environment variables
5. Railway will auto-redeploy

---

## Quick Deployment Commands

Run these in order:

```bash
# 1. Check what's deployed
git log --oneline -3

# Should show:
# 7a2ddbd Trigger Railway redeploy
# 3e1dad0 Add Pesapal payment integration
# de8271e Rebuild Tailwind CSS

# 2. Verify Railway deployment status
railway status

# 3. View Railway logs
railway logs

# 4. If needed, force redeploy
git commit --allow-empty -m "Force deploy"
git push origin main
```

---

## Expected Behavior After Deployment

### 1. Pricing Page

**URL**: https://bestpdfconverter.online/pricing

**Should show**:
- "Upgrade to Premium" button under Premium plan
- Button is a link (not disabled)
- Clicking it redirects somewhere (not staying on same page)

### 2. When Logged In

**After login** → Click "Upgrade to Premium":
- Redirects to: `/payment/subscribe/premium`
- Shows loading or processes payment
- Then redirects to Pesapal OR shows error

### 3. When NOT Logged In

**Click "Upgrade to Premium"**:
- Shows: "Login to Subscribe" button
- Clicking redirects to login page

---

## Current Status

| Item | Status | Action Needed |
|------|--------|---------------|
| Code pushed to GitHub | ✅ Done | None |
| Railway deployment | ⏳ Check | Verify in dashboard |
| Environment variables | ❌ Missing | ADD THEM NOW |
| Database initialized | ❌ Unknown | Check after deploy |
| Admin created | ❌ Local only | Create on Railway |
| Pesapal credentials | ❌ Invalid | Contact Pesapal |

---

## Next Steps (In Order)

1. ✅ **Add environment variables to Railway** (MOST IMPORTANT)
2. ✅ **Verify Railway deployment completed**
3. ✅ **Check if database tables exist**
4. ✅ **Create admin account on Railway**
5. ✅ **Test payment button**
6. ✅ **Get valid Pesapal credentials**
7. ✅ **Update credentials in Railway**
8. ✅ **Test full payment flow**

---

## Railway Environment Variables Checklist

Add these in Railway dashboard → Variables:

- [ ] PESAPAL_CONSUMER_KEY
- [ ] PESAPAL_CONSUMER_SECRET
- [ ] PESAPAL_BASE_URL
- [ ] PESAPAL_IPN_URL
- [ ] PESAPAL_CALLBACK_URL
- [ ] ADMIN_PASSWORD (recommended)
- [ ] DATABASE_URL (should already exist)
- [ ] SECRET_KEY (should already exist)

---

## Contact Info

**Railway Support**: https://discord.gg/railway
**Pesapal Support**: support@pesapal.com
**Your Repo**: https://github.com/zfermi/Zenpdf

---

**Action Required**: Add environment variables to Railway NOW, then check deployment status.
