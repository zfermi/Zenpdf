# Pesapal Setup & Troubleshooting Guide

## Current Status

❌ **Authentication Failed**: Your Pesapal credentials are being rejected by the API.

**Error**: `invalid_consumer_key_or_secret_provided`

This means the credentials need to be properly configured in the Pesapal portal.

---

## Step-by-Step Setup Guide

### 1. Verify Your Pesapal Account

1. **Login to Pesapal Developer Portal**
   - Go to: https://developer.pesapal.com/
   - Or: https://www.pesapal.com/merchant/

2. **Check Account Status**
   - Ensure your account is verified
   - Complete KYC if not done
   - Wait for account approval (can take 24-48 hours)

### 2. Get Correct API Credentials

The credentials you provided might be for a different purpose. Here's how to get the right ones:

#### Option A: Sandbox/Demo Credentials

1. Login to https://developer.pesapal.com/
2. Navigate to **API 3.0** section
3. Find **Demo/Sandbox** credentials
4. Copy:
   - Consumer Key
   - Consumer Secret

#### Option B: Production Credentials

1. Login to https://developer.pesapal.com/
2. Navigate to **API 3.0** section
3. Find **Live/Production** credentials
4. Copy:
   - Consumer Key
   - Consumer Secret

### 3. Enable API Access

Some Pesapal accounts require explicit API access enablement:

1. Login to merchant portal
2. Go to **Settings** → **API Access**
3. Enable **API 3.0**
4. Save changes

### 4. Check App Registration

You might need to register your application:

1. In Pesapal portal, go to **Apps** or **Applications**
2. Click **Register New App**
3. Enter details:
   - **App Name**: ZenPDF
   - **App URL**: https://bestpdfconverter.online
   - **Callback URL**: https://bestpdfconverter.online/payment/callback
   - **IPN URL**: https://bestpdfconverter.online/payment/ipn
4. Save and get credentials for this app

---

## Common Issues & Solutions

### Issue 1: Invalid Credentials Error

**Symptoms**: `invalid_consumer_key_or_secret_provided`

**Solutions**:

1. **Double-check credentials**
   - Make sure no extra spaces
   - Check for hidden characters
   - Verify you copied the complete key/secret

2. **Verify account status**
   - Account must be verified
   - KYC must be completed
   - Account must be active

3. **Check API version**
   - Make sure you're using API 3.0 credentials
   - Not API 2.0 or older versions

4. **Environment mismatch**
   - Sandbox credentials only work with sandbox URL
   - Production credentials only work with production URL

### Issue 2: Account Not Verified

**Solution**:
1. Complete KYC verification
2. Submit required documents
3. Wait for Pesapal approval email
4. Credentials won't work until verified

### Issue 3: API Access Not Enabled

**Solution**:
1. Contact Pesapal support: support@pesapal.com
2. Request API 3.0 access
3. Provide business details
4. Wait for confirmation

### Issue 4: Wrong Credential Type

**Check**:
- Are these OAuth 1.0 credentials? (We need OAuth 2.0 for API v3)
- Are these for a different Pesapal product?
- Are these merchant credentials vs API credentials?

---

## Testing Your Credentials

Once you have the correct credentials, test them:

```bash
# Update .env file with new credentials
# Then run:
python test_both_urls.py
```

You should see:
```
✓ SUCCESS! Valid credentials for SANDBOX (or PRODUCTION)
```

---

## Alternative: Use Demo/Test Credentials

If you're just testing, Pesapal might provide demo credentials:

1. Check Pesapal documentation for demo credentials
2. These are usually public test credentials
3. Contact support to request test access

---

## Contact Pesapal Support

If issues persist:

**Email**: support@pesapal.com
**Phone**: Check your merchant portal
**Portal**: https://developer.pesapal.com/support

**What to ask**:
> "I need API 3.0 credentials for my merchant account to integrate card payments.
> My business is ZenPDF (bestpdfconverter.online). Please provide:
> - Consumer Key
> - Consumer Secret
> - Confirmation that my account has API 3.0 access enabled"

---

## Expected Credential Format

**Consumer Key**:
- Usually starts with uppercase letters
- Length: ~32 characters
- Example: `qkio1BGGYdGVWYvTg36RruPEdqFnNpDt`

**Consumer Secret**:
- Often ends with `=` (base64 encoded)
- Length: varies
- Example: `FHjR99jfZ43JdQ/XGGh+ys4t/as=`

Your credentials look correct in format, so the issue is likely:
- Account not verified
- API access not enabled
- Wrong environment (sandbox vs production)
- App not registered

---

## Temporary Workaround

While waiting for Pesapal credentials to work, you can:

1. **Test the UI/UX flow** without real payment
2. **Manually upgrade users** via admin panel
3. **Use alternative payment** methods temporarily

To manually upgrade a user:
```bash
# Login to your app
# Go to: https://bestpdfconverter.online/admin
# Find the user
# Change subscription_tier to 'premium'
```

---

## Once Credentials Work

When you get valid credentials:

### 1. Update .env
```bash
PESAPAL_CONSUMER_KEY=your_working_key
PESAPAL_CONSUMER_SECRET=your_working_secret
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3  # or production URL
```

### 2. Test Authentication
```bash
python test_both_urls.py
```

### 3. Test Payment Flow
```bash
python app.py
# Visit https://bestpdfconverter.online/pricing
# Click "Upgrade to Premium"
# Complete test payment
```

### 4. Verify IPN
```bash
# Check logs after payment
tail -f logs/zenpdf.log | grep -i payment
```

---

## Current Integration Status

✅ **Code Integration**: Complete and ready
✅ **Payment Routes**: Implemented
✅ **Error Handling**: In place
✅ **Logging**: Configured
❌ **API Credentials**: Need valid credentials
⬜ **Testing**: Pending valid credentials
⬜ **Production**: Pending testing

---

## Next Steps for You

1. ✅ **Verify Pesapal Account**
   - Login to portal
   - Check verification status
   - Complete KYC if needed

2. ✅ **Get Correct Credentials**
   - API 3.0 credentials
   - Sandbox OR production
   - Copy exactly as shown

3. ✅ **Enable API Access**
   - Settings → API
   - Enable API 3.0
   - Save changes

4. ✅ **Test Credentials**
   ```bash
   python test_both_urls.py
   ```

5. ✅ **Update .env**
   - Replace credentials
   - Use correct base URL
   - Restart app

6. ✅ **Test Payment**
   - Login to app
   - Go to pricing
   - Click upgrade
   - Use test card

---

## Support Resources

- **Pesapal Docs**: https://developer.pesapal.com/
- **API Reference**: https://developer.pesapal.com/api-3.0
- **Support Email**: support@pesapal.com
- **Integration Guide**: See PESAPAL_INTEGRATION.md

---

**The integration is 100% complete on our end. We're just waiting for valid Pesapal credentials to test!** 🚀
