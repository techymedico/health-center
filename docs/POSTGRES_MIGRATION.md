# PostgreSQL Migration Guide

Migrate from SQLite to PostgreSQL for production-grade persistence.

## Why PostgreSQL?

**SQLite Issues on Render:**
- Ephemeral filesystem (data lost on redeploy)
- No concurrent writes
- Limited for production use

**PostgreSQL Benefits:**
- Persistent storage (survives redeploys)
- Better performance
- Production-ready
- **FREE** on Render (500 MB storage)

## 🚀 Migration Steps

### Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `iitj-doctor-schedule-db`
   - **Database**: `doctor_schedule`
   - **User**: (auto-generated)
   - **Region**: Same as your web service
   - **Plan**: **Free**
4. Click **Create Database**

### Step 2: Get Connection String

1. Wait for database to provision (~2 minutes)
2. Copy **Internal Database URL** (starts with `postgresql://`)
   - Format: `postgresql://user:password@host:port/database`

### Step 3: Update Backend Configuration

#### Option A: Update Environment Variable

1. Go to your web service on Render
2. Environment → Edit
3. Update `DATABASE_URL` to your PostgreSQL URL
4. Save changes
5. Render will automatically redeploy

#### Option B: Update render.yaml (for Blueprint)

```yaml
services:
  - type: web
    name: iitj-doctor-schedule-api
    env: python
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: iitj-doctor-schedule-db
          property: connectionString
```

### Step 4: Add psycopg2 to Requirements

Update `backend/requirements.txt`:

```txt
# Add this line
psycopg2-binary==2.9.10
```

Commit and push to GitHub. Render will rebuild.

### Step 5: Verify Migration

```bash
# Check backend logs
# You should see: "Connected to PostgreSQL"

# Test API
curl https://your-app.onrender.com/schedules

# Trigger scrape to populate database
curl -X POST https://your-app.onrender.com/ingest-scraped-data
```

### Step 6: Backup Strategy (Optional)

Render PostgreSQL free tier doesn't include automated backups.

**Manual Backup:**

```bash
# Install PostgreSQL client locally
brew install postgresql  # macOS
# or
sudo apt install postgresql-client  # Linux

# Backup database
pg_dump "postgresql://user:password@host:port/database" > backup.sql

# Restore
psql "postgresql://user:password@host:port/database" < backup.sql
```

**Automated Backup with GitHub Actions:**

Create `.github/workflows/backup-db.yml`:

```yaml
name: Database Backup

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup PostgreSQL
        run: |
          pg_dump "${{ secrets.DATABASE_URL }}" > backup-$(date +%Y%m%d).sql
      
      - name: Upload backup
        uses: actions/upload-artifact@v3
        with:
          name: database-backup
          path: backup-*.sql
```

## 🔄 Rollback to SQLite

If you need to rollback:

1. Update `DATABASE_URL` to:
   ```
   sqlite:///./doctor_schedule.db
   ```
2. Remove `psycopg2-binary` from requirements.txt
3. Redeploy

## 📊 Database Schema

Both SQLite and PostgreSQL use the same schema (SQLAlchemy handles differences):

```sql
-- schedules table
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    date VARCHAR,
    name VARCHAR,
    timing VARCHAR,
    category VARCHAR,
    room VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- subscriptions table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    email VARCHAR,
    push_subscription TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Performance Optimization

After migrating to PostgreSQL, consider these optimizations:

### Add Indexes

Update `backend/app/database.py`:

```python
class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)  # ✅ Already indexed
    name = Column(String, index=True)  # ⬅️ Add index for search
    # ... rest of columns
```

### Connection Pooling

Update `backend/app/database.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,           # Max 5 connections
    max_overflow=10,       # Allow 10 extra during peak
    pool_pre_ping=True,    # Check connection before use
    pool_recycle=3600      # Recycle after 1 hour
)
```

## 💡 Tips

- **Free tier limit**: 500 MB storage (sufficient for this app)
- **Monitor usage**: Check Render dashboard for storage metrics
- **Data retention**: Free tier keeps data for 90 days of inactivity
- **Upgrade path**: $7/month for 1 GB if you outgrow free tier

## ✅ Checklist

- [ ] PostgreSQL database created on Render
- [ ] Connection string copied
- [ ] `DATABASE_URL` updated in web service
- [ ] `psycopg2-binary` added to requirements.txt
- [ ] Backend redeployed
- [ ] Migration verified (schedules loading)
- [ ] Backup strategy implemented (optional)

---

Questions? Check [Render PostgreSQL docs](https://render.com/docs/databases) or open an issue!
