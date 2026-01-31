# Scaling Guide

How to scale your IITJ Doctor Schedule app beyond the free tier.

## 📊 When to Scale?

### Signs You Need to Upgrade:

✅ **Backend sleeping affects users** - Render free tier sleeps after 15 mins  
✅ **High traffic** - More than 100 concurrent users  
✅ **Data loss concerns** - Need guaranteed database persistence  
✅ **More frequent scraping** - Want to scrape every hour instead of every 6 hours  
✅ **Advanced features** - SMS notifications, analytics, etc.  

## 💰 Upgrade Options

### Render Backend Upgrade

| Plan | Price | Benefits |
|------|-------|----------|
| **Free** | $0 | 750 hours, sleeps after 15 mins |
| **Starter** | $7/month | Always on, 512 MB RAM, no sleep |
| **Standard** | $25/month | 2 GB RAM, better performance |

**Recommendation:** Start with **Starter** plan ($7/month)

### Render PostgreSQL Upgrade

| Plan | Price | Storage |
|------|-------|---------|
| **Free** | $0 | 500 MB, 90-day retention |
| **Starter** | $7/month | 1 GB, automated backups |
| **Standard** | $20/month | 10 GB, point-in-time recovery |

**Recommendation:** **Starter** plan ($7/month) for production

### Vercel Upgrade

Frontend is usually fine on free tier!

| Plan | Price | Benefits |
|------|-------|----------|
| **Hobby** | $0 | Unlimited free deployments |
| **Pro** | $20/month | Advanced analytics, more bandwidth |

**Recommendation:** Stay on **Free** tier unless you need analytics

## 🚀 Performance Optimizations

### 1. Enable Backend Caching

Update `backend/app/main.py`:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Initialize cache (use Render Redis add-on - free)
@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cache schedule endpoint
@router.get("/schedules")
@cache(expire=300)  # Cache for 5 minutes
async def get_schedules(...):
    # ... existing code
```

Add to `requirements.txt`:
```
fastapi-cache2==0.2.1
aioredis==2.0.1
```

### 2. Frontend Optimizations

**Enable Code Splitting:**

```javascript
// frontend/src/App.jsx
import { lazy, Suspense } from 'react';

const NotificationManager = lazy(() => import('./components/NotificationManager'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <NotificationManager />
    </Suspense>
  );
}
```

**Add Service Worker Caching:**

```javascript
// frontend/public/sw.js
const CACHE_NAME = 'iitj-health-v1';
const urlsToCache = [
  '/',
  '/index.css',
  '/logo.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});
```

### 3. Database Indexing

Add indexes for faster queries:

```python
# backend/app/database.py
class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)  # ✅
    name = Column(String, index=True)  # ⬅️ Add
    category = Column(String, index=True)  # ⬅️ Add
```

### 4. Optimize Scraper

Reduce scraping frequency during off-hours:

```python
# backend/app/scheduler.py
from datetime import datetime

def smart_scraper_job():
    hour = datetime.now().hour
    # Scrape every 2 hours during day, 6 hours at night
    interval = 2 if 6 <= hour <= 22 else 6
    # ... run scraper
```

## 📈 Monitoring & Analytics

### 1. Add Logging

```python
# backend/app/main.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Add Error Tracking (Free)

Use [Sentry](https://sentry.io) (free tier available):

```bash
pip install sentry-sdk
```

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 3. Frontend Analytics

Use Vercel Analytics (free on Pro tier) or [Plausible](https://plausible.io):

```bash
npm install plausible-tracker
```

```javascript
// frontend/src/main.jsx
import Plausible from 'plausible-tracker';

const plausible = Plausible({
  domain: 'your-app.vercel.app'
});

plausible.trackPageview();
```

## 🔔 Advanced Notifications

### SMS Notifications (via Twilio)

```bash
pip install twilio
```

```python
# backend/app/services/notification_service.py
from twilio.rest import Client

def send_sms(phone, message):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_='+1234567890',
        to=phone
    )
```

**Cost:** ~$0.0075 per SMS on Twilio

### WhatsApp Notifications (via Twilio)

Similar to SMS but uses WhatsApp:

```python
client.messages.create(
    from_='whatsapp:+14155238886',
    to='whatsapp:+1234567890',
    body='Doctor arriving soon!'
)
```

**Cost:** ~$0.005 per message

## 🌍 Multi-Instance Deployment

For high availability, deploy to multiple regions:

```yaml
# render.yaml
services:
  - type: web
    name: iitj-api-us
    region: oregon
    # ... config
    
  - type: web
    name: iitj-api-eu
    region: frankfurt
    # ... config
```

Use a load balancer (e.g., Cloudflare) to route traffic.

## 📦 Containerization

Package backend as Docker for easier deployment:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy to:
- **Render** (supports Docker)
- **Railway** (free tier available)
- **Fly.io** (free tier available)

## 💵 Cost Estimates

### Minimal Production Setup

- Render Web Service (Starter): **$7/month**
- Render PostgreSQL (Starter): **$7/month**
- Vercel (Free): **$0**
- **Total: $14/month**

### Full-Featured Setup

- Render Web Service (Standard): **$25/month**
- Render PostgreSQL (Standard): **$20/month**
- Vercel Pro: **$20/month**
- Sentry (Team): **$26/month**
- Twilio SMS: **~$10/month**
- **Total: ~$101/month**

## ✅ Scaling Checklist

- [ ] Upgrade Render web service to Starter ($7/month)
- [ ] Migrate to PostgreSQL Starter plan ($7/month)
- [ ] Add database indexes for performance
- [ ] Enable caching (Redis add-on)
- [ ] Add error tracking (Sentry)
- [ ] Optimize scraper schedule
- [ ] Add monitoring/logging
- [ ] Consider SMS/WhatsApp notifications
- [ ] Set up automated backups
- [ ] Add health monitoring

## 🎯 Recommended Upgrade Path

1. **Month 1-2**: Stay on free tier, monitor usage
2. **Month 3**: Upgrade Render to Starter if backend sleep is annoying ($7/month)
3. **Month 4**: Migrate to PostgreSQL Starter for persistence ($7/month)
4. **Month 5+**: Add advanced features (SMS, analytics) as needed

---

Questions about scaling? Open an issue on GitHub!
