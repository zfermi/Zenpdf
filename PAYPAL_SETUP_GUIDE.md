# PayPal Integration Setup Guide

## Overview

Your payment system has been switched from Pesapal to **PayPal**, which is much simpler and more widely supported. PayPal accepts credit/debit cards directly within their checkout flow - users don't need a PayPal account!

## Why PayPal?

✅ **Accepts cards directly** - No PayPal account required
✅ **Easier integration** - Simple REST API
✅ **Better support** - Extensive documentation
✅ **Global reach** - Works in most countries
✅ **Instant credentials** - Sandbox ready immediately

## Step 1: Create PayPal Developer Account

### 1.1 Sign Up
1. Go to https://developer.paypal.com
2. Click "Log In" or "Sign Up"
3. Create account or use existing PayPal account
4. Access the Developer Dashboard

### 1.2 Get Sandbox Credentials
1. Once logged in, go to https://developer.paypal.com/dashboard
2. Click on "Apps & Credentials"
3. Make sure you're on the **"Sandbox"** tab
4. You'll see **"Default Application"** already created
5. Click on it to view credentials

**Copy these values:**
- **Client ID** (starts with `A...`)
- **Secret** (click "Show" to reveal, starts with `E...`)

## Step 2: Configure Environment Variables

### For Local Development (.env file):

Create or update your `.env` file:

```bash
# PayPal Sandbox (for testing)
PAYPAL_CLIENT_ID=AYour_Sandbox_Client_ID_Here
PAYPAL_CLIENT_SECRET=EYour_Sandbox_Secret_Here
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

### For Railway Production:

**Option A: Use Sandbox for Testing**
```bash
PAYPAL_CLIENT_ID=<your_sandbox_client_id>
PAYPAL_CLIENT_SECRET=<your_sandbox_secret>
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

**Option B: Use Live for Production**
1. Go to https://developer.paypal.com/dashboard
2. Switch to **"Live"** tab
3. Create a new app or use existing
4. Copy Live credentials

```bash
PAYPAL_CLIENT_ID=<your_live_client_id>
PAYPAL_CLIENT_SECRET=<your_live_secret>
PAYPAL_BASE_URL=https://api-m.paypal.com
```

## Step 3: Update Railway Environment Variables

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add/Update these variables:

```
PAYPAL_CLIENT_ID = <paste_your_client_id>
PAYPAL_CLIENT_SECRET = <paste_your_secret>
PAYPAL_BASE_URL = https://api-m.sandbox.paypal.com
```

**Important**: Remove the old Pesapal variables or they'll be ignored.

## Step 4: Deploy

### 4.1 Commit Changes
```bash
git add .
git commit -m "Switch from Pesapal to PayPal payment integration"
git push
```

### 4.2 Verify Deployment
Railway will automatically deploy. Check logs:
```bash
railway logs
```

Look for successful startup with no errors.

## Step 5: Test Payment Flow

### 5.1 Test with Sandbox

1. Go to your website: https://bestpdfconverter.online
2. Login to your account
3. Navigate to Pricing page
4. Click "Subscribe to Premium"
5. You'll be redirected to PayPal sandbox

**PayPal Sandbox Test Cards:**

PayPal provides test accounts. To use test cards:

1. Go to https://developer.paypal.com/dashboard
2. Navigate to "Sandbox" > "Accounts"
3. You'll see test buyer accounts (personal accounts)
4. Click on one to view email and password
5. Use these credentials to login on PayPal checkout page

**Or use test credit cards** (if card checkout is enabled):
- **Visa**: 4032039683435142
- **Mastercard**: 5425233430109903
- **Expiry**: Any future date (e.g., 12/2025)
- **CVV**: 123
- **Name**: Any name

### 5.2 Complete Test Payment

1. On PayPal page, login with test account or use test card
2. Click "Pay Now"
3. You'll be redirected back to your site
4. Check if subscription is activated
5. Your account should now show "Premium" tier

### 5.3 Verify in PayPal Dashboard

1. Go to https://developer.paypal.com/dashboard
2. Click "Sandbox" > "Accounts"
3. Find your merchant account (business account)
4. Login to view transactions
5. Verify payment was received

## How PayPal Payment Flow Works

```
┌─────────────┐
│ User clicks │
│ "Subscribe" │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│ Backend creates     │
│ PayPal order       │
│ (paypal_service.py)│
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│ User redirected to  │
│ PayPal checkout     │
│ (approve_url)       │
└──────┬──────────────┘
       │
  ┌────┴────┐
  │         │
  v         v
┌─────┐ ┌────────┐
│Pay  │ │Cancel  │
└──┬──┘ └───┬────┘
   │        │
   v        v
┌─────┐ ┌────────┐
│/success│/cancel│
└──┬──┘ └───────┘
   │
   v
┌──────────────────┐
│ Capture payment  │
│ Activate premium │
└──────────────────┘
```

