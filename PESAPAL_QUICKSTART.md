# Pesapal Integration - Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Get Pesapal Credentials

1. Go to https://developer.pesapal.com/
2. Sign up/Login to your merchant account
3. Get your credentials:
   - Consumer Key
   - Consumer Secret

### Step 2: Update .env File

Copy your actual credentials into `.env`:

```bash
# Pesapal Configuration
PESAPAL_CONSUMER_KEY=your_actual_consumer_key_here
PESAPAL_CONSUMER_SECRET=your_actual_consumer_secret_here

# For Testing (use sandbox)
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3

# Callback URLs (update with your domain)
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

### Step 3: Whitelist Your Domain in Pesapal

1. Login to Pesapal Developer Portal
2. Go to Settings → Domains
3. Add: `bestpdfconverter.online`
4. Save

### Step 4: Test the Integration

```bash
# Run your app
python app.py
```

1. Navigate to `/pricing`
2. Login to your account
3. Click "Upgrade to Premium"
4. You'll be redirected to Pesapal
5. Use test card: `4111111111111111`

### Step 5: Go Live

When ready for production:

1. Update `.env`:
   ```bash
   PESAPAL_BASE_URL=https://pay.pesapal.com/v3
   ```

2. Get production credentials from Pesapal

3. Deploy to your server

## That's It!

For detailed documentation, see [PESAPAL_INTEGRATION.md](PESAPAL_INTEGRATION.md)

## Quick Test Checklist

- ✅ Pesapal credentials configured
- ✅ Domain whitelisted in Pesapal
- ✅ SSL certificate installed
- ✅ Test payment completes successfully
- ✅ User subscription updates correctly
- ✅ IPN notifications received

## Support

- Issues? Check logs: `tail -f logs/zenpdf.log`
- Pesapal Support: support@pesapal.com
- API Docs: https://developer.pesapal.com/
