package com.iitj.healthcenter.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.iitj.healthcenter.domain.model.DoctorSchedule

@Composable
fun DoctorCard(
    schedule: DoctorSchedule,
    isSubscribed: Boolean,
    onSubscribeClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header with name and category badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = schedule.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                // Category badge
                Surface(
                    color = if (schedule.category.contains("Regular")) 
                        Color(0xFF10B981) else Color(0xFFA855F7),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = schedule.category,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                        color = Color.White,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Timing
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(text = "🕒 ", style = MaterialTheme.typography.bodyMedium)
                Text(
                    text = schedule.timing,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }
            
            // Room (if available)
            if (!schedule.room.isNullOrEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertical) {
                    Text(text = "📍 ", style = MaterialTheme.typography.bodySmall)
                    Text(
                        text = schedule.room,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Date
            Spacer(modifier = Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertical) {
                Text(text = "📅 ", style = MaterialTheme.typography.bodySmall)
                Text(
                    text = schedule.date,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Subscribe button
            OutlinedButton(
                onClick = onSubscribeClick,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = if (isSubscribed) MaterialTheme.colorScheme.primaryContainer
                    else Color.Transparent
                ),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary)
            ) {
                Text(
                    text = if (isSubscribed) "✓ Subscribed" else "Subscribe",
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}
