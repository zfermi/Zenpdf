# Deployment Guide for bestpdfconverter.online

## 🎯 Domain: bestpdfconverter.online

This guide will help you deploy the Pesapal payment integration to your live domain.

---

## Pre-Deployment Status

✅ **Code Integration**: Complete
✅ **Payment Routes**: Implemented
✅ **Error Handling**: In place
✅ **Security**: CSP headers configured
✅ **Documentation**: Complete
⏳ **Pesapal Credentials**: Need verification
⬜ **Testing**: Pending valid credentials
⬜ **Live Deployment**: Ready when credentials work

---

## Step 1: Fix Pesapal Credentials

Your current credentials are being rejected. Here's how to get working ones:

### Option A: Check Pesapal Developer Portal

1. **Login**: https://developer.pesapal.com/
2. **Navigate to**: API 3.0 → Credentials
3. **Look for**:
   - Demo/Sandbox credentials (for testing)
   - Production credentials (for live)

### Option B: Register Your App in Pesapal

1. **Login**: https://developer.pesapal.com/
2. **Go to**: Apps / My Applications
3. **Click**: Register New App
4. **Fill in**:
   ```
   App Name: ZenPDF
   App URL: https://bestpdfconverter.online
   Callback URL: https://bestpdfconverter.online/payment/callback
   IPN URL: https://bestpdfconverter.online/payment/ipn
   ```
5. **Save** and copy the new credentials

### Option C: Contact Pesapal Support

If the portal doesn't show credentials:

**Email**: support@pesapal.com

**Message template**:
```
Subject: API 3.0 Credentials Request for bestpdfconverter.online

Hello Pesapal Support,

I need API 3.0 credentials for my PDF conversion service:
- Business Name: ZenPDF
- Domain: bestpdfconverter.online
- Integration: Card payment processing

Please provide:
1. Consumer Key
2. Consumer Secret
3. Confirmation that API 3.0 access is enabled

I'm getting "invalid_consumer_key_or_secret_provided" error
with my current credentials.

Thank you!
```

---

## Step 2: Update Environment Variables

Once you have valid credentials:

### Edit .env file

```bash
# Update these with working credentials
PESAPAL_CONSUMER_KEY=your_new_consumer_key_here
PESAPAL_CONSUMER_SECRET=your_new_consumer_secret_here

# Start with sandbox for testing
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3

# Your domain URLs (already correct)
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

### Test the credentials

```bash
python test_both_urls.py
```

**Expected output**:
```
✓ SUCCESS! Valid credentials for SANDBOX
```

---

## Step 3: Deploy to Your Server

### If using Railway:

1. **Push to Git**:
   ```bash
   git add .
   git commit -m "Add Pesapal payment integration"
   git push origin main
   ```

2. **Set Environment Variables in Railway**:
   - Go to Railway dashboard
   - Click your project
   - Go to Variables tab
   - Add:
     ```
     PESAPAL_CONSUMER_KEY=your_key
     PESAPAL_CONSUMER_SECRET=your_secret
     PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
     PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
     PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
     ```

3. **Deploy**: Railway will auto-deploy on push

### If using other hosting (Heroku, DigitalOcean, etc.):

1. **Upload code** to your server
2. **Set environment variables** in hosting panel
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Restart application**:
   ```bash
   # Depends on your hosting
   systemctl restart zenpdf  # or
   supervisorctl restart zenpdf  # or
   pm2 restart zenpdf
   ```

---

## Step 4: Verify SSL Certificate

Pesapal requires HTTPS for all callbacks.

### Check SSL:
```bash
curl -I https://bestpdfconverter.online
```

**Look for**:
```
HTTP/2 200
...
```

### If SSL is missing:

1. **Get free SSL** from Let's Encrypt
2. **Use Cloudflare** (automatic SSL)
3. **Use your hosting's** SSL certificate

Most modern hosts provide SSL automatically. Railway does this by default.

---

## Step 5: Whitelist Your Domain in Pesapal

1. **Login**: https://developer.pesapal.com/
2. **Go to**: Settings → Domains / Allowed Domains
3. **Add**: `bestpdfconverter.online`
4. **Save**

This allows Pesapal to redirect back to your domain.

---

## Step 6: Test Payment Flow (Sandbox)

### 6.1 Access Your Site

Navigate to: https://bestpdfconverter.online/pricing

### 6.2 Create Test Account

1. Click "Sign Up"
2. Create a test account
3. Verify email (if required)
4. Login

### 6.3 Initiate Payment

1. On pricing page, click **"Upgrade to Premium"**
2. You should be redirected to Pesapal sandbox
3. You'll see a payment form

### 6.4 Complete Test Payment

Use these test card details:

```
Card Number: 4111111111111111
Expiry: 12/25 (any future date)
CVV: 123 (any 3 digits)
Name: Test User
```

### 6.5 Verify Success

After payment:
- You should be redirected back to your site
- URL: `https://bestpdfconverter.online/payment/callback?OrderTrackingId=...`
- You should see: "Payment successful!" message
- Dashboard should show "Premium" status

### 6.6 Check Logs

```bash
# On your server
tail -f logs/zenpdf.log | grep -i payment
```

**Look for**:
```
Payment initiated for user X
Payment callback - Status: completed
Premium subscription activated for user X
```

---

## Step 7: Test IPN (Background Notification)

### 7.1 Check IPN Registration

```bash
python test_pesapal.py
```

