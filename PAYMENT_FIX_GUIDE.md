# Payment Integration Fix - Consumer Key Unknown Error

## Problem Summary

When trying to subscribe to premium, you were seeing an error:
```
Failed to launch 'problem:%20consumer_key_unknown%20%7C%20Advice:%20%3E%20%20%7C'
because the scheme does not have a registered handler.
```

## Root Cause

The issue had **two parts**:

### 1. Incorrect Base URL Configuration
The code was using hardcoded Pesapal URLs (`demo.pesapal.com`) instead of the configured URL (`cybqa.pesapal.com/pesapalv3`). This has been **FIXED**.

### 2. Invalid Consumer Key for Environment ⚠️ **STILL NEEDS FIXING**
Your consumer key is not recognized by `cybqa.pesapal.com`. This means either:
- The consumer key was issued for a different Pesapal environment
- The consumer key has not been activated yet
- The Pesapal account needs additional setup

## What Was Fixed

### Code Changes

1. **Updated `pesapal_service_v2.py`**:
   - Added `base_url` parameter to `__init__` method
   - Now uses the configured `PESAPAL_BASE_URL` instead of hardcoded values
   - Strips `/v3` or `/pesapalv3` suffix for API 2.0 compatibility

2. **Added Error Handling**:
   - Detects `problem:` URLs from Pesapal
   - Shows clear error messages instead of browser scheme errors
   - Prevents redirect to invalid URLs

3. **Created Diagnostic Tools**:
   - `check_pesapal_config.py` - Verifies environment variables
   - `test_payment_fix.py` - Tests payment integration

## How to Fix the Consumer Key Issue

### Option 1: Get Credentials for cybqa.pesapal.com (Recommended for Testing)

1. **Login to Pesapal Demo/Sandbox**:
   - Go to https://developer.pesapal.com or https://cybqa.pesapal.com
   - Login or create a demo account

2. **Get API Credentials**:
   - Navigate to API settings or Developer settings
   - Copy your Consumer Key and Consumer Secret for the **demo/sandbox environment**

3. **Update Environment Variables**:
   ```bash
   # In Railway dashboard or .env file
   PESAPAL_CONSUMER_KEY=your_demo_consumer_key_here
   PESAPAL_CONSUMER_SECRET=your_demo_consumer_secret_here
   PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
   ```

### Option 2: Use Production Credentials

If you have production credentials:

1. **Get Production Credentials** from your live Pesapal account

2. **Update Environment Variables**:
   ```bash
   PESAPAL_CONSUMER_KEY=your_prod_consumer_key_here
   PESAPAL_CONSUMER_SECRET=your_prod_consumer_secret_here
   PESAPAL_BASE_URL=https://www.pesapal.com  # No /v3 suffix for API 2.0
   ```

### Option 3: Use demo.pesapal.com with Your Current Key

If your key is for `demo.pesapal.com`:

```bash
PESAPAL_BASE_URL=https://demo.pesapal.com
# Keep existing PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET
```

## Verifying the Fix

### 1. Check Configuration
```bash
python check_pesapal_config.py
```

Expected output:
```
✅ CONFIGURATION COMPLETE
All required Pesapal configuration is set.
```

### 2. Test Payment Integration
```bash
python test_payment_fix.py
```

If credentials are valid, you should see:
```
✅ Payment order created successfully!
  Redirect URL: https://...
```

If credentials are still invalid:
```
❌ Payment order creation failed:
  Error: Payment provider error: Problem: consumer_key_unknown
```

### 3. Test in Browser

1. Deploy the updated code to Railway
2. Login to your app
3. Go to Pricing page
4. Click "Subscribe to Premium"
5. You should either:
   - Be redirected to Pesapal payment page (if credentials valid)
   - See a clear error message (if credentials invalid)

You will **NOT** see the browser "unregistered scheme" error anymore.

## Deployment Steps

### 1. Commit and Push Changes
```bash
git add pesapal_service_v2.py payment.py check_pesapal_config.py test_payment_fix.py
git commit -m "Fix Pesapal consumer_key_unknown error and add better error handling"
git push
```

### 2. Update Railway Environment Variables

Go to Railway dashboard and set:
```
PESAPAL_CONSUMER_KEY=<your_valid_key>
PESAPAL_CONSUMER_SECRET=<your_valid_secret>
PESAPAL_BASE_URL=<matching_environment_url>
```

### 3. Verify Deployment

After deployment:
```bash
# Check Railway logs
railway logs

# Look for successful startup and no Pesapal errors
```

## Error Messages Reference

| Error Message | Meaning | Fix |
|--------------|---------|-----|
| `consumer_key_unknown` | Key not recognized by environment | Update consumer key or change PESAPAL_BASE_URL |
| `invalid_consumer_key_or_secret_provided` | Key/secret mismatch | Verify both key and secret are correct |
| `Payment provider error: ...` | Pesapal API error | Check error message for specific issue |
| `Invalid response from payment provider` | Unexpected response format | Check Pesapal API status |

## Testing Checklist

- [ ] `python check_pesapal_config.py` shows all config set
- [ ] `python test_payment_fix.py` creates payment order successfully
- [ ] Subscribe button redirects to Pesapal (not browser error)
- [ ] Payment callback works after test payment
- [ ] User subscription is activated after successful payment

## Next Steps

1. **Get valid Pesapal credentials** for your chosen environment
2. **Update environment variables** in Railway
3. **Redeploy** the application
4. **Test** the payment flow end-to-end

## Support

If you continue having issues:

1. Check Railway logs: `railway logs`
2. Verify Pesapal account status in their dashboard
3. Ensure callback URLs are whitelisted in Pesapal settings
4. Contact Pesapal support for credential verification
