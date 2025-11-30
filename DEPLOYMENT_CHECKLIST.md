# Pesapal Integration - Deployment Checklist

## Pre-Deployment Checklist

### 1. Pesapal Account Setup
- [ ] Created Pesapal merchant account
- [ ] Completed KYC verification
- [ ] Account approved and active
- [ ] Obtained Consumer Key
- [ ] Obtained Consumer Secret
- [ ] Reviewed Pesapal fees and terms

### 2. Domain Configuration
- [ ] Domain `bestpdfconverter.online` is active
- [ ] SSL certificate installed and valid
- [ ] DNS properly configured
- [ ] Domain whitelisted in Pesapal portal

### 3. Environment Configuration
- [ ] Updated `.env` with Pesapal credentials
- [ ] Set correct PESAPAL_BASE_URL (sandbox or production)
- [ ] Configured PESAPAL_IPN_URL
- [ ] Configured PESAPAL_CALLBACK_URL
- [ ] Verified all environment variables are set

### 4. Code Deployment
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] No syntax errors: `python -m py_compile *.py`
- [ ] Payment blueprint registered in app.py
- [ ] CSP headers updated in config.py
- [ ] Database migrations applied (if any)

### 5. Testing (Sandbox)
- [ ] Can access `/pricing` page
- [ ] "Upgrade to Premium" button works
- [ ] Redirects to Pesapal sandbox
- [ ] Test payment completes successfully
- [ ] Callback URL receives response
- [ ] User subscription updates to Premium
- [ ] IPN endpoint receives notification
- [ ] Payment logs appear in logs/zenpdf.log

### 6. Security Verification
- [ ] HTTPS enabled on all endpoints
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Talisman security headers active
- [ ] No credentials in client-side code
- [ ] Logs don't expose sensitive data

## Sandbox Testing

### Test Payment Flow
```bash
# Start application
python app.py

# Test URLs
https://bestpdfconverter.online/pricing
https://bestpdfconverter.online/payment/subscribe/premium
https://bestpdfconverter.online/payment/callback
https://bestpdfconverter.online/payment/ipn
```

### Test Cards
- **Visa**: 4111111111111111
- **Mastercard**: 5500000000000004
- **Expiry**: Any future date (e.g., 12/25)
- **CVV**: Any 3 digits (e.g., 123)
- **Name**: Test User

### Verify Success Criteria
- [ ] Payment initiates without errors
- [ ] Pesapal payment page loads
- [ ] Test payment processes successfully
- [ ] Redirected to callback URL
- [ ] User sees success message
- [ ] Dashboard shows "Premium" status
- [ ] Subscription dates are correct
- [ ] IPN notification logged

## Production Deployment

### 1. Switch to Production Mode

Update `.env`:
```bash
# Change from sandbox to production
PESAPAL_BASE_URL=https://pay.pesapal.com/v3

# Use production credentials
PESAPAL_CONSUMER_KEY=prod_consumer_key_here
PESAPAL_CONSUMER_SECRET=prod_consumer_secret_here
```

### 2. Verify Production Settings
- [ ] Production Pesapal credentials configured
- [ ] Production base URL set
- [ ] Callback URLs use HTTPS
- [ ] IPN URL is publicly accessible
- [ ] Firewall allows Pesapal IPs

### 3. Test with Real Payment
- [ ] Make small test purchase ($0.01 or minimum)
- [ ] Verify payment in Pesapal dashboard
- [ ] Confirm subscription updated correctly
- [ ] Check IPN received and processed
- [ ] Verify refund process (if applicable)

### 4. Monitor First Transactions
```bash
# Watch logs in real-time
tail -f logs/zenpdf.log | grep -i payment

# Check for errors
tail -f logs/zenpdf.log | grep -i error

# Monitor IPN
tail -f logs/zenpdf.log | grep -i ipn
```

## Post-Deployment Monitoring

### Daily Checks (First Week)
- [ ] Check Pesapal dashboard for transactions
- [ ] Review application logs for errors
- [ ] Verify all payments update subscriptions
- [ ] Monitor failed payment attempts
- [ ] Check IPN delivery rate

### Weekly Checks
- [ ] Reconcile Pesapal transactions with database
- [ ] Review payment failure rate
- [ ] Check subscription renewal process
- [ ] Analyze payment completion time
- [ ] Review customer support tickets

### Monthly Tasks
- [ ] Download Pesapal transaction reports
- [ ] Audit subscription status accuracy
- [ ] Review and optimize payment flow
- [ ] Update documentation if needed
- [ ] Plan improvements based on data

## Rollback Plan

If issues occur, rollback steps:

1. **Disable Payment Feature**
   ```python
   # Comment out in app.py
   # app.register_blueprint(payment_bp, url_prefix='/payment')
   ```

2. **Revert to Placeholder**
   - Restore old pricing.html with "Coming Soon" message

3. **Investigate**
   - Check logs: `tail -f logs/zenpdf.log`
   - Review Pesapal dashboard
   - Contact Pesapal support if needed

4. **Fix and Redeploy**
   - Fix identified issues
   - Test in sandbox again
   - Redeploy to production

## Emergency Contacts

- **Pesapal Support**: support@pesapal.com
- **Pesapal Phone**: Check your merchant portal
- **Technical Issues**: Check logs first, then contact support
- **Payment Disputes**: Handle via Pesapal merchant dashboard

## Success Metrics

Track these KPIs after deployment:

- **Payment Success Rate**: Target >95%
- **Callback Response Time**: Target <5 seconds
- **IPN Delivery Rate**: Target >99%
- **User Conversion Rate**: Monitor and optimize
- **Failed Payment Rate**: Target <5%
- **Support Tickets**: Monitor payment-related issues

## Common Issues & Solutions

### Issue: Callback URL not working
**Solutions**:
1. Verify HTTPS is enabled
2. Check firewall allows Pesapal IPs
3. Verify domain is whitelisted
4. Check application logs for errors

### Issue: IPN not received
**Solutions**:
1. Verify IPN URL is publicly accessible
2. Check IPN registration in Pesapal
3. Test IPN endpoint manually
4. Review firewall rules

### Issue: Payment completes but subscription not updated
**Solutions**:
1. Check database connection
2. Review application logs
3. Verify merchant reference parsing
4. Test IPN endpoint

## Documentation

Keep these files updated:
- [PESAPAL_INTEGRATION.md](PESAPAL_INTEGRATION.md) - Full guide
- [PESAPAL_QUICKSTART.md](PESAPAL_QUICKSTART.md) - Quick start
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Overview
- This checklist - Deployment steps

## Final Pre-Launch Checklist

- [ ] All tests pass in sandbox
- [ ] Production credentials configured
- [ ] Domain SSL valid
- [ ] Monitoring in place
- [ ] Logs configured
- [ ] Backup plan ready
- [ ] Support contacts saved
- [ ] Documentation complete

## Launch!

When all items are checked:

```bash
# Deploy to production
git add .
git commit -m "Add Pesapal payment integration"
git push origin main

# Restart application
# (depends on your hosting - Railway, Heroku, etc.)
```

## Post-Launch

- [ ] Announce payment feature to users
- [ ] Monitor first transactions closely
- [ ] Respond quickly to issues
- [ ] Gather user feedback
- [ ] Plan improvements

---

**Deployment Status**: ⬜ Ready to Deploy

Once all checkboxes are marked, you're ready to go live! 🚀
