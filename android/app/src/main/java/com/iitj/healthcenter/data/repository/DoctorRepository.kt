package com.iitj.healthcenter.data.repository

import com.iitj.healthcenter.data.remote.ApiService
import com.iitj.healthcenter.data.remote.dto.*
import com.iitj.healthcenter.domain.model.DoctorSchedule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class DoctorRepository(private val apiService: ApiService) {
    
    suspend fun getSchedules(date: String? = null): Result<List<DoctorSchedule>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getSchedules(date)
                val schedules = response.data.map { dto ->
                    DoctorSchedule(
                        id = dto.id,
                        date = dto.date,
                        name = dto.name,
                        timing = dto.timing,
                        category = dto.category,
                        room = dto.room
                    )
                }
                Result.success(schedules)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    suspend fun registerFcmToken(deviceId: String, fcmToken: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.registerFcmToken(
                    RegisterTokenRequest(deviceId, fcmToken)
                )
                Result.success(response.message)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    suspend fun subscribeDoctor(deviceId: String, doctorName: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.subscribeDoctor(
                    SubscribeDoctorRequest(deviceId, doctorName)
                )
                Result.success(response.message)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    suspend fun unsubscribeDoctor(deviceId: String, doctorName: String): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.unsubscribeDoctor(
                    SubscribeDoctorRequest(deviceId, doctorName)
                )
                Result.success(response.message)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    suspend fun getSubscriptions(deviceId: String): Result<List<String>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getSubscriptions(deviceId)
                val doctors = response["subscribed_doctors"] as? List<String> ?: emptyList()
                Result.success(doctors)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
