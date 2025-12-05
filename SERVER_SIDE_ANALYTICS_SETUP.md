# Server-Side Google Analytics 4 Setup Guide

## Overview
This implementation uses **server-side tracking** with Google Analytics 4 Measurement Protocol API, which completely bypasses ad blockers since all tracking happens on your server, not in the browser.

## What Was Implemented

### 1. New Files Created:
- `analytics.py` - Core server-side analytics tracking module
- `analytics_middleware.py` - Flask middleware for automatic page view tracking

### 2. Modified Files:
- `config.py` - Added GA4 configuration settings
- `app.py` - Integrated analytics initialization and middleware

## Setup Instructions

### Step 1: Get Your GA4 API Secret

1. Go to [Google Analytics](https://analytics.google.com)
2. Select your property (G-JT9QHQ41H9)
3. Click **Admin** (gear icon at bottom left)
4. Under **Data Streams**, click on your web stream
5. Scroll down to **Measurement Protocol API secrets**
6. Click **Create** to generate a new API secret
7. Give it a name like "Server-Side Tracking"
8. **Copy the secret value** - you'll need this!

### Step 2: Set Environment Variable

#### For Local Development:
Create or update `.env` file in your project root:
```bash
GA4_MEASUREMENT_ID=G-JT9QHQ41H9
GA4_API_SECRET=your_api_secret_here
```

#### For Railway Production:
1. Go to your Railway dashboard
2. Select your project
3. Go to **Variables** tab
4. Add new variable:
   - Name: `GA4_API_SECRET`
   - Value: (paste your API secret)
5. Click **Add**
6. Railway will automatically redeploy

### Step 3: Install Required Package

The server-side tracking requires the `requests` library:

```bash
pip install requests
```

Add to `requirements.txt`:
```
requests==2.31.0
```

### Step 4: Deploy

After setting the environment variable, deploy your changes:

```bash
git add .
git commit -m "Add server-side Google Analytics tracking"
git push
```

## How It Works

### Automatic Page View Tracking
Every time a user visits a page, the middleware automatically:
1. Captures the page path and title
2. Generates or retrieves a client ID (stored in session)
3. Sends tracking data directly from your server to Google Analytics
4. Works even if user has ad blockers enabled!

### Custom Event Tracking
You can track custom events in your code:

```python
from analytics import analytics

# Track a custom event
if analytics:
    analytics.track_event(
        'pdf_conversion',
        event_params={
            'operation_type': 'split',
            'file_size_mb': 5.2,
            'pages_count': 10
        },
        user_id=current_user.id if current_user.is_authenticated else None
    )
```

### Track Conversions
```python
# Track a purchase/subscription
if analytics:
    analytics.track_conversion(
        'purchase',
        value=9.99,
        currency='USD',
        user_id=current_user.id
    )
```

## Testing

### Test in Debug Mode:
```python
# In your route
if analytics:
    analytics.track_pageview('/test', 'Test Page', debug=True)
```

This will log the GA4 response to help you verify the data is being sent correctly.

### Check Real-Time Reports:
1. Go to Google Analytics
2. Navigate to **Reports** → **Realtime**
3. Visit your website
4. You should see the visit appear in real-time (even with ad blockers!)

## Advantages of Server-Side Tracking

✅ **Bypasses Ad Blockers** - Tracking happens on your server, not in browser  
✅ **More Accurate Data** - No client-side blocking means better data quality  
✅ **Better Privacy Control** - You control what data is sent  
✅ **Works with Strict CSP** - No need to whitelist Google domains  
✅ **Faster Page Load** - No external scripts to load  

## Monitoring

Check your application logs for analytics status:
- "Server-side analytics initialized" - Analytics is working
- "GA4_MEASUREMENT_ID or GA4_API_SECRET not set" - Need to set environment variables

## Troubleshooting

### No data appearing in GA4?
1. Verify `GA4_API_SECRET` is set in environment variables
2. Check application logs for errors
3. Use `debug=True` to see API responses
4. Wait 24-48 hours for data to appear in standard reports (Real-time should show immediately)

### Still seeing blocked requests in browser?
That's normal! The old client-side tracking code is still in your HTML templates. The server-side tracking works independently and will send data even when the browser code is blocked.

## Optional: Remove Client-Side Tracking

If you want to completely remove the client-side Google Analytics code from your HTML templates (since server-side tracking handles everything), you can remove these lines from all template files:

```html
<!-- Remove this block -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JT9QHQ41H9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-JT9QHQ41H9');
</script>
```

However, keeping both provides redundancy - users without ad blockers will be tracked client-side (more detailed), while users with ad blockers will still be tracked server-side.

## Support

For issues or questions, check the Google Analytics 4 Measurement Protocol documentation:
https://developers.google.com/analytics/devguides/collection/protocol/ga4
