# Pesapal Payment Flow Diagram

## Complete Payment Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                                     │
└─────────────────────────────────────────────────────────────────────────┘

    User visits Pricing Page
           │
           │ (clicks "Upgrade to Premium")
           ▼
    /payment/subscribe/premium
           │
           │ 1. Check if user is already premium
           │ 2. Generate unique order ID
           │ 3. Get Pesapal OAuth token
           │ 4. Submit order to Pesapal
           │
           ▼
    Pesapal API Response
           │
           │ Returns: redirect_url, order_tracking_id
           │
           ▼
    Redirect to Pesapal Payment Page
           │
           │ User sees payment form
           │ User enters card details
           │ User clicks "Pay Now"
           │
           ▼
    Pesapal Processes Payment
           │
           ├─────────────┬─────────────┐
           │             │             │
           ▼             ▼             ▼
        Success       Failed      Pending
           │             │             │
           │             │             │
           ▼             ▼             ▼
    Redirect to Callback URL
           │
           │ /payment/callback?OrderTrackingId=xxx&OrderMerchantReference=xxx
           │
           ▼
    Verify Payment Status
           │
           │ 1. Get transaction status from Pesapal
           │ 2. Check payment_status_description
           │ 3. Check status_code
           │
           ├─────────────┬─────────────┬─────────────┐
           │             │             │             │
           ▼             ▼             ▼             ▼
      Completed      Failed       Invalid      Pending
    (code: 1)     (code: 2)    (code: 3)
           │             │             │             │
           │             │             │             │
           ▼             ▼             ▼             ▼
    Update User     Show Error   Show Error   Show Info
    Subscription
           │
           │ subscription_tier = 'premium'
           │ subscription_start = now
           │ subscription_end = now + 30 days
           │
           ▼
    Show Success Message
           │
           ▼
    Redirect to Dashboard
           │
           ▼
    User sees Premium features
```

## Parallel IPN Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    IPN (Background Process)                              │
└─────────────────────────────────────────────────────────────────────────┘

    Pesapal Server
           │
           │ (sends notification in background)
           │
           ▼
    /payment/ipn?OrderTrackingId=xxx&OrderNotificationType=xxx
           │
           │ 1. Extract order tracking ID
           │ 2. Get transaction status
           │ 3. Parse merchant reference
           │ 4. Find user by ID
           │
           ▼
    Verify Payment Status
           │
           ├─────────────────────────┐
           │                         │
           ▼                         ▼
      Completed                 Other Status
           │                         │
           │                         │
           ▼                         ▼
    Update Subscription        Log Status
    (if not already updated)
           │
           │
           ▼
    Return Success Response
           │
           │ {"status": "success", "message": "IPN processed"}
           │
           ▼
    Pesapal marks IPN as delivered
```

## Order ID Format

```
ZENPDF-{user_id}-{random_token}

Example: ZENPDF-123-a1b2c3d4e5f6g7h8

Components:
├── ZENPDF     → Application identifier
├── 123        → User ID (from database)
└── a1b2...    → 16-char random hex token (security)
```

## Payment Status Codes

```
┌──────────────┬─────────────────────┬──────────────────────────┐
│ Status Code  │ Description         │ Action                   │
├──────────────┼─────────────────────┼──────────────────────────┤
│      1       │ Completed           │ Activate subscription    │
│      2       │ Failed              │ Show error, allow retry  │
│      3       │ Invalid             │ Show error, contact us   │
│    Other     │ Pending/Processing  │ Show info, wait for IPN  │
└──────────────┴─────────────────────┴──────────────────────────┘
```

