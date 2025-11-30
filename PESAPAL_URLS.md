# Pesapal Integration - Important URLs & Endpoints

## Your Application URLs

### Production URLs (bestpdfconverter.online)

| Purpose | URL | Description |
|---------|-----|-------------|
| **Payment Callback** | `https://bestpdfconverter.online/payment/callback` | Where users return after payment |
| **IPN Listener** | `https://bestpdfconverter.online/payment/ipn` | Instant Payment Notification webhook |
| **Subscribe Page** | `https://bestpdfconverter.online/payment/subscribe/premium` | Initiate payment |
| **Pricing Page** | `https://bestpdfconverter.online/pricing` | View plans |
| **Dashboard** | `https://bestpdfconverter.online/dashboard` | User dashboard |
| **Admin Panel** | `https://bestpdfconverter.online/admin` | Admin panel |

---

## Pesapal Portal URLs

### Developer Portal
- **Main Portal**: https://developer.pesapal.com/
- **Login**: https://developer.pesapal.com/login
- **API Documentation**: https://developer.pesapal.com/api-3.0
- **Support**: https://developer.pesapal.com/support

### Merchant Portal
- **Dashboard**: https://www.pesapal.com/merchant/
- **Transactions**: https://www.pesapal.com/merchant/transactions
- **Settings**: https://www.pesapal.com/merchant/settings

---

## Pesapal API Endpoints

### Sandbox (Testing)
- **Base URL**: `https://cybqa.pesapal.com/pesapalv3`
- **Auth**: `https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken`
- **Submit Order**: `https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest`
- **Transaction Status**: `https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus`
- **Register IPN**: `https://cybqa.pesapal.com/pesapalv3/api/URLSetup/RegisterIPN`
- **Get IPN List**: `https://cybqa.pesapal.com/pesapalv3/api/URLSetup/GetIpnList`

### Production (Live)
- **Base URL**: `https://pay.pesapal.com/v3`
- **Auth**: `https://pay.pesapal.com/v3/api/Auth/RequestToken`
- **Submit Order**: `https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest`
- **Transaction Status**: `https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus`
- **Register IPN**: `https://pay.pesapal.com/v3/api/URLSetup/RegisterIPN`
- **Get IPN List**: `https://pay.pesapal.com/v3/api/URLSetup/GetIpnList`

---

## IPN Configuration

### What is IPN?
IPN (Instant Payment Notification) is a webhook that Pesapal calls to notify your server about payment status changes.

### Your IPN URL
```
https://bestpdfconverter.online/payment/ipn
```

### IPN Parameters (GET request)
When Pesapal sends an IPN notification, it will call your URL with these parameters:

```
GET https://bestpdfconverter.online/payment/ipn?OrderTrackingId=xxx&OrderNotificationType=xxx&OrderMerchantReference=xxx
```

**Parameters**:
- `OrderTrackingId`: Unique Pesapal transaction ID
- `OrderNotificationType`: Type of notification (e.g., "COMPLETED")
- `OrderMerchantReference`: Your order ID (format: ZENPDF-{user_id}-{token})

### IPN Response Format
Your server should respond with:
```json
{
    "status": "success",
    "message": "IPN processed"
}
```

### IPN Registration
The IPN will be automatically registered when the first payment is made. You can also register it manually:

```python
from pesapal_service import create_pesapal_service
from app import app

with app.app_context():
    pesapal = create_pesapal_service(app)
    ipn_id = pesapal.register_ipn()
    print(f"IPN registered with ID: {ipn_id}")
```

---

## Callback URL Configuration

### Your Callback URL
```
https://bestpdfconverter.online/payment/callback
```

### Callback Parameters (GET request)
After payment, Pesapal redirects the user to your callback URL with these parameters:

```
GET https://bestpdfconverter.online/payment/callback?OrderTrackingId=xxx&OrderMerchantReference=xxx
```

**Parameters**:
- `OrderTrackingId`: Unique Pesapal transaction ID
- `OrderMerchantReference`: Your order ID

