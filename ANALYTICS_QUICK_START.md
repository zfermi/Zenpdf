# Quick Start: Server-Side Analytics

## 🚀 Get Your API Secret (5 minutes)

1. Go to https://analytics.google.com
2. Admin → Data Streams → Your Stream (bestpdfconverter.online)
3. Scroll to "Measurement Protocol API secrets"
4. Click "Create" → Name it "Server Tracking" → Copy the secret

## 🔧 Set Environment Variable

### Railway (Production):
```
Variable Name: GA4_API_SECRET
Variable Value: <paste your secret here>
```

### Local (.env file):
```
GA4_API_SECRET=your_secret_here
```

## ✅ That's It!

After setting the variable and redeploying, your analytics will work even with ad blockers!

Check real-time reports at: https://analytics.google.com → Reports → Realtime

---

For detailed documentation, see `SERVER_SIDE_ANALYTICS_SETUP.md`