**Look for**:
```
✓ Found 1 registered IPN(s)
  - IPN ID: xxx
    URL: https://bestpdfconverter.online/payment/ipn
```

### 7.2 Verify IPN Endpoint

```bash
curl "https://bestpdfconverter.online/payment/ipn?OrderTrackingId=test"
```

**Expected response**:
```json
{"status":"success","message":"IPN processed"}
```

### 7.3 Monitor IPN Logs

After making a payment:

```bash
tail -f logs/zenpdf.log | grep -i ipn
```

**Look for**:
```
IPN received - Tracking: xxx
Premium subscription activated via IPN
```

---

## Step 8: Switch to Production (When Ready)

After successful testing in sandbox:

### 8.1 Get Production Credentials

1. Login to Pesapal
2. Get **Production** API 3.0 credentials
3. They're different from sandbox credentials

### 8.2 Update Environment

Change in your .env or hosting panel:

```bash
# Change from sandbox to production
PESAPAL_BASE_URL=https://pay.pesapal.com/v3

# Use production credentials
PESAPAL_CONSUMER_KEY=prod_consumer_key
PESAPAL_CONSUMER_SECRET=prod_consumer_secret
```

### 8.3 Test with Real Card

1. Make a small test purchase ($0.01 if possible, or minimum)
2. Use a real card
3. Verify payment appears in Pesapal dashboard
4. Verify subscription updates correctly
5. Verify IPN is received

### 8.4 Monitor First Transactions

Keep logs open and watch first few real payments:

```bash
tail -f logs/zenpdf.log
```

---

## Step 9: Post-Deployment Checklist

After going live, verify:

- [ ] Can access pricing page: https://bestpdfconverter.online/pricing
- [ ] "Upgrade to Premium" button works
- [ ] Redirects to Pesapal payment page
- [ ] Payment completes successfully
- [ ] Redirects back to site after payment
- [ ] User subscription updates to Premium
- [ ] Dashboard shows Premium status
- [ ] IPN notifications are received
- [ ] Logs show payment activity
- [ ] No errors in logs
- [ ] SSL certificate is valid
- [ ] Domain is whitelisted in Pesapal

---

## Monitoring & Maintenance

### Daily Checks (First Week)

```bash
# Check for payment errors
tail -n 100 logs/zenpdf.log | grep -i error

# Check payment success rate
tail -n 100 logs/zenpdf.log | grep -i "payment.*success"

# Check IPN delivery
tail -n 100 logs/zenpdf.log | grep -i ipn
```

### Weekly Tasks

1. Login to Pesapal dashboard
2. Review transaction history
3. Check for failed payments
4. Reconcile with your database
5. Download transaction reports

### Monthly Tasks

1. Audit subscription status accuracy
2. Review payment completion times
3. Analyze failed payment reasons
4. Plan improvements based on data

---

## Troubleshooting

### Issue: Payment button doesn't work

**Check**:
```bash
# View page source
curl https://bestpdfconverter.online/pricing | grep "Upgrade to Premium"
```

**Should contain**:
```html
href="{{ url_for('payment.subscribe_premium') }}"
```

### Issue: Redirect to Pesapal fails

**Check application logs**:
```bash
tail -f logs/zenpdf.log
```

**Common issues**:
- Invalid credentials → Update credentials
- Network timeout → Check internet connectivity
- SSL errors → Verify certificate

### Issue: Callback doesn't update subscription

**Check**:
```bash
# Test callback endpoint
curl "https://bestpdfconverter.online/payment/callback"
```

**Common issues**:
- Database connection → Check DATABASE_URL
- User not logged in → Callback requires login
- Invalid tracking ID → Check Pesapal response

### Issue: IPN not received

**Check**:
```bash
# Test IPN endpoint
curl https://bestpdfconverter.online/payment/ipn
```

**Common issues**:
- Firewall blocking → Allow Pesapal IPs
- URL not registered → Check IPN list
- Server down → Check uptime

---

## URLs Quick Reference

Copy these when configuring Pesapal:

```
Domain: bestpdfconverter.online
Callback: https://bestpdfconverter.online/payment/callback
IPN: https://bestpdfconverter.online/payment/ipn
App Name: ZenPDF
```

---

## Support Contacts

**Pesapal**:
- Email: support@pesapal.com
- Portal: https://developer.pesapal.com/support
- Docs: https://developer.pesapal.com/api-3.0

**Your Integration**:
- All docs in project folder
- Main guide: PESAPAL_INTEGRATION.md
- URLs: PESAPAL_URLS.md
- Troubleshooting: PESAPAL_SETUP_TROUBLESHOOTING.md

---

## Current Status Summary

| Component | Status |
|-----------|--------|
| Code Integration | ✅ Complete |
| Payment Routes | ✅ Ready |
| Error Handling | ✅ Implemented |
| Security Headers | ✅ Configured |
| SSL Certificate | ✅ Required (verify) |
| Domain Whitelist | ⏳ Add to Pesapal |
| Pesapal Credentials | ⏳ Need valid ones |
| Sandbox Testing | ⬜ Pending |
| Production Deploy | ⬜ Pending |

---

## Next Immediate Steps

1. **Get valid Pesapal credentials** (see Step 1)
2. **Update .env file** with new credentials
3. **Test with**: `python test_both_urls.py`
4. **Deploy to server** (Railway or your host)
5. **Test payment flow** in sandbox
6. **Go live** when ready

---

**Your domain is ready for Pesapal integration!** 🚀

Just get valid credentials from Pesapal and you're good to go.
