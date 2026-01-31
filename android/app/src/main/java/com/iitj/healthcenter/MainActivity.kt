package com.iitj.healthcenter

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessaging
import com.iitj.healthcenter.data.repository.DoctorRepository
import com.iitj.healthcenter.ui.screens.ScheduleScreen
import com.iitj.healthcenter.viewmodel.ScheduleViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    
    private lateinit var viewModel: ScheduleViewModel
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            getFCMToken()
        } else {
            Toast.makeText(this, "Notification permission denied", Toast.LENGTH_SHORT).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize ViewModel
        val repository = DoctorRepository(RetrofitInstance.apiService)
        viewModel = ScheduleViewModel(repository)
        
        setContent {
            MaterialTheme {
                Surface {
                    ScheduleScreen(viewModel)
                }
            }
        }
        
        // Request notification permission (Android 13+)
        requestNotificationPermission()
        
        // Get FCM token
        getFCMToken()
    }
    
    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            when {
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED -> {
                    // Permission already granted
                }
                else -> {
                    // Request permission
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }
        }
    }
    
    private fun getFCMToken() {
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (!task.isSuccessful) {
                return@addOnCompleteListener
            }
            
            val token = task.result
            val deviceId = getSharedPreferences("app_prefs", MODE_PRIVATE)
                .getString("device_id", null) ?: return@addOnCompleteListener
            
            // Send token to backend
            val repository = DoctorRepository(RetrofitInstance.apiService)
            CoroutineScope(Dispatchers.IO).launch {
                repository.registerFcmToken(deviceId, token)
            }
        }
    }
}
