# PayPal Live Credentials Setup

## ✅ You Have Live Credentials - Here's How to Use Them

Since you have **live PayPal credentials**, you can accept real payments immediately!

## Important: Live vs Sandbox

| Environment | Purpose | Base URL | Transactions |
|-------------|---------|----------|--------------|
| **Sandbox** | Testing | `https://api-m.sandbox.paypal.com` | Fake money |
| **Live** | Production | `https://api-m.paypal.com` | Real money |

## Option 1: Start with Sandbox (Recommended)

Even though you have live credentials, it's best to **test with sandbox first**:

### Why Test First?
- ✅ Test the entire payment flow with no risk
- ✅ Make sure subscription activation works
- ✅ Verify all routes work correctly
- ✅ Check logging and error handling

### Get Sandbox Credentials (30 seconds)
1. Go to https://developer.paypal.com/dashboard
2. Make sure you're on **"Sandbox"** tab
3. Click on "Default Application"
4. Copy Client ID and Secret

### Configure Sandbox in Railway
```
PAYPAL_CLIENT_ID = <sandbox_client_id>
PAYPAL_CLIENT_SECRET = <sandbox_secret>
PAYPAL_BASE_URL = https://api-m.sandbox.paypal.com
```

### Test Payment Flow
1. Deploy to Railway: `git push`
2. Go to your website
3. Try to subscribe
4. Use PayPal test account or test card
5. Verify subscription activates

### Once Testing Passes
Switch to live credentials (see Option 2 below)

---

## Option 2: Use Live Credentials (Production)

### ⚠️ Important Checklist Before Going Live

Make sure:
- [ ] You've tested with sandbox and everything works
- [ ] Your PayPal business account is verified
- [ ] Bank account is connected to your PayPal account
- [ ] You understand PayPal fees will be deducted from payments
- [ ] You have a refund policy in place
- [ ] Your website terms clearly state subscription terms

### Configure Live Credentials in Railway

1. **Get Your Live Credentials**
   - Go to https://developer.paypal.com/dashboard
   - Switch to **"Live"** tab (top right)
   - Click on your application (or create new one)
   - Copy **Live Client ID** and **Live Secret**

2. **Update Railway Environment Variables**

   Go to Railway → Your Project → Variables and set:

   ```
   PAYPAL_CLIENT_ID = <your_live_client_id>
   PAYPAL_CLIENT_SECRET = <your_live_secret>
   PAYPAL_BASE_URL = https://api-m.paypal.com
   ```

   ⚠️ **CRITICAL**: Notice the base URL is different!
   - Sandbox: `https://api-m.sandbox.paypal.com`
   - Live: `https://api-m.paypal.com` (no "sandbox")

3. **Deploy**
   ```bash
   git push
   ```

4. **Test with Small Amount First**
   - Make a real payment yourself
   - Use a small test amount (or actual $9.99)
   - Verify funds appear in your PayPal account
   - Verify subscription activates on your site
   - Test refund process if needed

---

## Quick Setup Script

If you want to use **LIVE credentials right away**:

### Railway Variables (Live Production):
```bash
PAYPAL_CLIENT_ID=<paste_your_live_client_id_here>
PAYPAL_CLIENT_SECRET=<paste_your_live_secret_here>
PAYPAL_BASE_URL=https://api-m.paypal.com
```

### Local .env (Live - for testing):
```bash
PAYPAL_CLIENT_ID=your_live_client_id
PAYPAL_CLIENT_SECRET=your_live_secret
PAYPAL_BASE_URL=https://api-m.paypal.com
```

---

## Testing Your Live Integration

### 1. Test Payment Flow
1. Make sure you're logged in to your site
2. Go to Pricing page
3. Click "Subscribe to Premium"
4. You'll be redirected to **real** PayPal checkout
5. Use **real** payment method (your card or PayPal balance)
6. Complete payment
7. Should redirect back and activate subscription

