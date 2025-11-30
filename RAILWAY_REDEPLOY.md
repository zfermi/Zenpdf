# How to Force Railway to Redeploy

## Issue: Changes Not Showing on bestpdfconverter.online

The code has been pushed to GitHub, but Railway might not have deployed it yet, or you might be running the app on a different server.

---

## Option 1: Check Where Your App is Running

### Is it Railway?

```bash
curl -I https://bestpdfconverter.online 2>&1 | grep Server
```

**If Railway**: Should show `Server: railway-edge`
**If Other**: Shows `Server: nginx` or something else

If it's NOT Railway, you need to deploy to that server directly.

---

## Option 2: Force Railway to Redeploy

### Step 1: Login to Railway Dashboard

1. Go to: https://railway.app/
2. Login to your account
3. Find your ZenPDF project

### Step 2: Check Deployment Status

1. Click on your service
2. Go to **Deployments** tab
3. Check the latest deployment:
   - ✅ **Success**: Code deployed successfully
   - ⏳ **Building**: Still deploying
   - ❌ **Failed**: Check logs for errors

### Step 3: Trigger New Deployment

**Method A: Empty Commit**

```bash
git commit --allow-empty -m "Trigger Railway redeploy"
git push origin main
```

**Method B: Railway Dashboard**

1. In Railway dashboard
2. Click on your service
3. Click **Settings** tab
4. Scroll to **Build & Deploy**
5. Click **Redeploy** button

**Method C: Clear Cache and Redeploy**

1. Settings → **Clear Build Cache**
2. Then click **Redeploy**

---

## Option 3: If Running on Different Server

### Check if app is running locally

```bash
# Windows
netstat -ano | findstr :5000

# If Flask is running locally, stop it
```

### Deploy to Your Actual Server

If your site is hosted elsewhere (not Railway), you need to:

1. **SSH into your server**
   ```bash
   ssh user@your-server
   ```

2. **Navigate to app directory**
   ```bash
   cd /path/to/zenpdf
   ```

3. **Pull latest code**
   ```bash
   git pull origin main
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Add environment variables**
   - Edit .env file or system environment
   - Add all Pesapal variables

6. **Restart the application**
   ```bash
   # Using systemd
   sudo systemctl restart zenpdf

   # OR using supervisor
   sudo supervisorctl restart zenpdf

   # OR using pm2
   pm2 restart zenpdf

   # OR if using gunicorn directly
   pkill gunicorn
   gunicorn app:app
   ```

---

## Option 4: Check Current Git Commit

### On GitHub

1. Go to: https://github.com/zfermi/Zenpdf
2. Check latest commit
3. Should show: "Add Pesapal payment integration"

### What Should Be There

Latest commit should include:
- ✅ payment.py
- ✅ pesapal_service.py
- ✅ Updated app.py
- ✅ Updated config.py
- ✅ Updated requirements.txt
- ✅ Updated templates/pricing.html

---

## Option 5: Manual Deployment Check

### Test locally first

```bash
# In your project folder
python app.py
```

Then visit: http://localhost:5000/pricing

**Should work**: Shows pricing page
**If 404**: There's an issue with the code

### Check app.py routes

```bash
grep -n "route.*pricing" app.py
```

Should show: `@app.route('/pricing')`

---

## Debugging Steps

### 1. Check if Railway has latest code

```bash
git log --oneline -1
```

Should show: `Add Pesapal payment integration`

### 2. Check Railway build logs

In Railway dashboard:
1. Deployments tab
2. Click latest deployment
3. View build logs

**Look for**:
```
Successfully installed requests-2.31.0
Building...
Build successful
```

**Should NOT see**:
- Import errors
- Missing files
- Build failures

### 3. Check Railway runtime logs

In Railway dashboard:
1. Deployments tab
2. Click latest deployment
3. View runtime logs

**Look for**:
```
ZenPDF startup
* Running on http://0.0.0.0:PORT
```

**Should NOT see**:
- ImportError: No module named 'payment'
- ImportError: No module named 'pesapal_service'
- 500 errors

### 4. Check environment variables

In Railway dashboard:
1. Variables tab
2. Verify all 5 Pesapal variables are set

**Required**:
- PESAPAL_CONSUMER_KEY
- PESAPAL_CONSUMER_SECRET
- PESAPAL_BASE_URL
- PESAPAL_IPN_URL
- PESAPAL_CALLBACK_URL

---

## Quick Fix Commands

Run these in order:

```bash
# 1. Check current commit
git log --oneline -1

# 2. Make sure all files are committed
git status

# 3. Force redeploy
git commit --allow-empty -m "Force Railway redeploy"
git push origin main

# 4. Wait 2-3 minutes for Railway to deploy

# 5. Test pricing page
curl -I https://bestpdfconverter.online/pricing
```

---

## Expected Result

After successful deployment:

```bash
curl -I https://bestpdfconverter.online/pricing
```

**Should return**:
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Server: railway-edge
```

**NOT**:
```
HTTP/1.1 404 Not Found
```

---

## Still Not Working?

### Check These:

1. **Wrong domain?**
   - Is bestpdfconverter.online pointing to Railway?
   - Check DNS settings
   - Check Railway custom domain settings

2. **Different server?**
   - Is the site hosted elsewhere?
   - Check where DNS points to
   - You might need to deploy there instead

3. **Railway not connected?**
   - Check Railway GitHub integration
   - Make sure auto-deploy is enabled
   - Reconnect GitHub if needed

---

## Contact Support

If nothing works:

**Railway Support**:
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/

**Your Code**:
- All files are committed
- All routes are defined
- All imports are correct

The issue is likely with deployment/server configuration, not the code.

---

**Next Step**: Figure out where your site is actually hosted, then deploy there.
