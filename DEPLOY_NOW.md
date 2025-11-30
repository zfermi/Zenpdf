# Deploy to Railway - Step by Step

## Quick Deployment Guide

Follow these steps **IN ORDER** to deploy your payment integration to Railway.

---

## Step 1: Login to Railway

```bash
railway login
```

This will:
1. Open your browser
2. Ask you to authorize Railway CLI
3. Log you in

---

## Step 2: Link to Your Project

```bash
railway link
```

This will:
1. Show a list of your Railway projects
2. Select your ZenPDF/Best Pdf Converter project
3. Link this folder to that project

---

## Step 3: Add Environment Variables

Run these commands **ONE BY ONE**:

```bash
railway variables set PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd

railway variables set PESAPAL_CONSUMER_SECRET=FsMt3oRVio2gqIPdgAzEepPo0f4=

railway variables set PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3

railway variables set PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn

railway variables set PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

**Optional but recommended**:
```bash
railway variables set ADMIN_PASSWORD=YourSecurePassword123
```

---

## Step 4: Trigger Deployment

Railway should auto-deploy when you add variables, but you can force it:

```bash
railway up
```

OR just wait 2-3 minutes for auto-deployment.

---

## Step 5: Watch Deployment Logs

```bash
railway logs
```

**Look for**:
- ✅ "Best Pdf Converter startup"
- ✅ "Running on http://0.0.0.0:..."
- ❌ NO import errors
- ❌ NO missing module errors

Press `Ctrl+C` to exit logs.

---

## Step 6: Initialize Database on Railway

After deployment succeeds:

```bash
railway run python create_admin.py
```

This will:
- Create database tables (if they don't exist)
- Create admin account with email: admin@bestpdfconverter.online
- Password: admin123 (or your ADMIN_PASSWORD if set)

---

## Step 7: Test Your Site

1. **Open**: https://bestpdfconverter.online/pricing
2. **Login**: https://bestpdfconverter.online/auth/login
   - If no account, register first
3. **Click**: "Upgrade to Premium"
4. **Should**: Redirect to Pesapal (or show auth error if credentials invalid)

---

## Quick Command Reference

```bash
# Login
railway login

# Link project
railway link

# Add variables (run each separately)
railway variables set PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd
railway variables set PESAPAL_CONSUMER_SECRET=FsMt3oRVio2gqIPdgAzEepPo0f4=
railway variables set PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
railway variables set PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
railway variables set PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback

# View all variables
railway variables

# Deploy
railway up

# Watch logs
railway logs

# Create admin
railway run python create_admin.py

# Check deployment status
railway status
```

---

## Troubleshooting

### Issue: "Unauthorized. Please login"

**Solution**:
```bash
railway login
```

### Issue: "No project linked"

**Solution**:
```bash
railway link
```
Then select your project from the list.

### Issue: Deployment failing

**Check logs**:
```bash
railway logs
```

**Common issues**:
- Missing dependencies → Check requirements.txt
- Import errors → Make sure all files pushed to git
- Database errors → Run `railway run python create_admin.py`

### Issue: Variables not setting

**View current variables**:
```bash
railway variables
```

**Delete and re-add**:
```bash
railway variables delete PESAPAL_CONSUMER_KEY
railway variables set PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd
```

---

## Verification Checklist

After deployment:

- [ ] Railway logs show "Best Pdf Converter startup"
- [ ] No errors in logs
- [ ] Variables are set (check with `railway variables`)
- [ ] Admin created (run `railway run python create_admin.py`)
- [ ] Pricing page loads: https://bestpdfconverter.online/pricing
- [ ] Payment button appears
- [ ] Clicking button redirects (not 404)

---

## Alternative: Use Railway Dashboard

If CLI doesn't work, you can do everything via web dashboard:

1. **Open**: https://railway.app/
2. **Select**: Your project
3. **Click**: Variables tab
4. **Add**: Each Pesapal variable manually
5. **Wait**: For auto-deployment
6. **Check**: Deployments tab for status

---

## What Happens Next

Once deployed:

1. ✅ Payment routes will be live
2. ✅ "Upgrade to Premium" button will work
3. ✅ Users can start payment flow
4. ⚠️ Pesapal auth will fail (expected - need valid credentials)
5. ✅ Admin panel will be accessible

---

## Final Steps After Deployment

### 1. Test Payment Flow
- Login to site
- Click "Upgrade to Premium"
- Should redirect to Pesapal

### 2. Get Valid Pesapal Credentials
- Contact: support@pesapal.com
- OR: Register at https://developer.pesapal.com/
- Update Railway variables with new credentials

### 3. Test Real Payment
- Use test card: 4111111111111111
- Complete payment
- Verify subscription activated

---

## Quick Start (Copy-Paste)

```bash
# Step 1: Login
railway login

# Step 2: Link project
railway link

# Step 3: Add variables
railway variables set PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd
railway variables set PESAPAL_CONSUMER_SECRET=FsMt3oRVio2gqIPdgAzEepPo0f4=
railway variables set PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
railway variables set PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
railway variables set PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback

# Step 4: Wait for deployment (or force it)
railway up

# Step 5: Watch logs
railway logs

# Step 6: Create admin
railway run python create_admin.py

# Done! Test at: https://bestpdfconverter.online/pricing
```

---

**You're ready to deploy! Just run those commands.** 🚀
