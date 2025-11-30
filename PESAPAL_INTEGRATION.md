# Pesapal Payment Integration Guide

This guide will help you integrate Pesapal card payment gateway into your ZenPDF application for the domain **bestpdfconverter.online**.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setting Up Pesapal Account](#setting-up-pesapal-account)
3. [Configuration](#configuration)
4. [Testing the Integration](#testing-the-integration)
5. [Going Live](#going-live)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Active Pesapal merchant account
- Domain: **bestpdfconverter.online**
- SSL certificate installed on your domain (required for production)
- Python 3.7+ with Flask

---

## Setting Up Pesapal Account

### 1. Create a Pesapal Merchant Account

1. Visit [Pesapal Merchant Portal](https://www.pesapal.com/)
2. Sign up for a merchant account
3. Complete the KYC verification process
4. Wait for account approval

### 2. Get API Credentials

1. Log in to the [Pesapal Developer Portal](https://developer.pesapal.com/)
2. Navigate to **API Credentials** or **Settings**
3. Copy your:
   - **Consumer Key**
   - **Consumer Secret**

### 3. Configure Sandbox for Testing

Initially, you'll use the Pesapal sandbox environment:
- Sandbox URL: `https://cybqa.pesapal.com/pesapalv3`

---

## Configuration

### 1. Update Environment Variables

Edit your `.env` file with the following Pesapal configuration:

```bash
# Pesapal Payment Integration
PESAPAL_CONSUMER_KEY=your_actual_consumer_key_here
PESAPAL_CONSUMER_SECRET=your_actual_consumer_secret_here

# For Testing (Sandbox)
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3

# For Production
# PESAPAL_BASE_URL=https://pay.pesapal.com/v3

# Callback URLs (update with your domain)
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

### 2. Update Talisman CSP Headers

Since Pesapal payment pages need to be embedded, update your CSP policy in [config.py](config.py:77):

```python
TALISMAN_CONTENT_SECURITY_POLICY = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", "https://pagead2.googlesyndication.com", "https://www.pesapal.com", "https://pay.pesapal.com", "https://cybqa.pesapal.com"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'font-src': ["'self'", "data:"],
    'frame-src': ["'self'", "https://www.pesapal.com", "https://pay.pesapal.com", "https://cybqa.pesapal.com"],
}
```

### 3. Whitelist Your Domain in Pesapal

1. Log in to Pesapal Developer Portal
2. Navigate to **Settings** > **Domains**
3. Add your domain: `bestpdfconverter.online`
4. Save the configuration

---

## Testing the Integration

### 1. Start Your Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 2. Test Payment Flow

1. Navigate to `https://bestpdfconverter.online/pricing`
2. Click "Upgrade to Premium" (you must be logged in)
3. You'll be redirected to Pesapal sandbox payment page
4. Use test card credentials:
   - **Card Number**: `4111111111111111` (Visa test card)
   - **Expiry**: Any future date
   - **CVV**: Any 3 digits
   - **Name**: Test User

### 3. Verify Callback Handling

After payment:
- Success: Redirects to `/payment/callback?OrderTrackingId=...`
- The user's subscription should be updated to Premium
- Check your application logs for payment confirmation

### 4. Verify IPN (Instant Payment Notification)

Pesapal will send payment notifications to:
- URL: `https://bestpdfconverter.online/payment/ipn`
- This runs in the background and updates subscription status

---

## Going Live

### 1. Switch to Production Environment

Update `.env`:

```bash
# Change to production URL
PESAPAL_BASE_URL=https://pay.pesapal.com/v3

# Get production credentials from Pesapal
PESAPAL_CONSUMER_KEY=your_production_consumer_key
PESAPAL_CONSUMER_SECRET=your_production_consumer_secret
```

### 2. Update IPN Registration

When you switch to production, the IPN will be automatically registered on the first payment attempt. You can also manually register it:

```python
from pesapal_service import create_pesapal_service
from app import app

with app.app_context():
    pesapal = create_pesapal_service(app)
    ipn_id = pesapal.register_ipn()
    print(f"IPN registered with ID: {ipn_id}")
```

### 3. SSL Certificate

Ensure your domain `bestpdfconverter.online` has a valid SSL certificate. Pesapal requires HTTPS for all callbacks.

### 4. Verify Production Setup

1. Make a test purchase with a real card (small amount)
2. Verify the payment shows in your Pesapal dashboard
3. Confirm user subscription is updated correctly
4. Check IPN logs to ensure notifications are received

---

## Payment Flow

### User Journey

1. **User clicks "Upgrade to Premium"** on pricing page
   - Route: `/payment/subscribe/premium`
   - Must be logged in

2. **System creates payment order**
   - Generates unique order ID: `ZENPDF-{user_id}-{random_token}`
   - Amount: $9.99 USD
   - Description: "ZenPDF Premium Subscription - Monthly"

3. **User is redirected to Pesapal**
   - Pesapal displays payment form
   - User enters card details
   - User completes payment

4. **Pesapal redirects back to your site**
   - Route: `/payment/callback?OrderTrackingId=...`
   - System verifies payment status
   - Updates user subscription if successful

5. **Pesapal sends IPN notification**
   - Route: `/payment/ipn?OrderTrackingId=...`
   - Redundant verification (in case callback fails)
   - Updates subscription in background

### Payment Status Codes

- `1` - **Completed**: Payment successful
- `2` - **Failed**: Payment failed
- `3` - **Invalid**: Invalid payment/request

---

## API Endpoints

### Implemented Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/payment/subscribe/premium` | GET | Initiate premium subscription | Yes |
| `/payment/callback` | GET | Payment callback handler | Yes |
| `/payment/ipn` | GET/POST | IPN notification handler | No |
| `/payment/status/<tracking_id>` | GET | Check payment status | Yes |

---

## Troubleshooting

### Issue: Payment callback not working

**Solution:**
- Verify your domain is whitelisted in Pesapal
- Check that SSL is properly configured
- Ensure callback URL is correct in `.env`
- Check application logs for errors

### Issue: IPN not received

**Solution:**
- Verify IPN URL is registered in Pesapal
- Check that the URL is publicly accessible
- Ensure your server can receive POST/GET requests
- Check firewall settings

### Issue: "Failed to authenticate with Pesapal"

**Solution:**
- Verify Consumer Key and Consumer Secret are correct
- Check if you're using sandbox/production credentials correctly
- Ensure base URL matches your environment

### Issue: Payment completes but subscription not updated

**Solution:**
- Check application logs for errors
- Verify database is writable
- Test IPN endpoint manually
- Check merchant reference format

### Issue: CORS errors

**Solution:**
- Update Talisman CSP policy to include Pesapal domains
- Add `frame-src` and `script-src` for Pesapal URLs

---

## Security Considerations

1. **Never expose your Consumer Secret** in client-side code
2. **Always use HTTPS** for production
3. **Verify payment status** server-side (don't trust client)
4. **Log all transactions** for audit trail
5. **Implement rate limiting** on payment endpoints
6. **Validate merchant reference** format in IPN handler

---

## Monitoring and Logs

### Check Payment Logs

```bash
tail -f logs/zenpdf.log | grep -i payment
```

### Monitor IPN Notifications

```bash
tail -f logs/zenpdf.log | grep -i ipn
```

### Check Pesapal Dashboard

- Log in to Pesapal merchant portal
- View transaction history
- Check for failed payments
- Download reports

---

## Support

- **Pesapal Support**: support@pesapal.com
- **Pesapal Developer Docs**: https://developer.pesapal.com/
- **ZenPDF Issues**: Check application logs in `logs/zenpdf.log`

---

## Next Steps

1. ✅ Set up Pesapal merchant account
2. ✅ Get API credentials
3. ✅ Configure environment variables
4. ✅ Test in sandbox environment
5. ⬜ Switch to production
6. ⬜ Monitor first real transactions
7. ⬜ Set up automated reconciliation

---

## Additional Features to Implement (Optional)

- **Subscription Management**: Add ability to cancel/renew subscriptions
- **Payment History**: Show transaction history in user dashboard
- **Webhooks for Failed Payments**: Handle failed payments gracefully
- **Currency Support**: Support multiple currencies (KES, USD, etc.)
- **Refund Processing**: Implement refund functionality
- **Promo Codes**: Add discount/promo code support

---

## Version History

- **v1.0** - Initial Pesapal integration with card payment support
- Domain: bestpdfconverter.online
- Date: 2024
