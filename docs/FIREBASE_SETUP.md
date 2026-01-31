# Firebase Setup Guide

Complete guide to set up Firebase Cloud Messaging for the IITJ Health Center app.

---

## 🔥 Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **Add project**
3. Enter project name: `IITJ Health Center`
4. Disable Google Analytics (optional for this project)
5. Click **Create project**
6. Wait for setup to complete (~30 seconds)

---

## 📱 Step 2: Add Android App to Firebase

1. In Firebase Console, click the **Android icon** (⚙️ → Project Settings)
2. Scroll to "Your apps" section
3. Click **Add app** → **Android**
4. Fill in:
   - **Android package name**: `com.iitj.healthcenter`
   - **App nickname** (optional): `IITJ Health Center Android`
   - **Debug signing certificate SHA-1** (optional for FCM)
5. Click **Register app**
6. **Download `google-services.json`**
7. Place `google-services.json` in `android/app/` directory
8. Click **Next** → **Next** → **Continue to console**

---

## 🔑 Step 3: Get Firebase Service Account Key (for Backend)

1. In Firebase Console → Project Settings (⚙️ icon)
2. Go to **Service Accounts** tab
3. Click **Generate new private key**
4. Click **Generate key** → Download JSON file
5. Rename it to `firebase-service-account.json`
6. Place in `backend/` directory

> [!CAUTION]
> NEVER commit this file to Git! It contains sensitive credentials.

---

## 🖥️ Step 4: Configure Backend

### Update `.env` file:

```bash
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
```

### Test Firebase initialization:

```bash
cd backend
source venv/bin/activate
python -c "from app.services.fcm_service import initialize_firebase; initialize_firebase(); print('Firebase initialized!')"
```

---

## 📲 Step 5: Build Android App

### Update Backend URL:

Edit `android/app/src/main/java/com/iitj/healthcenter/RetrofitInstance.kt`:

```kotlin
private const val BASE_URL = "https://your-actual-backend.onrender.com/"
```

### Build APK:

```bash
cd android
./gradlew assembleDebug
```

APK location: `android/app/build/outputs/apk/debug/app-debug.apk`

### Install APK:

```bash
# Via ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Or transfer to phone and install manually
```

---

## ✅ Step 6: Test FCM Flow

### Testing Notification Delivery:

1. **Open the Android app** on your device
2. **Grant notification permission** when prompted
3. **App automatically registers FCM token** with backend
4. **Subscribe to a doctor** by tapping the "Subscribe" button
5. **Backend will send FCM notification** when that doctor's duty starts

### Manual Token Registration Test:

```bash
# Get FCM token from Android app logs (Logcat in Android Studio)
# Then test registration:

curl -X POST https://your-backend.onrender.com/register-fcm-token \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device-123",
    "fcm_token": "YOUR_FCM_TOKEN_HERE"
  }'
```

### Test Subscription:

```bash
curl -X POST https://your-backend.onrender.com/subscribe-doctor \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device-123",
    "doctor_name": "Dr. XYZ"
  }'
```

---

## 🐛 Troubleshooting

### FCM Token Not Generating

**Symptoms**: No FCM token in Logcat

**Solutions**:
- Verify `google-services.json` is in `android/app/`
- Check internet connection on device
- Rebuild app: `./gradlew clean assembleDebug`
- Check Firebase Console → Project Settings → Cloud Messaging → API is enabled

### Notifications Not Received

**Symptoms**: App subscribed but no notifications

**Solutions**:
1. **Check backend logs** for FCM sending errors
2. **Verify Firebase service account** is configured correctly
3. **Check notification permission** is granted on device
4. **Verify device is subscribed**:
   ```bash
   curl https://your-backend.onrender.com/subscriptions/YOUR_DEVICE_ID
   ```

### Backend Firebase Init Fails

**Symptoms**: `Firebase not initialized` in backend logs

**Solutions**:
- Check `FIREBASE_CREDENTIALS_PATH` in `.env`
- Verify `firebase-service-account.json` exists at that path
- Validate JSON file is not corrupted
- Check file permissions: `chmod 644 firebase-service-account.json`

---

## 🎯 Production Deployments

### Render Backend

Add environment variable in Render dashboard:
```
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase-service-account.json
```

Upload `firebase-service-account.json` as a secret file in Render.

### Release APK

```bash
cd android
./gradlew assembleRelease
```

Sign the APK for Google Play Store distribution.

---

## 📊 Monitoring FCM

### Check Sent Messages:

Firebase Console → Cloud Messaging → Campaign shows:
- Total messages sent
- Delivery success rate
- Open rate (if analytics enabled)

### Backend Logs:

```bash
# Check FCM sending in Render logs
tail -f logs  # Or view in Render dashboard
```

Look for:
```
FCM sent to 5 devices for Dr. ABC
FCM notification sent successfully: projects/...
```

---

## 🔒 Security Checklist

- [ ] `google-services.json` added to `.gitignore`
- [ ] `firebase-service-account.json` added to `.gitignore`
- [ ] Firebase credentials stored as environment variables on Render
- [ ] FCM server key not exposed in client code
- [ ] Backend validates device IDs before sending notifications

---

## 💡 Tips

- **Test on real device**: Emulators may not receive FCM properly
- **Keep app in background**: Test notifications when app is not foreground
- **Check battery optimization**: Some devices kill background FCM
- **Firebase free tier**: Unlimited FCM messages (completely free!)

---

Need help? Check [Firebase documentation](https://firebase.google.com/docs/cloud-messaging) or open an issue!
