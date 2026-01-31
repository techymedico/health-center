package com.iitj.healthcenter.data.remote

import com.iitj.healthcenter.data.remote.dto.*
import retrofit2.http.*

interface ApiService {
    
    @GET("schedules")
    suspend fun getSchedules(
        @Query("date") date: String? = null
    ): SchedulesResponse
    
    @POST("register-fcm-token")
    suspend fun registerFcmToken(
        @Body request: RegisterTokenRequest
    ): ApiResponse
    
    @POST("subscribe-doctor")
    suspend fun subscribeDoctor(
        @Body request: SubscribeDoctorRequest
    ): ApiResponse
    
    @POST("unsubscribe-doctor")
    suspend fun unsubscribeDoctor(
        @Body request: SubscribeDoctorRequest
    ): ApiResponse
    
    @GET("subscriptions/{device_id}")
    suspend fun getSubscriptions(
        @Path("device_id") deviceId: String
    ): Map<String, Any>
}
