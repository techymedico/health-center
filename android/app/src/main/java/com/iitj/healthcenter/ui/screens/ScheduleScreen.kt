package com.iitj.healthcenter.ui.screens

import android.content.Context
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.iitj.healthcenter.ui.components.DoctorCard
import com.iitj.healthcenter.viewmodel.ScheduleViewModel
import java.util.UUID

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScheduleScreen(viewModel: ScheduleViewModel) {
    val context = LocalContext.current
    val schedules by viewModel.schedules.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val subscribedDoctors by viewModel.subscribedDoctors.collectAsState()
    
    val deviceId = getDeviceId(context)
    
    LaunchedEffect(Unit) {
        viewModel.loadSubscriptions(deviceId)
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text("IITJ Health Center", fontWeight = FontWeight.Bold)
                        Text(
                            "Doctor Schedule",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Date filter buttons
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterButton(
                    text = "Today",
                    onClick = { viewModel.loadSchedules(viewModel.getTodayDate()) }
                )
                FilterButton(
                    text = "Tomorrow",
                    onClick = { viewModel.loadSchedules(viewModel.getTomorrowDate()) }
                )
                FilterButton(
                    text = "All",
                    onClick = { viewModel.loadSchedules(null) }
                )
            }
            
            when {
                isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                
                error != null -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Error: $error",
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
                
                schedules.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("No schedules found")
                    }
                }
                
                else -> {
                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(schedules) { schedule ->
                            DoctorCard(
                                schedule = schedule,
                                isSubscribed = subscribedDoctors.contains(schedule.name),
                                onSubscribeClick = {
                                    if (subscribedDoctors.contains(schedule.name)) {
                                        viewModel.unsubscribeDoctor(deviceId, schedule.name)
                                    } else {
                                        viewModel.subscribeDoctor(deviceId, schedule.name)
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FilterButton(text: String, onClick: () -> Unit) {
    FilledTonalButton(onClick = onClick) {
        Text(text)
    }
}

fun getDeviceId(context: Context): String {
    val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
    var deviceId = prefs.getString("device_id", null)
    
    if (deviceId == null) {
        deviceId = UUID.randomUUID().toString()
        prefs.edit().putString("device_id", deviceId).apply()
    }
    
    return deviceId
}