### Callback Flow
1. User completes payment on Pesapal
2. Pesapal redirects to callback URL with parameters
3. Your app fetches transaction status from Pesapal
4. Updates user subscription if payment successful
5. Shows success/failure message to user

---

## Setting Up URLs in Pesapal Portal

### Step 1: Login to Pesapal
1. Go to https://developer.pesapal.com/
2. Login with your credentials

### Step 2: Register Your Application
1. Navigate to **Apps** or **My Apps**
2. Click **Add New App** or **Register App**
3. Fill in details:

| Field | Value |
|-------|-------|
| App Name | ZenPDF |
| App URL | https://bestpdfconverter.online |
| Callback URL | https://bestpdfconverter.online/payment/callback |
| IPN URL | https://bestpdfconverter.online/payment/ipn |

4. Save and get your credentials

### Step 3: Whitelist Domain
1. Go to **Settings** → **Domains**
2. Add domain: `bestpdfconverter.online`
3. Save changes

---

## Testing URLs

### Local Development
If testing locally first:

```bash
# Callback URL
http://localhost:5000/payment/callback

# IPN URL (must be publicly accessible - use ngrok)
https://your-ngrok-url.ngrok.io/payment/ipn
```

**Note**: For IPN testing, you need a public URL. Use ngrok:
```bash
ngrok http 5000
# Use the https URL provided
```

### Production
Always use HTTPS in production:
```bash
# ✓ Correct
https://bestpdfconverter.online/payment/callback
https://bestpdfconverter.online/payment/ipn

# ✗ Wrong
http://bestpdfconverter.online/payment/callback  # No HTTPS
```

---

## Environment Variables

### For .env file:

```bash
# Sandbox (Testing)
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback

# Production (Live)
PESAPAL_BASE_URL=https://pay.pesapal.com/v3
PESAPAL_IPN_URL=https://bestpdfconverter.online/payment/ipn
PESAPAL_CALLBACK_URL=https://bestpdfconverter.online/payment/callback
```

---

## Verification Checklist

Before going live, verify these URLs work:

- [ ] Callback URL is accessible: `curl https://bestpdfconverter.online/payment/callback`
- [ ] IPN URL is accessible: `curl https://bestpdfconverter.online/payment/ipn`
- [ ] SSL certificate is valid
- [ ] Domain is whitelisted in Pesapal
- [ ] Firewall allows Pesapal IPs
- [ ] URLs match exactly in Pesapal portal

---

## Firewall Configuration

If you have a firewall, allow these Pesapal IPs (check with Pesapal support for current IPs):

**Whitelist for IPN**:
- Allow POST/GET requests from Pesapal servers
- Check Pesapal documentation for current IP ranges

---

## Testing IPN Manually

To test if your IPN URL is working:

```bash
# Test GET request
curl "https://bestpdfconverter.online/payment/ipn?OrderTrackingId=test123&OrderNotificationType=COMPLETED&OrderMerchantReference=ZENPDF-1-abc123"

# Expected response
{"status":"success","message":"IPN processed"}
```

---

## Troubleshooting URLs

### Issue: Callback not working

**Check**:
1. Is URL accessible? `curl https://bestpdfconverter.online/payment/callback`
2. Is HTTPS working? Check SSL certificate
3. Is it whitelisted in Pesapal?
4. Check application logs for errors

### Issue: IPN not received

**Check**:
1. Is URL publicly accessible?
2. Is it registered in Pesapal? Run `python test_pesapal.py` to check
3. Is firewall blocking Pesapal?
4. Check logs: `tail -f logs/zenpdf.log | grep -i ipn`

---

## Support & Documentation

- **Pesapal API Docs**: https://developer.pesapal.com/api-3.0
- **Pesapal Support**: support@pesapal.com
- **Your Integration Docs**: See PESAPAL_INTEGRATION.md

---

## Quick Reference Card

**Copy-paste these values when configuring Pesapal:**

```
Domain: bestpdfconverter.online
Callback URL: https://bestpdfconverter.online/payment/callback
IPN URL: https://bestpdfconverter.online/payment/ipn
App Name: ZenPDF
```

---

**All URLs are configured and ready to use!** ✅
