# PayPal Integration - Quick Start

## ✅ What's Done

Your payment system has been **completely switched from Pesapal to PayPal**!

### Benefits:
- ✅ **Cards accepted directly** - Users don't need PayPal account
- ✅ **Much simpler** - Easy REST API integration
- ✅ **Better support** - Extensive PayPal documentation
- ✅ **Instant credentials** - Sandbox ready immediately

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get PayPal Credentials

1. Go to https://developer.paypal.com/dashboard
2. Login (or create account)
3. You'll see **"Default Application"** under Sandbox
4. Click it to view credentials
5. Copy **Client ID** and **Secret**

### Step 2: Update Railway

1. Go to Railway dashboard
2. Select your project
3. Click "Variables"
4. Add these 3 variables:

```
PAYPAL_CLIENT_ID = <paste_your_client_id_here>
PAYPAL_CLIENT_SECRET = <paste_your_secret_here>
PAYPAL_BASE_URL = https://api-m.sandbox.paypal.com
```

### Step 3: Deploy

```bash
git push
```

That's it! Railway will auto-deploy.

### Step 4: Test

1. Go to https://bestpdfconverter.online
2. Login
3. Click "Subscribe to Premium"
4. You'll be redirected to PayPal sandbox
5. Use a test account from PayPal dashboard
6. Complete payment
7. You'll be redirected back with Premium activated!

## Test Cards (Sandbox)

PayPal sandbox accepts these test cards:

- **Visa**: 4032039683435142
- **Mastercard**: 5425233430109903
- **Expiry**: Any future date
- **CVV**: 123

Or use PayPal test accounts from the Sandbox > Accounts section.

## Files Changed

| File | What Changed |
|------|--------------|
| [paypal_service.py](paypal_service.py) | New PayPal API integration |
| [payment.py](payment.py) | New payment routes for PayPal |
| [config.py](config.py) | Added PayPal configuration |
| [.env.example](.env.example) | PayPal environment variables |

## Environment Variables

Only 3 variables needed:

```bash
PAYPAL_CLIENT_ID=<your_sandbox_client_id>
PAYPAL_CLIENT_SECRET=<your_sandbox_secret>
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

## Going Live (Later)

When ready for production:

1. Switch to "Live" tab in PayPal dashboard
2. Get Live credentials
3. Update Railway variables:
   ```
   PAYPAL_BASE_URL = https://api-m.paypal.com
   ```
4. Use Live Client ID and Secret

## Need Help?

See [PAYPAL_SETUP_GUIDE.md](PAYPAL_SETUP_GUIDE.md) for detailed instructions.

---

**Summary:**
- Get credentials from PayPal (30 seconds)
- Update 3 Railway variables (30 seconds)
- Push code (already done)
- Test (2 minutes)

**Total time: ~5 minutes!** 🎉
