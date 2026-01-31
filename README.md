# IITJ Health Center Doctor Schedule Web App

> A complete full-stack web application for viewing doctor schedules at IITJ Health Center with real-time notifications. **100% FREE hosting** using Render (backend) and Vercel (frontend).

## IITJ Doctor Schedule - Web + Android + FCM

> **Full-stack doctor schedule system with React web app, Android mobile app, and Firebase Cloud Messaging notifications - ALL hosted on FREE tiers!**

[![Deploy Status](https://img.shields.io/badge/deploy-ready-success)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Free Hosting](https://img.shields.io/badge/hosting-100%25%20free-green)]()

---

## 🌟 Features

### Web Application
- 📅 **Real-time schedule display** - View doctor schedules by date
- 🔍 **Smart filtering** - Filter by today, tomorrow, or custom dates
- 📧 **Email notifications** - Get notified via email
- 🔔 **Web push notifications** - Browser notifications for upcoming duties
- 🎨 **Beautiful UI** - Modern design with glassmorphism and gradients
- 📱 **Fully responsive** - Works on all devices

### Android Application
- 📱 **Native Android app** - Built with Kotlin & Jetpack Compose
- 🔥 **Firebase push notifications** - Real-time FCM notifications
- 🎯 **Doctor-specific subscriptions** - Subscribe only to doctors you care about
- 🏗️ **MVVM architecture** - Clean, maintainable code structure
- 🎨 **Material Design 3** - Modern Android UI

### Backend
- ⚡ **FastAPI** - High-performance Python backend
- 🤖 **Auto-scraping** - Scheduled data extraction every 6 hours
- 📊 **Database** - SQLite with PostgreSQL upgrade path
- 🔥 **Firebase Admin SDK** - Server-side FCM integration
- 🔔 **Multi-channel notifications** - Email, Web Push, and FCM

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          User Devices                    │
├──────────────┬────────────┬──────────────┤
│ Web Browser  │  Android   │  iOS (future)│
└──────┬───────┴─────┬──────┴──────────────┘
       │             │
       │             │
       ▼             ▼
┌──────────────┬─────────────────┐
│Vercel (Web)  │                 │
│React+Tailwind│    Render       │
└──────┬───────┤   (Backend)     │
       │       │    FastAPI      │
       │       └────┬─────┬──────┘
       │            │     │
       ▼            ▼     ▼
    API calls   Firebase  DB
                  FCM    SQLite
```

## 📂 Project Structure

```
iitj_health_center_scraper/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy models & DB setup
│   │   ├── scheduler.py         # APScheduler background jobs
│   │   ├── routes/              # API endpoints
│   │   │   ├── schedule.py      # Schedule endpoints
│   │   │   ├── notifications.py # Web/email subscription
│   │   │   └── fcm.py           # FCM device & subscription endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── scraper_service.py
│   │   │   ├── notification_service.py
│   │   │   └── fcm_service.py   # Firebase Cloud Messaging
│   │   └── scraper/             # Original scraper code
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variable template
│   └── firebase-service-account.json.example  # Firebase credentials template
├── frontend/                     # React Web App
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── components/          # Reusable components
│   │   └── services/            # API client & push notifications
│   ├── public/
│   │   └── sw.js                # Service worker for push
│   ├── package.json
│   └── vercel.json              # Vercel deployment config
├── android/                      # Android Mobile App
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/iitj/healthcenter/
│   │   │   │   ├── MainActivity.kt          # App entry point
│   │   │   │   ├── RetrofitInstance.kt      # API client
│   │   │   │   ├── data/
│   │   │   │   │   ├── remote/              # API DTOs & service
│   │   │   │   │   └── repository/          # Data repository
│   │   │   │   ├── domain/model/            # Domain models
│   │   │   │   ├── ui/
│   │   │   │   │   ├── screens/             # Compose screens
│   │   │   │   │   └── components/          # Reusable UI components
│   │   │   │   ├── viewmodel/               # MVVM ViewModels
│   │   │   │   └── services/
│   │   │   │       └── MyFirebaseMessagingService.kt  # FCM handler
│   │   │   ├── res/                         # Android resources
│   │   │   └── AndroidManifest.xml
│   │   ├── build.gradle.kts                 # App-level Gradle
│   │   └── google-services.json.example     # Firebase config template
│   ├── build.gradle.kts                     # Project-level Gradle
│   └── settings.gradle.kts
├── .github/workflows/            # GitHub Actions
│   └── scheduled-scrape.yml     # Daily scraping + keep-alive
├── docs/                         # Documentation
│   ├── DEPLOYMENT.md            # Deployment guide (Web + Backend)
│   ├── FIREBASE_SETUP.md        # Firebase setup guide
│   ├── ANDROID_BUILD.md         # Android build guide
│   ├── POSTGRES_MIGRATION.md    # Database upgrade guide
│   └── SCALING.md               # Scaling beyond free tier
├── render.yaml                   # Render deployment config
├── .gitignore
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Git and GitHub account
- Gmail account (for email notifications)

### 3. Firebase Setup (for Android notifications)

See [docs/FIREBASE_SETUP.md](docs/FIREBASE_SETUP.md) for complete guide.

**Quick version:**
1. Create Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Add Android app with package `com.iitj.healthcenter`
3. Download `google-services.json` → Place in `android/app/`
4. Download Firebase service account JSON → Place in `backend/` as `firebase-service-account.json`
5. Update backend `.env`:
   ```bash
   FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
   ```

### 4. Android App

See [docs/ANDROID_BUILD.md](docs/ANDROID_BUILD.md) for complete guide.

**Quick build:**
```bash
cd android

# Update backend URL in RetrofitInstance.kt first!
# Then build:
./gradlew assembleDebug

# Install on device
adb install app/build/outputs/apk/debug/app-debug.apk
```

**Requirements:**
- Android Studio
- Android SDK 24+
- `google-services.json` from Firebase

### Local Development

**1. Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Generate VAPID keys for push notifications
python -c "from pywebpush import webpush; import json; print(json.dumps(webpush.generate_vapid_keys()))"

# Run server
uvicorn app.main:app --reload
# Backend runs at http://localhost:8000
```

**2. Frontend Setup**

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Run dev server
npm run dev
# Frontend runs at http://localhost:5173
```

**3. Open Browser**

Visit `http://localhost:5173` to see the app!

## 🌐 Deployment

### Backend (Render)

1. Push code to GitHub
3. Set root directory to `frontend`
4. Add environment variables:
   - `VITE_API_URL` = Your Render backend URL
   - `VITE_VAPID_PUBLIC_KEY` = Your VAPID public key
5. Deploy! 🚀

### GitHub Actions Setup

1. Go to repository Settings → Secrets and variables → Actions
2. Add secret: `BACKEND_URL` = Your Render backend URL
3. Workflow runs automatically (scrapes daily + keeps service awake)

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | SQLite or PostgreSQL connection string | ✅ |
| `SMTP_USER` | Gmail address for sending emails | ✅ |
| `SMTP_PASSWORD` | Gmail App Password ([guide](https://support.google.com/accounts/answer/185833)) | ✅ |
| `VAPID_PRIVATE_KEY` | Web Push private key | ✅ |
| `VAPID_PUBLIC_KEY` | Web Push public key | ✅ |
| `FRONTEND_URL` | Your Vercel URL for CORS | ✅ |

### Frontend Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |
| `VITE_VAPID_PUBLIC_KEY` | Web Push public key |

## 📱 Features Guide

### Email Notifications

1. Enter your email in the notification section
2. Click "Subscribe"
3. Receive emails when doctors are starting duty (within 60 mins)

### Push Notifications

1. Click "Enable Push Notifications"
2. Grant browser permission
3. Receive notifications even when browser is closed

### Date Filtering

- Click "Today" or "Tomorrow" for quick filters
- View schedules for specific dates
- Clear filter to see all schedules

## 🔒 Free Tier Limitations

- **Render**: Web service sleeps after 15 mins inactivity (GitHub Actions keeps it awake)
- **Render**: 750 hours/month free tier (sufficient for this use case)
- **Vercel**: Unlimited free deployments
- **SQLite**: Data persists but use PostgreSQL free add-on for production

## 📖 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Step-by-step deployment instructions
- [PostgreSQL Migration](docs/POSTGRES_MIGRATION.md) - Migrate from SQLite to PostgreSQL
- [Scaling Guide](docs/SCALING.md) - Tips for scaling beyond free tier

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database
- APScheduler - Background job scheduling
- pywebpush - Web Push notifications
- BeautifulSoup - Web scraping

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client
- date-fns - Date utilities

**DevOps:**
- Render - Backend hosting
- Vercel - Frontend hosting
- GitHub Actions - Automation

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

## 📄 License

MIT License - feel free to use for your institution!

## 💡 Support

For issues or questions, please open a GitHub issue.

---

Made with ❤️ for IITJ Community