### 2. Verify in PayPal Dashboard
1. Go to https://www.paypal.com
2. Login to your business account
3. Check "Activity" for the transaction
4. Verify amount received (minus PayPal fees)

### 3. Check Railway Logs
```bash
railway logs
```

Look for:
- "Payment initiated for user..."
- "PayPal capture result... Status=COMPLETED"
- "Premium subscription activated for user..."

---

## PayPal Fees (Live)

PayPal charges fees on live transactions:

**Standard Rate**: 2.9% + $0.30 per transaction

For $9.99 subscription:
- Customer pays: $9.99
- PayPal fee: $0.59
- You receive: $9.40

**Note**: Fees may vary by country and business type.

---

## Common Issues & Solutions

### Issue 1: "Failed to authenticate with PayPal"

**Cause**: Wrong credentials or base URL mismatch

**Solution**:
1. Verify you copied the **Live** credentials (not sandbox)
2. Make sure `PAYPAL_BASE_URL = https://api-m.paypal.com`
3. No typos in Client ID or Secret
4. Redeploy after updating variables

### Issue 2: Payment succeeds but subscription not activated

**Check**:
1. Railway logs for errors
2. Database connection
3. User must be logged in when returning from PayPal
4. Check `/success` route for errors

**Fix**: Check logs with `railway logs | grep -i error`

### Issue 3: "Invalid payment response"

**Cause**: User not logged in after redirect

**Solution**: Make sure session cookies are preserved. Check:
- `SESSION_COOKIE_SECURE = True` in config
- HTTPS is enabled
- Cookies not blocked

---

## Monitoring Live Payments

### PayPal Dashboard
- https://www.paypal.com
- Check "Activity" regularly
- Set up email notifications

### Railway Logs
```bash
railway logs --follow
```

Watch for:
- Payment initiations
- Successful captures
- Failed transactions
- Errors

### Database Check
```sql
SELECT id, email, subscription_tier, subscription_end
FROM users
WHERE subscription_tier = 'premium'
ORDER BY subscription_start DESC;
```

---

## Security Notes

### Never Commit Credentials!
- ✅ Use Railway environment variables
- ✅ Keep credentials in Railway dashboard
- ❌ Never put in code or .env file that's committed

### Webhook Security (Optional but Recommended)
For production, verify PayPal webhook signatures:

```python
# In payment.py webhook route
def paypal_webhook():
    # Verify webhook signature
    # See: https://developer.paypal.com/api/rest/webhooks/
```

---

## Going Live Checklist

- [ ] Live credentials obtained from PayPal
- [ ] Railway variables updated with live credentials
- [ ] Base URL set to `https://api-m.paypal.com` (not sandbox)
- [ ] Code deployed: `git push`
- [ ] Test payment completed successfully
- [ ] Funds received in PayPal account
- [ ] Subscription activated on site
- [ ] Refund tested (optional but recommended)
- [ ] Error logging verified
- [ ] Terms of service updated
- [ ] Privacy policy includes payment info

---

## Support

**PayPal Issues**:
- PayPal Help: https://www.paypal.com/businesshelp
- PayPal Developer Support: https://developer.paypal.com/support/

**Technical Issues**:
- Check Railway logs: `railway logs`
- Check [PAYPAL_SETUP_GUIDE.md](PAYPAL_SETUP_GUIDE.md)
- Review error messages in logs

---

## Summary

**With live credentials, you can either:**

1. **Test with Sandbox First** (Recommended)
   - Get sandbox credentials
   - Test entire flow
   - Then switch to live

2. **Go Live Immediately**
   - Use your live credentials
   - Set `PAYPAL_BASE_URL = https://api-m.paypal.com`
   - Deploy and test with real payment
   - Monitor closely

**Recommended**: Start with sandbox, then switch to live once tested!

---

## Quick Commands

```bash
# Deploy to Railway
git push

# Check logs
railway logs

# Check recent logs
railway logs --tail 100

# Follow logs in real-time
railway logs --follow
```

Ready to accept payments! 💰
