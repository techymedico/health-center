# Android App Build & Run Guide

Step-by-step guide to build and run the IITJ Health Center Android app.

---

## 📋 Prerequisites

### Required Software

- **Android Studio**: [Download Latest Version](https://developer.android.com/studio)
- **JDK 11 or higher**: Usually bundled with Android Studio
- **Android SDK 24+**: Installed via Android Studio SDK Manager

### Required Files

- ✅ `google-services.json` (from Firebase Console)
- ✅ Backend deployed and running on Render

---

## 🚀 Quick Start (5 Minutes)

### 1. Setup Firebase

Follow [FIREBASE_SETUP.md](FIREBASE_SETUP.md) to:
- Create Firebase project
- Add Android app
- Download `google-services.json`
- Place it in `android/app/`

### 2. Update Backend URL

Edit `android/app/src/main/java/com/iitj/healthcenter/RetrofitInstance.kt`:

```kotlin
private const val BASE_URL = "https://YOUR_BACKEND_URL.onrender.com/"
```

Replace `YOUR_BACKEND_URL` with your actual Render backend URL.

### 3. Build and Run

```bash
cd android
./gradlew assembleDebug
```

Install on device:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 🛠️ Development Setup

### Open in Android Studio

1. Launch Android Studio
2. File → Open → Select `android/` folder
3. Wait for Gradle sync to complete (~2-5 minutes first time)
4. Build → Make Project (Ctrl+F9 / Cmd+F9)

### Run on Emulator

1. Tools → Device Manager
2. Create Device → Select Pixel 5 or similar
3. Download system image (API 33 recommended)
4. Click ▶️ Run button (or Shift+F10)

### Run on Physical Device

1. Enable **Developer Options** on your Android device:
   - Settings → About Phone → Tap "Build Number" 7 times
2. Enable **USB Debugging**:
   - Settings → Developer Options → USB Debugging
3. Connect device via USB
4. Click ▶️ Run button → Select your device

---

## 📦 Build Variants

### Debug APK (Development)

```bash
./gradlew assembleDebug
```

Location: `app/build/outputs/apk/debug/app-debug.apk`

**Features:**
- Logging enabled
- No code obfuscation
- Larger file size (~15 MB)

### Release APK (Production)

```bash
./gradlew assembleRelease
```

Location: `app/build/outputs/apk/release/app-release-unsigned.apk`

**Features:**
- Logging disabled
- ProGuard enabled
- Minified code
- Smaller file size (~8 MB)

> [!NOTE]
> Release APK needs to be signed for installation. See [Signing Guide](#signing-apk-for-release) below.

---

## 🔧 Configuration

### Update Backend URL

**File**: `RetrofitInstance.kt`

```kotlin
private const val BASE_URL = "https://your-backend.onrender.com/"
```

### Change App Name

**File**: `android/app/src/main/res/values/strings.xml`

```xml
<string name="app_name">Your Custom Name</string>
```

### Change App Icon

Replace files in `android/app/src/main/res/mipmap-*/ic_launcher.png`

Generate icons: [Android Asset Studio](https://romannurik.github.io/AndroidAssetStudio/icons-launcher.html)

### Change Package Name

> [!CAUTION]
> Changing package name requires updating Firebase configuration!

1. Refactor package in Android Studio
2. Update `applicationId` in `app/build.gradle.kts`
3. Re-download `google-services.json` from Firebase with new package name

---

## 🐛 Troubleshooting

### Gradle Sync Failed

**Symptom**: "Gradle sync failed" error

**Solutions**:
```bash
# Clear Gradle cache
./gradlew clean
rm -rf .gradle/

# Invalidate caches in Android Studio
File → Invalidate Caches → Invalidate and Restart
```

### Google Services Plugin Error

**Symptom**: "File google-services.json is missing"

**Solution**:
- Ensure `google-services.json` is in `android/app/` directory
- Verify file is valid JSON (not HTML error page)
- Rebuild project

### Build Fails with "Dependency Conflict"

**Solution**:
```bash
./gradlew app:dependencies
# Check for conflicting versions
# Update dependencies in app/build.gradle.kts
```

### App Crashes on Startup

**Solution**:
1. Check Logcat in Android Studio
2. Common issues:
   - Backend URL incorrect → Update `RetrofitInstance.kt`
   - Firebase not configured → Add `google-services.json`
   - Permission denied → Grant notification permission

### FCM Token Not Generated

**Solution**:
- Verify internet connection
- Check Google Play Services installed on device
- Rebuild app: `./gradlew clean assembleDebug`

---

## 📏 Signing APK for Release

### Generate Keystore

```bash
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

### Configure Signing in Gradle

Edit `app/build.gradle.kts`:

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("my-release-key.jks")
            storePassword = "your-keystore-password"
            keyAlias = "my-key-alias"
            keyPassword = "your-key-password"
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(...)
        }
    }
}
```

### Build Signed APK

```bash
./gradlew assembleRelease
```

Signed APK: `app/build/outputs/apk/release/app-release.apk`

---

## 📱 Testing Guide

### Manual Testing Checklist

- [ ] App launches successfully
- [ ] Schedules load from backend
- [ ] "Today" filter shows today's schedules
- [ ] "Tomorrow" filter shows tomorrow's schedules
- [ ] "All" filter shows all schedules
- [ ] Subscribe to doctor → Button shows "✓ Subscribed"
- [ ] Unsubscribe from doctor → Button shows "Subscribe"
- [ ] Grant notification permission works
- [ ] FCM token registered (check Logcat)
- [ ] Receive push notification when doctor duty starts
- [ ] Tap notification → App opens
- [ ] App works in background
- [ ] App works when killed

### Automated Testing

```bash
# Run unit tests
./gradlew test

# Run instrumented tests (requires device/emulator)
./gradlew connectedAndroidTest
```

---

## 📊 APK Size Optimization

Current sizes:
- Debug APK: ~15 MB
- Release APK: ~8 MB (with ProGuard)

### Further Optimization

**Enable R8 full mode** (app/build.gradle.kts):
```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true // Add this
    }
}
```

**Remove unused resources**:
```kotlin
android {
    buildFeatures {
        buildConfig = false
        resValues = false
    }
}
```

---

## 🎯 Production Deployment

### Google Play Store

1. **Sign with release keystore** (see above)
2. **Create App Bundle** (preferred format):
   ```bash
   ./gradlew bundleRelease
   ```
   AAB location: `app/build/outputs/bundle/release/app-release.aab`
3. **Upload to Google Play Console**
4. **Fill in store listing**
5. **Set up content rating**
6. **Publish!**

### Direct Distribution

For organizations without Play Store:

1. Build signed release APK
2. Host on secure server or use services like:
   - Firebase App Distribution (free)
   - GitHub Releases
   - Internal file server
3. Users download and install (requires "Unknown Sources" enabled)

---

## 💡 Tips

- **Use real device for FCM testing** - Emulators may have issues
- **Check Logcat constantly** - Shows API errors, FCM tokens, etc.
- **Enable airplane mode to test offline** - App should handle gracefully
- **Test with different Android versions** - Minimum API 24, test on API 33+

---

## 📚 Useful Commands

```bash
# Build debug APK
./gradlew assembleDebug

# Build release APK
./gradlew assembleRelease

# Install on connected device
./gradlew installDebug

# Uninstall from device
adb uninstall com.iitj.healthcenter

# View app logs
adb logcat | grep -i "iitj"

# List connected devices
adb devices

# Clear app data
adb shell pm clear com.iitj.healthcenter
```

---

Need help? Open an issue or check [Android Developer Documentation](https://developer.android.com/docs)!