## Important Files

| File | Purpose |
|------|---------|
| [paypal_service.py](paypal_service.py) | PayPal API integration |
| [payment.py](payment.py) | Payment routes (subscribe, success, cancel) |
| [config.py](config.py:73-77) | PayPal configuration |
| [.env.example](.env.example:26-32) | Environment variable template |

## API Endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| `/payment/subscribe/premium` | GET | Initiate payment |
| `/payment/success` | GET | Handle successful payment |
| `/payment/cancel` | GET | Handle cancelled payment |
| `/payment/webhook` | POST | Receive PayPal webhooks (optional) |
| `/payment/status/<order_id>` | GET | Check order status |

## Troubleshooting

### Error: "Failed to authenticate with PayPal"

**Solution**: Check your credentials
```bash
# Verify environment variables are set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Client ID:', os.getenv('PAYPAL_CLIENT_ID')[:20] if os.getenv('PAYPAL_CLIENT_ID') else 'NOT SET')"
```

### Error: "Failed to create PayPal order"

**Possible causes:**
1. **Invalid amount** - Must be at least 0.01
2. **Invalid currency** - Use supported codes (USD, EUR, GBP, etc.)
3. **Wrong base URL** - Sandbox vs Live mismatch

**Check logs:**
```bash
railway logs | grep PayPal
```

### Payment succeeds but subscription not activated

**Solutions:**
1. Check Railway logs for errors in `/success` route
2. Verify database connection is working
3. Ensure user is logged in when payment completes

### Sandbox vs Live Issues

| Environment | Base URL | Where to get credentials |
|-------------|----------|--------------------------|
| Sandbox (Test) | `https://api-m.sandbox.paypal.com` | Dashboard > Sandbox tab |
| Live (Production) | `https://api-m.paypal.com` | Dashboard > Live tab |

**Make sure base URL matches your credentials!**

## Going Live (Production)

When ready for real payments:

1. **Complete PayPal business verification**
   - Verify your business with PayPal
   - Connect bank account
   - May take 1-3 days

2. **Create Live App**
   - Go to https://developer.paypal.com/dashboard
   - Switch to "Live" tab
   - Create new app or use default
   - Copy Live credentials

3. **Update Environment Variables**
   ```bash
   PAYPAL_CLIENT_ID=<live_client_id>
   PAYPAL_CLIENT_SECRET=<live_secret>
   PAYPAL_BASE_URL=https://api-m.paypal.com
   ```

4. **Test thoroughly**
   - Start with small test transaction
   - Verify funds appear in your PayPal account
   - Test refund process

5. **Monitor transactions**
   - Check PayPal dashboard regularly
   - Set up email notifications
   - Monitor Railway logs for errors

## Pricing Notes

Current premium price: **$9.99/month**

Configured in [config.py](config.py:77):
```python
PREMIUM_PRICE = 999  # $9.99 in cents
```

To change price:
1. Update `PREMIUM_PRICE` in config.py
2. Update pricing page to reflect new price
3. Redeploy

## Testing Checklist

- [ ] PayPal credentials configured in Railway
- [ ] Deployed to Railway successfully
- [ ] Can access pricing page
- [ ] Subscribe button redirects to PayPal
- [ ] Can complete payment with test account/card
- [ ] Redirected back to site after payment
- [ ] Subscription activated (shows "Premium")
- [ ] Premium features work (higher limits, etc.)

## Support Resources

- **PayPal Developer Portal**: https://developer.paypal.com
- **API Documentation**: https://developer.paypal.com/docs/api/orders/v2/
- **Sandbox Testing**: https://developer.paypal.com/tools/sandbox/
- **Test Cards**: https://developer.paypal.com/tools/sandbox/card-testing/

## Summary

✅ **What's changed:**
- Switched from Pesapal to PayPal
- Simpler integration with REST API
- Cards accepted directly in PayPal checkout
- Easier testing with sandbox

✅ **What you need:**
1. PayPal Developer account (free)
2. Sandbox credentials (instant)
3. Update Railway environment variables
4. Deploy and test

✅ **Next steps:**
1. Get PayPal credentials from https://developer.paypal.com/dashboard
2. Update Railway variables
3. Push code: `git push`
4. Test payment flow

That's it! Much simpler than Pesapal! 🎉
