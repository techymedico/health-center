package com.iitj.healthcenter.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.iitj.healthcenter.data.repository.DoctorRepository
import com.iitj.healthcenter.domain.model.DoctorSchedule
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class ScheduleViewModel(
    private val repository: DoctorRepository
) : ViewModel() {
    
    private val _schedules = MutableStateFlow<List<DoctorSchedule>>(emptyList())
    val schedules: StateFlow<List<DoctorSchedule>> = _schedules.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _subscribedDoctors = MutableStateFlow<Set<String>>(emptySet())
    val subscribedDoctors: StateFlow<Set<String>> = _subscribedDoctors.asStateFlow()
    
    init {
        loadSchedules()
    }
    
    fun loadSchedules(date: String? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.getSchedules(date).fold(
                onSuccess = { schedules ->
                    _schedules.value = schedules
                    _isLoading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "Failed to load schedules"
                    _isLoading.value = false
                }
            )
        }
    }
    
    fun loadSubscriptions(deviceId: String) {
        viewModelScope.launch {
            repository.getSubscriptions(deviceId).fold(
                onSuccess = { doctors ->
                    _subscribedDoctors.value = doctors.toSet()
                },
                onFailure = { /* ignore */ }
            )
        }
    }
    
    fun subscribe Doctor(deviceId: String, doctorName: String) {
        viewModelScope.launch {
            repository.subscribeDoctor(deviceId, doctorName).fold(
                onSuccess = {
                    _subscribedDoctors.value = _subscribedDoctors.value + doctorName
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "Failed to subscribe"
                }
            )
        }
    }
    
    fun unsubscribeDoctor(deviceId: String, doctorName: String) {
        viewModelScope.launch {
            repository.unsubscribeDoctor(deviceId, doctorName).fold(
                onSuccess = {
                    _subscribedDoctors.value = _subscribedDoctors.value - doctorName
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "Failed to unsubscribe"
                }
            )
        }
    }
    
    fun getTodayDate(): String {
        val sdf = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
        return sdf.format(Date())
    }
    
    fun getTomorrowDate(): String {
        val calendar = Calendar.getInstance()
        calendar.add(Calendar.DAY_OF_YEAR, 1)
        val sdf = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
        return sdf.format(calendar.time)
    }
}
