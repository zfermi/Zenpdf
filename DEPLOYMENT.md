# ZenPDF Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest) 🚂

1. **Sign up at [railway.app](https://railway.app)**

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `zfermi/Zenpdf` repository
   - Railway auto-detects Python

3. **Set Environment Variables:**
   - Go to Variables tab
   - Add: `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Add: `FLASK_ENV` = `production`
   - Add: `FLASK_DEBUG` = `False`

4. **Deploy:**
   - Railway auto-deploys on push
   - Get your URL: `https://your-app-name.railway.app`

5. **Custom Domain (Optional):**
   - Go to Settings → Domains
   - Add custom domain
   - Railway provides SSL automatically

**Cost:** $5-20/month  
**Time:** 10 minutes  
**Difficulty:** ⭐ Easy

---

### Option 2: Heroku

1. **Install Heroku CLI:**
   ```bash
   # Download from heroku.com/cli
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   heroku create zenpdf
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   heroku config:set FLASK_ENV=production
   heroku config:set FLASK_DEBUG=False
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Open app:**
   ```bash
   heroku open
   ```

**Cost:** $7/month (hobby dyno)  
**Time:** 15 minutes  
**Difficulty:** ⭐⭐ Medium

---

### Option 3: DigitalOcean App Platform

1. **Sign up at [digitalocean.com](https://digitalocean.com)**

2. **Create app:**
   - Go to App Platform
   - Click "Create App"
   - Connect GitHub repo: `zfermi/Zenpdf`
   - Select Python as runtime

3. **Configure:**
   - Build command: `pip install -r requirements.txt`
   - Run command: `python app.py`
   - Environment variables:
     - `SECRET_KEY` = (generate)
     - `FLASK_ENV` = `production`
     - `PORT` = `8080`

4. **Deploy:**
   - Click "Create Resources"
   - App deploys automatically

**Cost:** $5-12/month  
**Time:** 15 minutes  
**Difficulty:** ⭐⭐ Medium

---

### Option 4: Render

1. **Sign up at [render.com](https://render.com)**

2. **Create web service:**
   - New → Web Service
   - Connect GitHub repo: `zfermi/Zenpdf`

3. **Configure:**
   - Build command: `pip install -r requirements.txt`
   - Start command: `python app.py`
   - Environment variables:
     - `SECRET_KEY` = (generate)
     - `FLASK_ENV` = `production`

4. **Deploy:**
   - Click "Create Web Service"
   - Get URL: `https://zenpdf.onrender.com`

**Cost:** Free tier available, $7/month for production  
**Time:** 10 minutes  
**Difficulty:** ⭐ Easy

---

## Pre-Deployment Checklist

Before deploying:

- [x] Code is committed to GitHub
- [x] Version is set (v1.0.0)
- [ ] Generate `SECRET_KEY`:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Test locally:
  ```bash
  python app.py
  ```
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Test file upload/download functionality
- [ ] Check `.gitignore` excludes sensitive files

---

## Post-Deployment Checklist

After deploying:

- [ ] Test app is accessible via URL
- [ ] Test PDF split functionality
- [ ] Test PDF merge functionality
- [ ] Test error handling (try invalid files)
- [ ] Verify files are deleted after processing
- [ ] Check logs for errors
- [ ] Test on mobile device
- [ ] Set up custom domain (optional)
- [ ] Set up Google Analytics (optional)
- [ ] Set up Google AdSense (optional)

---

## Environment Variables

**Required:**
- `SECRET_KEY` - Flask session secret (generate unique key)
- `FLASK_ENV` - Set to `production` for production

**Optional:**
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 0.0.0.0)
- `FLASK_DEBUG` - Set to `False` for production

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Troubleshooting

### App won't start
- Check logs for errors
- Verify `SECRET_KEY` is set
- Check `requirements.txt` dependencies
- Ensure `PORT` environment variable matches platform

### File upload fails
- Check file size limits (10MB)
- Verify upload directories exist
- Check platform file system permissions

### 500 Internal Server Error
- Check application logs
- Verify all dependencies installed
- Check environment variables are set
- Review error logs in platform dashboard

### SSL/HTTPS Issues
- Most platforms auto-provide SSL
- Railway/Heroku/Render: SSL automatic
- For custom domains, verify DNS settings

---

## Monitoring

Set up monitoring after deployment:

1. **Application Logs:**
   - Railway: View in dashboard
   - Heroku: `heroku logs --tail`
   - DigitalOcean: View in App Platform

2. **Uptime Monitoring:**
   - UptimeRobot (free)
   - Pingdom
   - StatusCake

3. **Error Tracking:**
   - Sentry (free tier available)
   - Rollbar
   - LogRocket

---

## Scaling

When you need to scale:

1. **Increase resources:**
   - Railway: Upgrade plan
   - Heroku: Upgrade dyno size
   - DigitalOcean: Increase app resources

2. **Add database:**
   - For user tracking
   - For premium subscriptions
   - PostgreSQL recommended

3. **CDN for static files:**
   - Cloudflare (free)
   - AWS CloudFront
   - Fastly

4. **File storage:**
   - AWS S3 for file uploads
   - DigitalOcean Spaces
   - Google Cloud Storage

---

## Recommended First Deployment: Railway

**Why Railway:**
- ✅ Easiest setup (5 minutes)
- ✅ Auto-deploys from GitHub
- ✅ Free SSL included
- ✅ Good free tier
- ✅ Simple pricing
- ✅ Great documentation

**Steps:**
1. Go to railway.app
2. Connect GitHub
3. Select repository
4. Add environment variables
5. Deploy!

**That's it!** 🚀

