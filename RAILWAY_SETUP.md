# Railway Environment Variables Setup

## 🚨 IMPORTANT: Add These Environment Variables to Railway

The code has been pushed to GitHub and Railway will deploy it automatically. However, **you MUST add these environment variables in Railway** for the payment integration to work.

---

## Step 1: Access Railway Dashboard

1. Go to: https://railway.app/
2. Login to your account
3. Select your **ZenPDF** project
4. Click on your service (web service)

---

## Step 2: Add Environment Variables

Click on **Variables** tab and add these:

### Required Pesapal Variables

```bash
PESAPAL_CONSUMER_KEY=LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd
PESAPAL_CONSUMER_SECRET=FsMt3oRVio2gqIPdgAzEepPo0f4=
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

### How to Add in Railway

1. **PESAPAL_CONSUMER_KEY**
   - Click "+ New Variable"
   - Name: `PESAPAL_CONSUMER_KEY`
   - Value: `LD0ObzzrrGFV312qMFJrRxjMH1GKEkYd`
   - Click "Add"

2. **PESAPAL_CONSUMER_SECRET**
   - Click "+ New Variable"
   - Name: `PESAPAL_CONSUMER_SECRET`
   - Value: `FsMt3oRVio2gqIPdgAzEepPo0f4=`
   - Click "Add"

3. **PESAPAL_BASE_URL**
   - Click "+ New Variable"
   - Name: `PESAPAL_BASE_URL`
   - Value: `https://cybqa.pesapal.com/pesapalv3`
   - Click "Add"

4. **PESAPAL_IPN_URL**
   - Click "+ New Variable"
   - Name: `PESAPAL_IPN_URL`
   - Value: `https://bestpdfconverter.online/payment/ipn`
   - Click "Add"

5. **PESAPAL_CALLBACK_URL**
   - Click "+ New Variable"
   - Name: `PESAPAL_CALLBACK_URL`
   - Value: `https://bestpdfconverter.online/payment/callback`
   - Click "Add"

---

## Step 3: Restart/Redeploy

After adding all variables:

1. Railway will automatically redeploy
2. OR click "Deploy" button to trigger redeploy
3. Wait for deployment to complete (~2-3 minutes)

---

## Step 4: Verify Deployment

### Check Deployment Logs

In Railway dashboard:
1. Click on **Deployments** tab
2. Click on the latest deployment
3. View logs for any errors

**Look for**:
```
ZenPDF startup
* Running on http://0.0.0.0:5000
```

**Should NOT see**:
- Errors about missing Pesapal config
- Import errors for payment or pesapal_service
- 500 errors when accessing /payment/ routes

### Test Payment Endpoints

Once deployed, test these URLs:

```bash
# IPN endpoint (should return JSON)
curl -k https://bestpdfconverter.online/payment/ipn

# Expected response:
# Error or requires parameters, but should not be 404
```

---

## Step 5: Test the Integration

### 5.1 Visit Pricing Page

Go to: https://bestpdfconverter.online/pricing

### 5.2 Check "Upgrade to Premium" Button

- Should be visible under Premium plan
- Should be a working link (not disabled)

### 5.3 Try Clicking It

**If NOT logged in**: Should redirect to login
**If logged in**: Should redirect to Pesapal (or show error if credentials invalid)

---

## Troubleshooting

### Issue: Environment variables not showing

**Solution**:
- Make sure you're in the correct Railway project
- Check you're editing the web service (not database)
- Try refreshing the page

### Issue: Deployment failing

**Check logs for**:
- Missing dependencies: `pip install -r requirements.txt`
- Import errors: Check file names match
- Syntax errors: Check Python version (should be 3.7+)

### Issue: 404 on /payment/ routes

**Possible causes**:
- Environment variables not set
- Deployment not complete
- Railway cache issue

**Solution**:
```bash
# Clear Railway cache and redeploy
# In Railway dashboard:
1. Settings → "Clear Build Cache"
2. Then redeploy
```

### Issue: Still getting credential errors

Your current credentials are being rejected by Pesapal. You need to:

1. **Contact Pesapal Support**
   - Email: support@pesapal.com
   - Request valid API 3.0 credentials

2. **OR Register App in Pesapal Portal**
   - Login: https://developer.pesapal.com/
   - Register new app with your domain
   - Get new credentials

3. **Update Railway Variables**
   - Replace PESAPAL_CONSUMER_KEY
   - Replace PESAPAL_CONSUMER_SECRET
   - Railway will auto-redeploy

---

## Current Deployment Status

✅ Code pushed to GitHub
✅ Railway will auto-deploy
⏳ Need to add environment variables (YOU DO THIS)
⏳ Need valid Pesapal credentials
⬜ Ready to test payments

---

## Quick Commands for Verification

After Railway deploys, run these locally to test:

```bash
# Test IPN endpoint
curl -k https://bestpdfconverter.online/payment/ipn

# Test pricing page has payment button
curl -k https://bestpdfconverter.online/pricing | grep -i "payment.subscribe_premium"

# Check Railway logs
railway logs
```

---

## Summary

**What you need to do NOW:**

1. ✅ Open Railway dashboard
2. ✅ Go to your ZenPDF project
3. ✅ Click Variables tab
4. ✅ Add 5 Pesapal environment variables (see above)
5. ✅ Wait for auto-redeploy
6. ✅ Test the site

**Then:**
- Get valid Pesapal credentials from their support
- Update the credential variables in Railway
- Test payment flow

---

**The code is deployed! Just add the environment variables in Railway.** 🚀