## API Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    OAuth Token Management                                │
└─────────────────────────────────────────────────────────────────────────┘

    First API Call
           │
           ▼
    Check if token exists and valid
           │
           ├─────────────┬─────────────┐
           │             │             │
           ▼             ▼             ▼
      Valid Token   Expired Token   No Token
           │             │             │
           │             │             │
           │             ▼             ▼
           │     Request New Token ────┘
           │             │
           │             │ POST /api/Auth/RequestToken
           │             │ {
           │             │   consumer_key: xxx,
           │             │   consumer_secret: xxx
           │             │ }
           │             │
           │             ▼
           │     Receive Token
           │             │
           │             │ {
           │             │   token: "abc123...",
           │             │   expires_in: 300
           │             │ }
           │             │
           │             ▼
           │     Store Token + Expiry
           │             │
           └─────────────┘
                         │
                         ▼
                  Use Token for API Call
                         │
                         │ Headers: {
                         │   Authorization: "Bearer abc123..."
                         │ }
                         │
                         ▼
                  API Request Success
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Error Scenarios                                  │
└─────────────────────────────────────────────────────────────────────────┘

    Error Occurs
           │
           ├────────┬────────┬────────┬────────┬────────┐
           │        │        │        │        │        │
           ▼        ▼        ▼        ▼        ▼        ▼
      Network   Invalid  Expired  Payment Database  Other
      Error    Credentials Token  Failed   Error
           │        │        │        │        │        │
           │        │        │        │        │        │
           ▼        ▼        ▼        ▼        ▼        ▼
      Retry   Show Error Refresh Show Error Rollback Show Error
      3 times  to User   Token   to User  Transaction to User
           │        │        │        │        │        │
           │        │        │        │        │        │
           ▼        ▼        ▼        ▼        ▼        ▼
      Log      Log      Log      Log      Log      Log
      Error    Error    Error    Error    Error    Error
           │        │        │        │        │        │
           └────────┴────────┴────────┴────────┴────────┘
                                   │
                                   ▼
                          Redirect to Safe Page
                                   │
                                   ▼
                          Show User-Friendly Message
```

## Database Updates

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    User Table Updates                                    │
└─────────────────────────────────────────────────────────────────────────┘

    Payment Successful
           │
           ▼
    ┌─────────────────────────────┐
    │ User Table                  │
    ├─────────────────────────────┤
    │ id: 123                     │
    │ email: user@example.com     │
    │ username: johndoe           │
    ├─────────────────────────────┤
    │ BEFORE:                     │
    │ subscription_tier: 'free'   │
    │ subscription_start: NULL    │
    │ subscription_end: NULL      │
    ├─────────────────────────────┤
    │ AFTER:                      │
    │ subscription_tier: 'premium'│
    │ subscription_start: NOW()   │
    │ subscription_end: NOW()+30d │
    └─────────────────────────────┘
           │
           ▼
    User is now Premium
```

## Sequence Diagram

```
User          App           Pesapal         Database
 │             │               │               │
 │  Click Pay  │               │               │
 ├────────────>│               │               │
 │             │ Get Token     │               │
 │             ├──────────────>│               │
 │             │<──────────────┤               │
 │             │ Submit Order  │               │
 │             ├──────────────>│               │
 │             │<──────────────┤               │
 │<────────────┤ Redirect      │               │
 │             │               │               │
 │  Enter Card Details         │               │
 ├────────────────────────────>│               │
 │             │ Process       │               │
 │             │ Payment       │               │
 │<────────────────────────────┤               │
 │             │               │               │
 │ Redirected  │               │               │
 ├────────────>│               │               │
 │             │ Verify Status │               │
 │             ├──────────────>│               │
 │             │<──────────────┤               │
 │             │         Update Subscription   │
 │             ├──────────────────────────────>│
 │             │<──────────────────────────────┤
 │<────────────┤ Show Success  │               │
 │             │               │               │
 │             │ IPN Notify    │               │
 │             │<──────────────┤               │
 │             │         Verify Update         │
 │             ├──────────────────────────────>│
 │             │         (Already Updated)     │
 │             │<──────────────────────────────┤
 │             ├──────────────>│ ACK           │
 │             │               │               │
```

## File Structure

```
Zenpdf/
├── pesapal_service.py         ← Pesapal API wrapper
├── payment.py                 ← Payment routes
├── app.py                     ← Main app (imports payment_bp)
├── config.py                  ← Pesapal config
├── models.py                  ← User model
├── templates/
│   └── pricing.html          ← Updated with payment button
├── .env                       ← Credentials (not in repo)
├── .env.example              ← Template with Pesapal vars
└── docs/
    ├── PESAPAL_INTEGRATION.md    ← Full guide
    ├── PESAPAL_QUICKSTART.md     ← Quick start
    ├── INTEGRATION_SUMMARY.md    ← Overview
    ├── DEPLOYMENT_CHECKLIST.md   ← Deploy steps
    └── PAYMENT_FLOW.md          ← This file
```

## Timeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Typical Payment Timeline                                    │
└─────────────────────────────────────────────────────────────────────────┘

0s     User clicks "Upgrade to Premium"
       │
0.5s   App generates order and gets token
       │
1s     Redirect to Pesapal
       │
30s    User fills payment form
       │
35s    Pesapal processes payment
       │
36s    Redirect to callback
       │
37s    App verifies status
       │
37.5s  Database updated
       │
38s    User sees success message
       │
40s    IPN received (redundant)
       │
41s    Complete ✓
```

---

**Visual Flow Complete** 🎯

This diagram shows the complete payment integration flow from user click to subscription activation!
