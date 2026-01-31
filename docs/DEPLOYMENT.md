# Deployment Guide

Complete step-by-step guide to deploy your IITJ Doctor Schedule app to **FREE** hosting services.

## 📋 Prerequisites

- GitHub account
- Gmail account with 2FA enabled
- Code pushed to GitHub repository

## 🔑 Step 1: Generate VAPID Keys

Web Push notifications require VAPID keys for authentication.

```bash
cd backend
source venv/bin/activate
python -c "from pywebpush import webpush; import json; print(json.dumps(webpush.generate_vapid_keys(), indent=2))"
```

Save the output - you'll need both `public` and `private` keys.

## 📧 Step 2: Get Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Search for "App Passwords"
4. Create new app password for "Mail"
5. Copy the 16-character password (you won't see it again!)

## 🚀 Step 3: Deploy Backend to Render

### 3.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### 3.2 Deploy from Blueprint

1. Click **New** → **Blueprint**
2. Connect your GitHub repository
3. Render detects `render.yaml` automatically
4. Click **Apply**

### 3.3 Configure Environment Variables

Go to your web service dashboard and set these environment variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `sqlite:///./doctor_schedule.db` (or PostgreSQL URL) |
| `FRONTEND_URL` | `https://your-app.vercel.app` (set after Vercel deploy) |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password from Step 2 |
| `SMTP_FROM` | Same as SMTP_USER |
| `VAPID_PRIVATE_KEY` | Private key from Step 1 |
| `VAPID_PUBLIC_KEY` | Public key from Step 1 |
| `VAPID_CLAIMS_EMAIL` | `mailto:your-email@example.com` |

### 3.4 Get Backend URL

After deployment completes, your backend URL will be:
```
https://your-app-name.onrender.com
```

Test it:
```bash
curl https://your-app-name.onrender.com/health
```

## 🎨 Step 4: Deploy Frontend to Vercel

### 4.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 4.2 Import Project

1. Click **Add New** → **Project**
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 4.3 Set Environment Variables

Add these in Vercel project settings:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-app-name.onrender.com` |
| `VITE_VAPID_PUBLIC_KEY` | Public key from Step 1 |

### 4.4 Deploy

Click **Deploy** - Vercel builds and deploys automatically!

Your frontend URL will be:
```
https://your-app.vercel.app
```

### 4.5 Update Backend CORS

Go back to Render and update these environment variables with your Vercel URL:
- `FRONTEND_URL`
- `ALLOWED_ORIGINS`

Redeploy the backend for changes to take effect.

## 🤖 Step 5: Setup GitHub Actions

### 5.1 Add Repository Secret

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click **New repository secret**
4. Name: `BACKEND_URL`
5. Value: `https://your-app-name.onrender.com`
6. Click **Add secret**

### 5.2 Test Workflow

1. Go to Actions tab in your repository
2. Select "Scheduled Scraping and Keep-Alive"
3. Click "Run workflow" → "Run workflow"
4. Check that it completes successfully

The workflow will now:
- Scrape data daily at 6 AM IST
- Ping your backend every 10 minutes (9 AM - 6 PM IST) to prevent sleep

## ✅ Step 6: Verify Deployment

### 6.1 Test Backend

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Get schedules
curl https://your-app-name.onrender.com/schedules

# Trigger manual scrape
curl -X POST https://your-app-name.onrender.com/ingest-scraped-data
```

### 6.2 Test Frontend

1. Open `https://your-app.vercel.app` in browser
2. Verify schedules load
3. Test date filters
4. Subscribe to email notifications
5. Enable push notifications (grant permission)

### 6.3 Test Notifications

**Email Test:**
1. Subscribe with your email
2. Backend checks every minute for upcoming doctors
3. You'll receive email if any doctor starts within 60 minutes

**Push Test:**
1. Enable push notifications
2. Keep browser open
3. Wait for notification (or manually test via backend)

## 🔧 Troubleshooting

### Backend Issues

**Service won't start:**
- Check Render logs for errors
- Verify all environment variables are set
- Check Python version is 3.11+

**Database errors:**
- SQLite is ephemeral on Render free tier
- Use persistent disk (free add-on) or migrate to PostgreSQL

**Scraper fails:**
- Check logs: `tail -f backend logs on Render`
- IITJ website might have changed structure

### Frontend Issues

**API calls fail:**
- Verify `VITE_API_URL` is correct
- Check browser console for CORS errors
- Ensure backend `ALLOWED_ORIGINS` includes Vercel URL

**Push notifications don't work:**
- Verify VAPID keys match between frontend and backend
- Ensure HTTPS (both Render and Vercel provide this)
- Check browser supports push (most modern browsers do)

**Service Worker errors:**
- Clear browser cache
- Check `sw.js` is being served correctly
- Verify `vercel.json` headers are set

### GitHub Actions Issues

**Workflow fails:**
- Check `BACKEND_URL` secret is set correctly
- Verify backend is accessible publicly
- Check workflow logs for specific errors

**Service still sleeps:**
- Render free tier sleeps after 15 mins inactivity
- GitHub Actions pings every 10 mins during business hours
- Consider upgrading to paid tier for always-on service

## 🎯 Next Steps

- [Migrate to PostgreSQL](POSTGRES_MIGRATION.md) for production persistence
- [Scale your app](SCALING.md) beyond free tier if needed
- Customize UI colors and branding
- Add more notification channels (SMS, WhatsApp, etc.)

## 💰 Cost Breakdown

| Service | Free Tier | Limits |
|---------|-----------|--------|
| Render | 750 hours/month | Sleeps after 15 mins |
| Vercel | Unlimited | 100 GB bandwidth |
| GitHub Actions | 2000 mins/month | More than enough |
| **Total** | **$0/month** | 🎉 |

---

Need help? Open an issue on GitHub!
