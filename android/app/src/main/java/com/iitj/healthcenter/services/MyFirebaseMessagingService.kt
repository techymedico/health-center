package com.iitj.healthcenter.services

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.iitj.healthcenter.MainActivity
import com.iitj.healthcenter.R
import com.iitj.healthcenter.RetrofitInstance
import com.iitj.healthcenter.data.remote.dto.RegisterTokenRequest
import com.iitj.healthcenter.data.repository.DoctorRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.UUID

class MyFirebaseMessagingService : FirebaseMessagingService() {
    
    companion object {
        private const val TAG = "FCMService"
        private const val CHANNEL_ID = "doctor_notifications"
    }
    
    override fun onNewToken(token: String) {
        Log.d(TAG, "New FCM token: $token")
        
        // Send token to backend
        val deviceId = getDeviceId()
        val repository = DoctorRepository(RetrofitInstance.apiService)
        
        CoroutineScope(Dispatchers.IO).launch {
            repository.registerFcmToken(deviceId, token)
        }
    }
    
    override fun onMessageReceived(message: RemoteMessage) {
        Log.d(TAG, "From: ${message.from}")
        
        // Handle notification
        message.notification?.let {
            showNotification(
                title = it.title ?: "Doctor Duty",
                body = it.body ?: "A doctor's duty is starting soon"
            )
        }
        
        // Handle data payload
        if (message.data.isNotEmpty()) {
            Log.d(TAG, "Message data: ${message.data}")
            val doctorName = message.data["doctor_name"]
            val category = message.data["category"]
            val timeRange = message.data["time_range"]
            
            showNotification(
                title = "🏥 Doctor Duty Started",
                body = "Dr. $doctorName ($category) - $timeRange"
            )
        }
    }
    
    private fun showNotification(title: String, body: String) {
        createNotificationChannel()
        
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()
        
        val notificationManager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Doctor Notifications",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for doctor duty schedules"
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun getDeviceId(): String {
        val prefs = getSharedPreferences("app_prefs", MODE_PRIVATE)
        var deviceId = prefs.getString("device_id", null)
        
        if (deviceId == null) {
            deviceId = UUID.randomUUID().toString()
            prefs.edit().putString("device_id", deviceId).apply()
        }
        
        return deviceId
    }
}
