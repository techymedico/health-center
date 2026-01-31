package com.iitj.healthcenter.data.remote.dto

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class DoctorScheduleDto(
    val id: Int,
    val date: String,
    val name: String,
    val timing: String,
    val category: String,
    val room: String?
)

@JsonClass(generateAdapter = true)
data class SchedulesResponse(
    val count: Int,
    val data: List<DoctorScheduleDto>
)

@JsonClass(generateAdapter = true)
data class RegisterTokenRequest(
    val device_id: String,
    val fcm_token: String
)

@JsonClass(generateAdapter = true)
data class SubscribeDoctorRequest(
    val device_id: String,
    val doctor_name: String
)

@JsonClass(generateAdapter = true)
data class ApiResponse(
    val status: String,
    val message: String
)
